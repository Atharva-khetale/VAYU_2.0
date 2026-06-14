"""
VAYU X - FIXED Configuration
All issues resolved for proper simulation
"""

import os
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# DEPLOYMENT & ENVIRONMENT
# ============================================================================

DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "museum")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEBUG_MODE = ENVIRONMENT == "development"

# ============================================================================
# ROBOT CONFIGURATION
# ============================================================================

@dataclass
class RobotConfig:
    robot_id: str = os.getenv("ROBOT_ID", "vayu_001")
    robot_name: str = "VAYU X"
    firmware_version: str = "2.0.0"
    hardware_version: str = "1.0"
    location: str = os.getenv("ROBOT_LOCATION", "museum_entrance")

ROBOT = RobotConfig()

# ============================================================================
# ML MODEL CONFIGURATION - FIXED
# ============================================================================

class MLConfig:
    """Machine Learning model configuration"""
    
    # TensorFlow Lite Models (for ESP32)
    TFLITE_MODELS = {
        "person_detection": {
            "model": "models/person_detection.tflite",
            "input_size": (96, 96),
            "threshold": 0.5,
            "max_detections": 10,
        },
        "object_detection": {
            "model": "models/object_detection.tflite",
            "input_size": (224, 224),
            "threshold": 0.5,
            "max_detections": 5,
        },
        "pose_estimation": {
            "model": "models/pose_estimation.tflite",
            "input_size": (192, 192),
            "threshold": 0.5,
        },
        "keyword_detection": {
            "model": "models/keyword_detection.tflite",
            "input_size": (16000,),  # Fixed: Audio sample input
            "sample_rate": 16000,
            "keywords": ["follow", "stop", "next", "exit", "help", "repeat"],
            "threshold": 0.7,
        },
    }
    
    QUANTIZATION = "int8"
    MODEL_INFERENCE_TIMEOUT_MS = 500
    MODEL_INFERENCE_THREADS = 1

# ============================================================================
# AGENT CONFIGURATION
# ============================================================================

class AgentConfig:
    """Configuration for individual agents"""
    
    VISION_AGENT = {
        "enabled": True,
        "hardware": "ESP32-CAM",
        "camera": "OV2640",
        "resolution": (320, 240),
        "fps": 15,
        "buffer_size": 4096,
        "jpeg_quality": 80,
        "timeout": 5.0,
    }
    
    VOICE_AGENT = {
        "enabled": True,
        "hardware": "ESP32-S3",
        "microphone": "INMP441",
        "speaker": "MAX98357A",
        "sample_rate": 16000,
        "channels": 1,
        "bit_depth": 16,
        "buffer_size": 4096,
        "wake_word": "vayu",
        "wake_word_sensitivity": 0.5,
    }
    
    MOTION_AGENT = {
        "enabled": True,
        "hardware": "ESP32-S3",
        "motor_driver": "TB6612FNG",
        "encoders": True,
        "servo_count": 2,
        "max_speed": 255,
        "acceleration": 50,
        "wheel_diameter_mm": 65,
        "wheel_separation_mm": 150,
    }
    
    SAFETY_AGENT = {
        "enabled": True,
        "obstacle_detection": True,
        "ultrasonic_threshold_cm": 20,
        "emergency_stop_enabled": True,
        "battery_min_voltage": 10.0,
        "battery_critical_voltage": 8.0,
        "thermal_threshold_celsius": 80,
        "tilt_threshold_degrees": 45,
    }
    
    MISSION_PLANNER = {
        "enabled": True,
        "decision_interval_ms": 100,
        "max_mission_duration_seconds": 3600,
        "mission_queue_size": 50,
    }

# ============================================================================
# NETWORK CONFIGURATION
# ============================================================================

class NetworkConfig:
    MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
    MQTT_USERNAME = os.getenv("MQTT_USERNAME", "vayu_user")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "vayu_password")
    MQTT_KEEPALIVE = 60

# ============================================================================
# SAFETY THRESHOLDS
# ============================================================================

class SafetyThresholds:
    BATTERY_VOLTAGE_MIN = 10.0
    BATTERY_VOLTAGE_CRITICAL = 8.0
    BATTERY_VOLTAGE_MAX = 16.8
    THERMAL_WARNING = 70.0
    THERMAL_CRITICAL = 85.0
    MAX_LINEAR_VELOCITY = 0.5
    MAX_ANGULAR_VELOCITY = 180.0
    MAX_ACCELERATION = 0.2
    OBSTACLE_DISTANCE_MIN = 0.2
    OBSTACLE_DETECTION_RANGE = 2.0
    MAX_TILT_ANGLE = 45.0
    MAX_ROLL_ANGLE = 45.0

# ============================================================================
# PERFORMANCE CONFIG
# ============================================================================

class PerformanceConfig:
    MAX_THREADS = 4
    THREAD_POOL_SIZE = 2
    MAX_BUFFER_SIZE_MB = 20
    QUEUE_MAX_SIZE = 100
    SENSOR_POLL_INTERVAL_MS = 50
    DECISION_INTERVAL_MS = 100
    TELEMETRY_INTERVAL_S = 5
    HEARTBEAT_INTERVAL_S = 10
    PACKET_MAX_SIZE_BYTES = 1024
    RETRY_MAX_ATTEMPTS = 3
    RETRY_BACKOFF_MS = 1000

# ============================================================================
# DEPLOYMENT MODES
# ============================================================================

DEPLOYMENT_FEATURES = {
    "museum": {
        "navigation_enabled": True,
        "exhibit_narration": True,
        "visitor_interaction": True,
        "child_mode": True,
        "multilingual": True,
        "route_guidance": True,
    },
    "home": {
        "elderly_assistance": True,
        "visitor_detection": True,
        "security_alerts": True,
        "medicine_reminders": True,
        "emergency_response": True,
    },
    "security": {
        "patrol_routes": True,
        "intrusion_detection": True,
        "live_monitoring": True,
        "alert_system": True,
        "motion_tracking": True,
    },
    "warehouse": {
        "inventory_guidance": True,
        "route_optimization": True,
        "fleet_coordination": True,
        "package_detection": True,
        "item_tracking": True,
    }
}

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config() -> Tuple[bool, str]:
    """Validate configuration"""
    if SafetyThresholds.BATTERY_VOLTAGE_CRITICAL >= SafetyThresholds.BATTERY_VOLTAGE_MIN:
        return False, "Critical battery voltage >= min voltage"
    
    if SafetyThresholds.THERMAL_CRITICAL <= SafetyThresholds.THERMAL_WARNING:
        return False, "Thermal critical <= thermal warning"
    
    if SafetyThresholds.MAX_LINEAR_VELOCITY <= 0:
        return False, "Max linear velocity must be positive"
    
    return True, "Configuration valid"

if __name__ == "__main__":
    is_valid, msg = validate_config()
    print(f"✓ Configuration: {msg}")
    print(f"✓ Robot ID: {ROBOT.robot_id}")
    print(f"✓ Deployment: {DEPLOYMENT_MODE}")
