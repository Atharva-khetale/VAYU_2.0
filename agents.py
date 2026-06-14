"""
VAYU X - Individual Agent Implementations
Vision, Voice, Motion, Safety, and Mission Planner Agents
Complete with simulation mode for testing
"""

import time
import numpy as np
import threading
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import random

from base import Agent, get_logger, log_event, EventType, TelemetryEvent, record_metric
from config import (
    AgentConfig, SensorConfig, SafetyThresholds, PinConfig,
    DEPLOYMENT_MODE, DEPLOYMENT_FEATURES, ENVIRONMENT
)
from edge_ai import EdgeAIAgent, EdgeAIModelManager

# ============================================================================
# VISION AGENT
# ============================================================================

class VisionAgent(Agent):
    """
    Vision Agent - Processes camera input and detects persons/objects
    Hardware: ESP32-CAM (OV2640)
    """
    
    def __init__(self, agent_id: str = "vision_001"):
        super().__init__(agent_id, "vision")
        self.edge_ai = EdgeAIModelManager()
        self.camera_active = False
        self.frame_count = 0
        self.detections_cache = []
        self.simulation_mode = ENVIRONMENT == "development"
    
    def startup(self) -> bool:
        """Initialize vision agent"""
        if not super().startup():
            return False
        
        try:
            # Load vision models
            if not self.edge_ai.load_model("person_detection"):
                self.logger.warning("Person detection model failed to load")
            
            self.camera_active = True
            self.logger.info("Vision agent ready")
            return True
        
        except Exception as e:
            self.log_error(f"Vision startup failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown vision agent"""
        self.camera_active = False
        return super().shutdown()
    
    def process(self) -> bool:
        """Process camera frames"""
        if not super().process():
            return False
        
        try:
            if not self.camera_active:
                return False
            
            start_time = time.time()
            
            # Simulate camera frame capture
            if self.simulation_mode:
                frame = self._get_simulated_frame()
            else:
                frame = self._get_camera_frame()
            
            if frame is None:
                self.logger.warning("No frame available")
                return False
            
            # Run person detection
            detections = self.edge_ai.detect_persons(frame)
            self.detections_cache = [d.to_dict() for d in detections]
            self.frame_count += 1
            
            # Record metrics
            process_time = (time.time() - start_time) * 1000
            record_metric(self.agent_id, "frame_process_time_ms", process_time)
            record_metric(self.agent_id, "detections_count", len(detections))
            
            if len(detections) > 0:
                self.logger.debug(f"Detected {len(detections)} persons")
            
            return True
        
        except Exception as e:
            self.log_error(f"Vision process error: {e}")
            return False
    
    def _get_simulated_frame(self) -> np.ndarray:
        """Generate simulated camera frame"""
        height, width = 240, 320
        frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        
        # Add some structure
        if random.random() > 0.5:
            # Add a rectangle to simulate object
            x, y, w, h = 50, 40, 100, 150
            frame[y:y+h, x:x+w] = np.random.randint(100, 200, (h, w, 3))
        
        return frame
    
    def _get_camera_frame(self) -> Optional[np.ndarray]:
        """Get real camera frame (would connect to ESP32-CAM)"""
        try:
            # In real implementation, would read from ESP32-CAM
            # For now, return None (hardware not available)
            return None
        except Exception as e:
            self.logger.error(f"Camera read error: {e}")
            return None
    
    def get_detections(self) -> List[Dict]:
        """Get last detection results"""
        return self.detections_cache.copy()

# ============================================================================
# VOICE AGENT
# ============================================================================

class VoiceAgent(Agent):
    """
    Voice Agent - Handles voice recognition and text-to-speech
    Hardware: ESP32-S3 with INMP441 microphone and MAX98357A speaker
    """
    
    def __init__(self, agent_id: str = "voice_001"):
        super().__init__(agent_id, "voice")
        self.is_listening = False
        self.last_keyword = None
        self.speech_queue = []
        self.simulation_mode = ENVIRONMENT == "development"
    
    def startup(self) -> bool:
        """Initialize voice agent"""
        if not super().startup():
            return False
        
        try:
            self.is_listening = True
            self.logger.info("Voice agent ready")
            return True
        
        except Exception as e:
            self.log_error(f"Voice startup failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown voice agent"""
        self.is_listening = False
        return super().shutdown()
    
    def process(self) -> bool:
        """Process voice input/output"""
        if not super().process():
            return False
        
        try:
            if self.simulation_mode:
                self._simulate_voice_input()
            else:
                self._process_voice_input()
            
            # Process speech queue
            self._process_speech_output()
            
            return True
        
        except Exception as e:
            self.log_error(f"Voice process error: {e}")
            return False
    
    def _simulate_voice_input(self) -> None:
        """Simulate voice input for testing"""
        if random.random() > 0.95:  # 5% chance per cycle
            keywords = ["follow", "stop", "next", "exit", "help", "repeat"]
            self.last_keyword = random.choice(keywords)
            self.logger.debug(f"Simulated keyword detected: {self.last_keyword}")
            
            log_event(TelemetryEvent(
                EventType.SENSOR_READ,
                self.agent_id,
                {"keyword": self.last_keyword, "confidence": 0.85}
            ))
    
    def _process_voice_input(self) -> None:
        """Process real voice input from microphone"""
        # Would connect to INMP441 microphone
        pass
    
    def _process_speech_output(self) -> None:
        """Process speech output queue"""
        while self.speech_queue:
            text = self.speech_queue.pop(0)
            self.logger.info(f"Speaking: {text}")
            
            log_event(TelemetryEvent(
                EventType.ACTION_EXECUTED,
                self.agent_id,
                {"action": "speak", "text": text}
            ))
    
    def speak(self, text: str) -> None:
        """Queue text for speech output"""
        self.speech_queue.append(text)
    
    def get_last_keyword(self) -> Optional[str]:
        """Get last detected keyword"""
        return self.last_keyword

# ============================================================================
# MOTION AGENT
# ============================================================================

@dataclass
class MotionCommand:
    """Motion command for robot"""
    action: str  # forward, backward, left, right, stop
    speed: float  # 0-1
    duration: float  # seconds

class MotionAgent(Agent):
    """
    Motion Agent - Controls robot movement
    Hardware: ESP32-S3 with TB6612FNG motor driver
    """
    
    def __init__(self, agent_id: str = "motion_001"):
        super().__init__(agent_id, "motion")
        self.current_speed = 0.0
        self.current_heading = 0.0  # degrees
        self.position_x = 0.0
        self.position_y = 0.0
        self.is_moving = False
        self.command_queue = []
        self.simulation_mode = ENVIRONMENT == "development"
    
    def startup(self) -> bool:
        """Initialize motion agent"""
        if not super().startup():
            return False
        
        try:
            self.logger.info("Motion agent ready")
            return True
        
        except Exception as e:
            self.log_error(f"Motion startup failed: {e}")
            return False
    
    def process(self) -> bool:
        """Process motion commands"""
        if not super().process():
            return False
        
        try:
            # Execute queued commands
            if self.command_queue:
                cmd = self.command_queue.pop(0)
                self._execute_command(cmd)
            else:
                # Simulation: random walk
                if self.simulation_mode and random.random() > 0.9:
                    self._simulate_movement()
            
            record_metric(self.agent_id, "current_speed", self.current_speed)
            record_metric(self.agent_id, "position_x", self.position_x)
            record_metric(self.agent_id, "position_y", self.position_y)
            
            return True
        
        except Exception as e:
            self.log_error(f"Motion process error: {e}")
            return False
    
    def queue_command(self, command: MotionCommand) -> None:
        """Queue a motion command"""
        self.command_queue.append(command)
        self.logger.debug(f"Command queued: {command.action}")
    
    def _execute_command(self, cmd: MotionCommand) -> None:
        """Execute a motion command"""
        if cmd.action == "forward":
            self.current_speed = cmd.speed
            self.position_y += cmd.speed * 0.1
        elif cmd.action == "backward":
            self.current_speed = -cmd.speed
            self.position_y -= cmd.speed * 0.1
        elif cmd.action == "left":
            self.current_heading -= 10
        elif cmd.action == "right":
            self.current_heading += 10
        elif cmd.action == "stop":
            self.current_speed = 0.0
        
        self.logger.debug(f"Executed: {cmd.action} (speed={self.current_speed})")
        
        log_event(TelemetryEvent(
            EventType.ACTION_EXECUTED,
            self.agent_id,
            {
                "action": cmd.action,
                "speed": self.current_speed,
                "position": {"x": self.position_x, "y": self.position_y}
            }
        ))
    
    def _simulate_movement(self) -> None:
        """Simulate robot movement"""
        action = random.choice(["forward", "left", "right"])
        cmd = MotionCommand(action=action, speed=0.5, duration=1.0)
        self._execute_command(cmd)
    
    def get_position(self) -> Dict[str, float]:
        """Get current position"""
        return {
            "x": self.position_x,
            "y": self.position_y,
            "heading": self.current_heading,
            "speed": self.current_speed
        }

# ============================================================================
# SAFETY AGENT
# ============================================================================

class SafetyAgent(Agent):
    """
    Safety Agent - Monitors safety-critical parameters
    Handles obstacle detection, battery monitoring, emergency stop
    """
    
    def __init__(self, agent_id: str = "safety_001"):
        super().__init__(agent_id, "safety")
        self.obstacle_detected = False
        self.battery_voltage = 12.0
        self.temperature_celsius = 25.0
        self.emergency_stop_active = False
        self.sensor_readings = {}
    
    def startup(self) -> bool:
        """Initialize safety agent"""
        if not super().startup():
            return False
        
        try:
            self.logger.info("Safety agent ready")
            return True
        
        except Exception as e:
            self.log_error(f"Safety startup failed: {e}")
            return False
    
    def process(self) -> bool:
        """Monitor safety parameters"""
        if not super().process():
            return False
        
        try:
            # Simulate sensor readings
            self._read_sensors()
            
            # Check safety thresholds
            self._check_thresholds()
            
            # Record metrics
            record_metric(self.agent_id, "battery_voltage", self.battery_voltage)
            record_metric(self.agent_id, "temperature_celsius", self.temperature_celsius)
            
            return True
        
        except Exception as e:
            self.log_error(f"Safety process error: {e}")
            return False
    
    def _read_sensors(self) -> None:
        """Read sensor values"""
        if ENVIRONMENT == "development":
            # Simulate sensor readings with small variations
            self.battery_voltage = max(8.0, self.battery_voltage - 0.001 + random.gauss(0, 0.01))
            self.temperature_celsius = 25.0 + random.gauss(0, 2)
            self.obstacle_detected = random.random() > 0.95
            
            self.sensor_readings = {
                "battery_voltage": self.battery_voltage,
                "temperature_celsius": self.temperature_celsius,
                "obstacle_detected": self.obstacle_detected,
                "tilt_degrees": random.gauss(0, 5)
            }
    
    def _check_thresholds(self) -> None:
        """Check safety thresholds"""
        # Battery critical
        if self.battery_voltage < SafetyThresholds.BATTERY_VOLTAGE_CRITICAL:
            self.emergency_stop_active = True
            self.logger.critical("Critical battery level - emergency stop activated")
            log_event(TelemetryEvent(
                EventType.SAFETY_TRIGGER,
                self.agent_id,
                {"reason": "battery_critical", "voltage": self.battery_voltage}
            ))
        
        # Temperature critical
        if self.temperature_celsius > SafetyThresholds.THERMAL_CRITICAL:
            self.emergency_stop_active = True
            self.logger.critical("Critical temperature - emergency stop activated")
            log_event(TelemetryEvent(
                EventType.SAFETY_TRIGGER,
                self.agent_id,
                {"reason": "thermal_critical", "temperature": self.temperature_celsius}
            ))
        
        # Obstacle detection
        if self.obstacle_detected:
            self.logger.warning("Obstacle detected")
            log_event(TelemetryEvent(
                EventType.SENSOR_READ,
                self.agent_id,
                {"obstacle_detected": True}
            ))
    
    def is_safe(self) -> bool:
        """Check if robot is safe to operate"""
        return (
            not self.emergency_stop_active and
            self.battery_voltage >= SafetyThresholds.BATTERY_VOLTAGE_MIN and
            self.temperature_celsius < SafetyThresholds.THERMAL_CRITICAL
        )
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get safety status"""
        return {
            "is_safe": self.is_safe(),
            "emergency_stop_active": self.emergency_stop_active,
            "obstacle_detected": self.obstacle_detected,
            "battery_voltage": self.battery_voltage,
            "temperature_celsius": self.temperature_celsius,
            "sensor_readings": self.sensor_readings
        }

# ============================================================================
# MISSION PLANNER AGENT
# ============================================================================

@dataclass
class Mission:
    """Robot mission definition"""
    mission_id: str
    name: str
    description: str
    waypoints: List[Dict[str, float]]  # List of {x, y, heading}
    deployment_mode: str
    priority: int = 0

class MissionPlannerAgent(Agent):
    """
    Mission Planner Agent - High-level decision making and mission planning
    Coordinates other agents to accomplish missions
    """
    
    def __init__(self, agent_id: str = "mission_001"):
        super().__init__(agent_id, "mission_planner")
        self.current_mission: Optional[Mission] = None
        self.mission_queue: List[Mission] = []
        self.completed_missions = []
        self.waypoint_index = 0
    
    def startup(self) -> bool:
        """Initialize mission planner"""
        if not super().startup():
            return False
        
        try:
            self._create_default_missions()
            self.logger.info("Mission planner ready")
            return True
        
        except Exception as e:
            self.log_error(f"Mission planner startup failed: {e}")
            return False
    
    def process(self) -> bool:
        """Process mission planning"""
        if not super().process():
            return False
        
        try:
            # If no active mission, get next from queue
            if not self.current_mission and self.mission_queue:
                self.current_mission = self.mission_queue.pop(0)
                self.waypoint_index = 0
                self.logger.info(f"Started mission: {self.current_mission.name}")
                
                log_event(TelemetryEvent(
                    EventType.DECISION_MADE,
                    self.agent_id,
                    {"decision": "mission_start", "mission_id": self.current_mission.mission_id}
                ))
            
            # Execute current mission
            if self.current_mission:
                self._execute_mission_step()
            
            return True
        
        except Exception as e:
            self.log_error(f"Mission planner process error: {e}")
            return False
    
    def _execute_mission_step(self) -> None:
        """Execute next step in current mission"""
        if self.waypoint_index < len(self.current_mission.waypoints):
            waypoint = self.current_mission.waypoints[self.waypoint_index]
            self.logger.debug(f"Moving to waypoint {self.waypoint_index}: {waypoint}")
            self.waypoint_index += 1
        else:
            # Mission complete
            self.completed_missions.append(self.current_mission)
            self.logger.info(f"Mission completed: {self.current_mission.name}")
            
            log_event(TelemetryEvent(
                EventType.DECISION_MADE,
                self.agent_id,
                {"decision": "mission_complete", "mission_id": self.current_mission.mission_id}
            ))
            
            self.current_mission = None
    
    def _create_default_missions(self) -> None:
        """Create default missions based on deployment mode"""
        if DEPLOYMENT_MODE == "museum":
            missions = [
                Mission(
                    mission_id="museum_001",
                    name="Main Exhibition Tour",
                    description="Guide visitors through main exhibition",
                    waypoints=[
                        {"x": 0, "y": 0, "heading": 0},
                        {"x": 5, "y": 0, "heading": 0},
                        {"x": 5, "y": 5, "heading": 90},
                        {"x": 0, "y": 5, "heading": 180},
                    ],
                    deployment_mode="museum"
                )
            ]
        elif DEPLOYMENT_MODE == "home":
            missions = [
                Mission(
                    mission_id="home_001",
                    name="Home Patrol",
                    description="Patrol home for security",
                    waypoints=[
                        {"x": 0, "y": 0, "heading": 0},
                        {"x": 3, "y": 0, "heading": 0},
                        {"x": 3, "y": 3, "heading": 90},
                    ],
                    deployment_mode="home"
                )
            ]
        else:
            missions = [
                Mission(
                    mission_id="default_001",
                    name="Default Patrol",
                    description="Default patrol route",
                    waypoints=[
                        {"x": 0, "y": 0, "heading": 0},
                        {"x": 2, "y": 0, "heading": 0},
                    ],
                    deployment_mode=DEPLOYMENT_MODE
                )
            ]
        
        self.mission_queue.extend(missions)
    
    def queue_mission(self, mission: Mission) -> None:
        """Queue a new mission"""
        self.mission_queue.append(mission)
        self.logger.info(f"Mission queued: {mission.name}")
    
    def get_mission_status(self) -> Dict[str, Any]:
        """Get current mission status"""
        return {
            "current_mission": self.current_mission.mission_id if self.current_mission else None,
            "waypoint_index": self.waypoint_index,
            "queued_missions": len(self.mission_queue),
            "completed_missions": len(self.completed_missions)
        }

# ============================================================================
# INITIALIZATION
# ============================================================================

if __name__ == "__main__":
    vision = VisionAgent()
    voice = VoiceAgent()
    motion = MotionAgent()
    safety = SafetyAgent()
    mission = MissionPlannerAgent()
    
    print("✓ All agents initialized")
    print(f"  Vision: {vision.agent_id}")
    print(f"  Voice: {voice.agent_id}")
    print(f"  Motion: {motion.agent_id}")
    print(f"  Safety: {safety.agent_id}")
    print(f"  Mission Planner: {mission.agent_id}")
