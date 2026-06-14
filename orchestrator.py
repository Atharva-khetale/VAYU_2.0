"""
VAYU X - Multi-Agent Orchestration System
Coordinates Vision, Voice, Motion, Safety, and Mission Planner agents
"""

import threading
import time
import json
import queue
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from base import (
    Agent, get_logger, log_event, EventType, TelemetryEvent,
    record_metric, AgentException
)
from config import (
    ROBOT, NetworkConfig, AgentConfig, PerformanceConfig,
    DEPLOYMENT_MODE, DEPLOYMENT_FEATURES
)
from edge_ai import EdgeAIAgent

# ============================================================================
# MESSAGE TYPES & COMMUNICATION
# ============================================================================

class MessageType(Enum):
    """Inter-agent message types"""
    SENSOR_DATA = "sensor_data"
    DECISION = "decision"
    ACTION = "action"
    STATUS = "status"
    ERROR = "error"
    TELEMETRY = "telemetry"
    COORDINATION = "coordination"

@dataclass
class Message:
    """Inter-agent message"""
    message_type: MessageType
    sender_id: str
    receiver_id: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    priority: int = 0  # 0=normal, 1=high, 2=critical
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.message_type.value,
            "sender": self.sender_id,
            "receiver": self.receiver_id,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "priority": self.priority
        }

class MessageBus:
    """Central message bus for inter-agent communication"""
    
    def __init__(self, max_size: int = 1000):
        self.queue = queue.PriorityQueue(maxsize=max_size)
        self.subscribers = defaultdict(list)
        self.lock = threading.Lock()
        self.logger = get_logger("MessageBus")
    
    def publish(self, message: Message) -> bool:
        """
        Publish message to bus
        
        Returns:
            True if successful, False if queue is full
        """
        try:
            # Use negative priority for priority queue (higher priority = lower value)
            self.queue.put((-message.priority, time.time(), message), block=False)
            return True
        except queue.Full:
            self.logger.warning("Message bus queue full")
            return False
    
    def subscribe(self, message_type: MessageType, receiver_id: str, callback: Callable) -> None:
        """Subscribe to message type"""
        with self.lock:
            key = f"{message_type.value}:{receiver_id}"
            self.subscribers[key].append(callback)
    
    def get_messages(self, receiver_id: str, timeout: float = 0.1) -> List[Message]:
        """Get messages for specific receiver"""
        messages = []
        try:
            while True:
                _, _, msg = self.queue.get(timeout=timeout)
                if msg.receiver_id == receiver_id or msg.receiver_id == "broadcast":
                    messages.append(msg)
        except queue.Empty:
            pass
        
        return messages
    
    def clear(self) -> None:
        """Clear all messages from bus"""
        try:
            while True:
                self.queue.get_nowait()
        except queue.Empty:
            pass

# ============================================================================
# AGENT STATES & CONTEXT
# ============================================================================

class RobotState(Enum):
    """Overall robot operational state"""
    IDLE = "idle"
    AUTONOMOUS = "autonomous"
    GUIDED = "guided"
    EMERGENCY_STOP = "emergency_stop"
    SHUTDOWN = "shutdown"

@dataclass
class RobotContext:
    """Shared context for all agents"""
    robot_id: str
    state: RobotState = RobotState.IDLE
    timestamp: float = field(default_factory=time.time)
    battery_voltage: float = 12.0
    battery_percentage: int = 100
    temperature_celsius: float = 25.0
    is_healthy: bool = True
    active_mission: Optional[str] = None
    detected_persons: List[Dict] = field(default_factory=list)
    detected_obstacles: List[Dict] = field(default_factory=list)
    current_location: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "heading": 0.0})
    active_keywords: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "robot_id": self.robot_id,
            "state": self.state.value,
            "timestamp": self.timestamp,
            "battery_voltage": self.battery_voltage,
            "battery_percentage": self.battery_percentage,
            "temperature_celsius": self.temperature_celsius,
            "is_healthy": self.is_healthy,
            "active_mission": self.active_mission,
            "detected_persons": self.detected_persons,
            "detected_obstacles": self.detected_obstacles,
            "current_location": self.current_location,
            "active_keywords": self.active_keywords
        }

# ============================================================================
# COORDINATION LOGIC
# ============================================================================

class DecisionEngine:
    """Central decision-making logic for mission planner"""
    
    def __init__(self, context: RobotContext):
        self.context = context
        self.logger = get_logger("DecisionEngine")
        self.mission_queue = []
        self.current_mission = None
    
    def evaluate_state(self) -> None:
        """Evaluate current state and update context"""
        try:
            # Safety checks
            if self.context.battery_percentage < 10:
                self.context.state = RobotState.EMERGENCY_STOP
                self.logger.warning("Critical battery level")
                return
            
            if self.context.temperature_celsius > 85:
                self.context.state = RobotState.EMERGENCY_STOP
                self.logger.warning("Critical temperature")
                return
            
            # Normal operation
            if len(self.context.detected_obstacles) > 0:
                self.logger.debug("Obstacles detected, adjusting course")
            
            self.context.timestamp = time.time()
        
        except Exception as e:
            self.logger.error(f"State evaluation error: {e}")
    
    def make_decision(self) -> Optional[Message]:
        """
        Make autonomous decision based on context
        
        Returns:
            Action message for motion agent, or None
        """
        try:
            if self.context.state == RobotState.EMERGENCY_STOP:
                return Message(
                    MessageType.ACTION,
                    "mission_planner",
                    "motion_agent",
                    {"action": "stop", "reason": "emergency"}
                )
            
            if self.context.state == RobotState.IDLE:
                # Check for new missions
                if self.mission_queue:
                    self.current_mission = self.mission_queue.pop(0)
                    self.context.state = RobotState.AUTONOMOUS
                    self.logger.info(f"Started mission: {self.current_mission}")
                    
                    return Message(
                        MessageType.ACTION,
                        "mission_planner",
                        "motion_agent",
                        {"action": "navigate", "mission": self.current_mission}
                    )
            
            return None
        
        except Exception as e:
            self.logger.error(f"Decision making error: {e}")
            return None
    
    def queue_mission(self, mission: str) -> None:
        """Queue a new mission"""
        self.mission_queue.append(mission)
        self.logger.info(f"Mission queued: {mission}")

# ============================================================================
# AGENT REGISTRY & MANAGER
# ============================================================================

class AgentManager:
    """Manages all agents in the system"""
    
    def __init__(self):
        self.logger = get_logger("AgentManager")
        self.agents: Dict[str, Agent] = {}
        self.agent_threads: Dict[str, threading.Thread] = {}
        self.message_bus = MessageBus()
        self.context = RobotContext(robot_id=ROBOT.robot_id)
        self.decision_engine = DecisionEngine(self.context)
        self.lock = threading.Lock()
        self.running = False
        
        # Create edge AI agent (always available)
        self.edge_ai = EdgeAIAgent()
    
    def register_agent(self, agent: Agent) -> bool:
        """
        Register an agent with the manager
        
        Args:
            agent: Agent instance to register
            
        Returns:
            True if successful
        """
        try:
            with self.lock:
                if agent.agent_id in self.agents:
                    self.logger.warning(f"Agent already registered: {agent.agent_id}")
                    return False
                
                self.agents[agent.agent_id] = agent
                self.logger.info(f"Agent registered: {agent.agent_id} ({agent.agent_type})")
                return True
        
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return False
    
    def startup_all_agents(self) -> bool:
        """Start all registered agents"""
        try:
            with self.lock:
                # Start edge AI first (critical for all operations)
                if not self.edge_ai.startup():
                    self.logger.error("EdgeAI startup failed")
                    return False
                
                # Start all other agents
                for agent_id, agent in self.agents.items():
                    if not agent.startup():
                        self.logger.error(f"Agent startup failed: {agent_id}")
                        return False
                    
                    # Create processing thread for agent
                    thread = threading.Thread(
                        target=self._agent_loop,
                        args=(agent,),
                        daemon=True,
                        name=f"agent_{agent_id}"
                    )
                    thread.start()
                    self.agent_threads[agent_id] = thread
            
            self.running = True
            self.logger.info(f"All agents started ({len(self.agents)} agents)")
            return True
        
        except Exception as e:
            self.logger.error(f"Startup error: {e}")
            return False
    
    def shutdown_all_agents(self) -> bool:
        """Shutdown all agents gracefully"""
        try:
            with self.lock:
                self.running = False
                
                for agent_id, agent in self.agents.items():
                    if not agent.shutdown():
                        self.logger.warning(f"Agent shutdown incomplete: {agent_id}")
                
                # Shutdown edge AI
                self.edge_ai.shutdown()
            
            # Wait for threads to finish
            for agent_id, thread in self.agent_threads.items():
                thread.join(timeout=5.0)
            
            self.logger.info("All agents shutdown")
            return True
        
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
            return False
    
    def _agent_loop(self, agent: Agent) -> None:
        """Main processing loop for agent"""
        while self.running and agent.is_running:
            try:
                # Process agent
                if not agent.process():
                    self.logger.warning(f"Agent process failed: {agent.agent_id}")
                
                # Get messages for this agent
                messages = self.message_bus.get_messages(agent.agent_id)
                for msg in messages:
                    # Route to agent (override in subclass to handle)
                    pass
                
                # Small sleep to prevent CPU spinning
                time.sleep(PerformanceConfig.SENSOR_POLL_INTERVAL_MS / 1000.0)
            
            except Exception as e:
                agent.log_error(f"Loop error: {e}")
                time.sleep(0.1)
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, Agent]:
        """Get all registered agents"""
        return self.agents.copy()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        health = {
            "timestamp": time.time(),
            "robot_id": ROBOT.robot_id,
            "deployment_mode": DEPLOYMENT_MODE,
            "agent_count": len(self.agents),
            "agents": {},
            "context": self.context.to_dict(),
            "edge_ai": self.edge_ai.get_status()
        }
        
        for agent_id, agent in self.agents.items():
            health["agents"][agent_id] = agent.get_status()
        
        return health
    
    def broadcast_message(self, message: Message) -> None:
        """Broadcast message to all agents"""
        message.receiver_id = "broadcast"
        self.message_bus.publish(message)
    
    def send_message(self, message: Message) -> bool:
        """Send directed message between agents"""
        return self.message_bus.publish(message)

# ============================================================================
# SYSTEM ORCHESTRATOR
# ============================================================================

class VAYUOrchestrator:
    """Main orchestrator for VAYU X system"""
    
    def __init__(self):
        self.logger = get_logger("Orchestrator")
        self.agent_manager = AgentManager()
        self.is_running = False
        self.heartbeat_thread = None
    
    def initialize(self) -> bool:
        """Initialize VAYU X system"""
        try:
            self.logger.info("Initializing VAYU X system")
            
            # Start all agents
            if not self.agent_manager.startup_all_agents():
                self.logger.error("Agent startup failed")
                return False
            
            self.is_running = True
            
            # Start heartbeat monitor
            self.heartbeat_thread = threading.Thread(
                target=self._heartbeat_loop,
                daemon=True,
                name="heartbeat"
            )
            self.heartbeat_thread.start()
            
            self.logger.info("✓ VAYU X system initialized")
            return True
        
        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown VAYU X system"""
        try:
            self.is_running = False
            self.agent_manager.shutdown_all_agents()
            self.logger.info("✓ VAYU X system shutdown")
            return True
        
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
            return False
    
    def _heartbeat_loop(self) -> None:
        """Monitor system health"""
        while self.is_running:
            try:
                health = self.agent_manager.get_system_health()
                
                # Log health metrics
                unhealthy_agents = [
                    a for a, status in health["agents"].items()
                    if not status["is_healthy"]
                ]
                
                if unhealthy_agents:
                    self.logger.warning(f"Unhealthy agents: {unhealthy_agents}")
                
                # Record system metric
                record_metric(
                    "system",
                    "agent_health_count",
                    len([a for a, s in health["agents"].items() if s["is_healthy"]])
                )
                
                time.sleep(PerformanceConfig.HEARTBEAT_INTERVAL_S)
            
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                time.sleep(1)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return self.agent_manager.get_system_health()

# ============================================================================
# INITIALIZATION
# ============================================================================

if __name__ == "__main__":
    orchestrator = VAYUOrchestrator()
    if orchestrator.initialize():
        print("✓ VAYU X Orchestrator ready")
        print(f"  Status: {orchestrator.get_status()}")
    else:
        print("✗ VAYU X initialization failed")
