"""
VAYU X - Logging and Base Infrastructure
Production-grade logging and base classes for all agents
"""

import logging
import logging.handlers
import time
import json
import threading
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum
import traceback
import sys

from config import LOG_LEVEL, DEBUG_MODE, ROBOT, ENVIRONMENT

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

class LogLevel(Enum):
    """Log levels"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

class VAYULogger:
    """Production-grade logger for VAYU X system"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for logger"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(VAYULogger, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize logger (called once due to singleton)"""
        if self._initialized:
            return
        
        self._initialized = True
        self.logger = logging.getLogger("VAYU_X")
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Prevent duplicate handlers
        self.logger.handlers = []
        
        # Console Handler (INFO and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File Handler (DEBUG and above)
        log_file = f"logs/vayu_{ROBOT.robot_id}.log"
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self.logger.warning(f"Could not create file handler: {e}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get logger instance for specific module"""
        return logging.getLogger(f"VAYU_X.{name}")

# Global logger instance
_logger_instance = VAYULogger()

def get_logger(name: str) -> logging.Logger:
    """Get logger for module"""
    return _logger_instance.get_logger(name)

# ============================================================================
# TELEMETRY & EVENT TRACKING
# ============================================================================

class EventType(Enum):
    """System event types for tracking"""
    AGENT_STARTUP = "agent_startup"
    AGENT_SHUTDOWN = "agent_shutdown"
    SENSOR_READ = "sensor_read"
    DECISION_MADE = "decision_made"
    ACTION_EXECUTED = "action_executed"
    ERROR_DETECTED = "error_detected"
    SAFETY_TRIGGER = "safety_trigger"
    COMM_SENT = "comm_sent"
    COMM_RECEIVED = "comm_received"
    STATE_CHANGE = "state_change"
    PERFORMANCE_METRIC = "performance_metric"

class TelemetryEvent:
    """Structured telemetry event"""
    
    def __init__(
        self,
        event_type: EventType,
        agent_id: str,
        data: Dict[str, Any],
        timestamp: Optional[float] = None
    ):
        self.event_type = event_type
        self.agent_id = agent_id
        self.data = data
        self.timestamp = timestamp or time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "type": self.event_type.value,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp,
            "data": self.data
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())

class TelemetryBuffer:
    """Thread-safe telemetry event buffer"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.events = []
        self.lock = threading.Lock()
    
    def add_event(self, event: TelemetryEvent) -> None:
        """Add event to buffer"""
        with self.lock:
            self.events.append(event)
            if len(self.events) > self.max_size:
                self.events.pop(0)
    
    def get_events(self, since_timestamp: Optional[float] = None) -> list:
        """Get events, optionally filtered by timestamp"""
        with self.lock:
            if since_timestamp:
                return [e for e in self.events if e.timestamp >= since_timestamp]
            return self.events.copy()
    
    def clear(self) -> None:
        """Clear all events"""
        with self.lock:
            self.events.clear()

# Global telemetry buffer
_telemetry_buffer = TelemetryBuffer()

def log_event(event: TelemetryEvent) -> None:
    """Log telemetry event"""
    _telemetry_buffer.add_event(event)

def get_telemetry(since_timestamp: Optional[float] = None) -> list:
    """Get telemetry events"""
    return _telemetry_buffer.get_events(since_timestamp)

# ============================================================================
# BASE AGENT CLASS
# ============================================================================

class Agent:
    """Base class for all agents in VAYU X system"""
    
    def __init__(self, agent_id: str, agent_type: str):
        """
        Initialize agent
        
        Args:
            agent_id: Unique identifier for this agent instance
            agent_type: Type of agent (vision, voice, motion, safety, mission)
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.logger = get_logger(agent_id)
        self.is_running = False
        self.is_healthy = True
        self.error_count = 0
        self.max_errors_before_shutdown = 10
        self.startup_time = None
        self.last_heartbeat = time.time()
        self.lock = threading.Lock()
        
        self.logger.info(f"Agent {agent_id} initialized (type={agent_type})")
    
    def startup(self) -> bool:
        """
        Startup sequence for agent
        Override in subclasses for specific initialization
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.lock:
                self.is_running = True
                self.startup_time = time.time()
                self.is_healthy = True
                self.error_count = 0
            
            self.logger.info(f"Agent {self.agent_id} started")
            log_event(TelemetryEvent(
                EventType.AGENT_STARTUP,
                self.agent_id,
                {"agent_type": self.agent_type}
            ))
            return True
        
        except Exception as e:
            self.logger.error(f"Startup failed: {e}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def shutdown(self) -> bool:
        """
        Shutdown sequence for agent
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.lock:
                self.is_running = False
            
            self.logger.info(f"Agent {self.agent_id} shutdown")
            log_event(TelemetryEvent(
                EventType.AGENT_SHUTDOWN,
                self.agent_id,
                {"uptime_seconds": time.time() - self.startup_time}
            ))
            return True
        
        except Exception as e:
            self.logger.error(f"Shutdown failed: {e}")
            return False
    
    def process(self) -> bool:
        """
        Main processing loop - override in subclasses
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.last_heartbeat = time.time()
            return True
        
        except Exception as e:
            self.log_error(f"Process error: {e}")
            return False
    
    def log_error(self, error_msg: str) -> None:
        """Log error and track for health monitoring"""
        with self.lock:
            self.error_count += 1
            self.is_healthy = self.error_count < self.max_errors_before_shutdown
        
        self.logger.error(f"{error_msg} (count={self.error_count})")
        log_event(TelemetryEvent(
            EventType.ERROR_DETECTED,
            self.agent_id,
            {
                "error_message": error_msg,
                "error_count": self.error_count,
                "is_healthy": self.is_healthy
            }
        ))
        
        if not self.is_healthy:
            self.logger.critical(f"Agent {self.agent_id} unhealthy, shutdown recommended")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        with self.lock:
            return {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "is_running": self.is_running,
                "is_healthy": self.is_healthy,
                "error_count": self.error_count,
                "uptime_seconds": time.time() - self.startup_time if self.startup_time else 0,
                "last_heartbeat": self.last_heartbeat,
                "timestamp": time.time()
            }
    
    def __repr__(self) -> str:
        return f"<Agent {self.agent_id} ({self.agent_type})>"

# ============================================================================
# ERROR HANDLING
# ============================================================================

class VAYUException(Exception):
    """Base exception for VAYU X system"""
    pass

class AgentException(VAYUException):
    """Agent-related exception"""
    pass

class CommunicationException(VAYUException):
    """Communication-related exception"""
    pass

class SensorException(VAYUException):
    """Sensor-related exception"""
    pass

class SafetyException(VAYUException):
    """Safety-critical exception"""
    pass

# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

class PerformanceMonitor:
    """Monitor performance metrics of agents"""
    
    def __init__(self):
        self.metrics = {}
        self.lock = threading.Lock()
    
    def record_metric(self, agent_id: str, metric_name: str, value: float) -> None:
        """Record performance metric"""
        with self.lock:
            key = f"{agent_id}_{metric_name}"
            if key not in self.metrics:
                self.metrics[key] = []
            
            self.metrics[key].append({
                "value": value,
                "timestamp": time.time()
            })
            
            # Keep only last 1000 records
            if len(self.metrics[key]) > 1000:
                self.metrics[key].pop(0)
    
    def get_metric_stats(self, agent_id: str, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric"""
        with self.lock:
            key = f"{agent_id}_{metric_name}"
            if key not in self.metrics or not self.metrics[key]:
                return {}
            
            values = [m["value"] for m in self.metrics[key]]
            
            return {
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "count": len(values),
                "latest": values[-1]
            }

# Global performance monitor
_perf_monitor = PerformanceMonitor()

def record_metric(agent_id: str, metric_name: str, value: float) -> None:
    """Record performance metric"""
    _perf_monitor.record_metric(agent_id, metric_name, value)

def get_metric_stats(agent_id: str, metric_name: str) -> Dict[str, float]:
    """Get metric statistics"""
    return _perf_monitor.get_metric_stats(agent_id, metric_name)

# ============================================================================
# INITIALIZATION
# ============================================================================

if __name__ == "__main__":
    logger = get_logger("test")
    logger.info("VAYU X Logging initialized")
    
    event = TelemetryEvent(
        EventType.AGENT_STARTUP,
        "test_agent",
        {"status": "ok"}
    )
    log_event(event)
    print("✓ Base infrastructure initialized")
