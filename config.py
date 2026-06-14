"""
VAYU X - Multi-Agent Autonomous Assistance Platform
Core Configuration Module
Production-Grade Configuration Management
"""

import os
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# ENVIRONMENT & DEPLOYMENT
# ============================================================================

# Deployment Mode
DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "museum")  # museum, home, security, warehouse
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")# production, staging, development
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # DEBUG, INFO, WARNING, ERROR
DEBUG_MODE = ENVIRONMENT == "development"

# ============================================================================
# ROBOT IDENTIFICATION
# ============================================================================

@dataclass
class RobotConfig:
    """Robot identification and configuration"""
    robot_id: str = os.getenv("ROBOT_ID", "vayu_001")
    robot_name: str = "VAYU X"
    firmware_version: str = "2.0.0"
    hardware_version: str = "1.0"
    location: str = os.getenv("ROBOT_LOCATION", "museum_entrance")

ROBOT = RobotConfig()

# ============================================================================
# NETWORK CONFIGURATION
# ============================================================================

class NetworkConfig:
    """Network configuration for ESP32 and cloud connectivity"""
    
    # WiFi Configuration
    WIFI_SSID = os.getenv("WIFI_SSID", "VAYU_NETWORK")
    WIFI_PASSWORD = os.getenv("WIFI_PASSWORD", "secure_password")
    WIFI_TIMEOUT = 10  # seconds
    
    # MQTT Configuration
    MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
    MQTT_USERNAME = os.getenv("MQTT_USERNAME", "vayu_user")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "vayu_password")
    MQTT_KEEPALIVE = 60  # seconds
    MQTT_CLIENT_ID = f"vayu_{ROBOT.robot_id}"
    
    # ESP-NOW Mesh Configuration
    ESPNOW_ENABLED = True
    ESPNOW_ENCRYPTION = True
    ESPNOW_PMK = os.getenv("ESPNOW_PMK", "ESPNOW_PMK1234567890")
    ESPNOW_MAX_PEERS = 20
    
    # MQTT Topics
    MQTT_TOPICS = {
        "status": f"vayu/{ROBOT.robot_id}/status",
        "command": f"vayu/{ROBOT.robot_id}/command",
        "telemetry": f"vayu/{ROBOT.robot_id}/telemetry",
        "vision": f"vayu/{ROBOT.robot_id}/vision",
        "voice": f"vayu/{ROBOT.robot_id}/voice",
        "motion": f"vayu/{ROBOT.robot_id}/motion",
        "safety": f"vayu/{ROBOT.robot_id}/safety",
        "mission": f"vayu/{ROBOT.robot_id}/mission",
        "error": f"vayu/{ROBOT.robot_id}/error",
        "fleet": f"vayu/fleet/status",
        "digital_twin": f"vayu/{ROBOT.robot_id}/digital_twin"
    }

# ============================================================================
# AGENT CONFIGURATION
# ============================================================================

class AgentConfig:
    """Configuration for individual agents"""
    
    # Vision Agent (ESP32-CAM)
    VISION_AGENT = {
        "enabled": True,
        "hardware": "ESP32-CAM",
        "camera": "OV2640",
        "resolution": (320, 240),  # For performance
        "fps": 15,
        "buffer_size": 4096,
        "jpeg_quality": 80,
        "timeout": 5.0,
    }
    
    # Voice Agent (ESP32-S3)
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
    
    # Motion Agent (ESP32-S3 + Motors)
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
    
    # Safety Agent (Distributed)
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
    
    # Mission Planner (Master)
    MISSION_PLANNER = {
        "enabled": True,
        "decision_interval_ms": 100,
        "max_mission_duration_seconds": 3600,
        "mission_queue_size": 50,
    }

# ============================================================================
# ML MODEL CONFIGURATION
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
            "keywords": ["follow", "stop", "next", "exit", "help", "repeat"],
            "threshold": 0.7,
        },
    }
    
    # Quantization Settings
    QUANTIZATION = "int8"  # int8 for ESP32 optimization
    
    # Model Inference
    MODEL_INFERENCE_TIMEOUT_MS = 500
    MODEL_INFERENCE_THREADS = 1  # For ESP32, use 1 thread

# ============================================================================
# SENSOR CONFIGURATION
# ============================================================================

class SensorConfig:
    """Hardware sensor configuration"""
    
    # I2C Configuration
    I2C_FREQUENCY = 400000  # 400kHz
    I2C_TIMEOUT = 1.0
    
    # Sensors
    SENSORS = {
        "imu_mpu6050": {
            "enabled": True,
            "address": 0x68,
            "sample_rate": 100,
            "accel_range": 2,  # ±2g
            "gyro_range": 250,  # ±250°/s
        },
        "ultrasonic_hcsr04": {
            "enabled": True,
            "trigger_pins": [12, 13, 14],  # Front, left, right
            "echo_pins": [15, 16, 17],
            "max_distance_cm": 400,
            "timeout_us": 30000,
        },
        "battery_ina219": {
            "enabled": True,
            "address": 0x40,
            "sample_interval": 1.0,
            "moving_average_window": 10,
        },
        "tof_vl53l0x": {
            "enabled": False,  # Optional
            "address": 0x29,
            "sample_rate": 50,
            "max_range_mm": 1200,
        },
    }

# ============================================================================
# DEPLOYMENT MODES
# ============================================================================

class DeploymentModes(Enum):
    """Supported deployment modes"""
    MUSEUM = "museum"
    HOME = "home"
    SECURITY = "security"
    WAREHOUSE = "warehouse"
    CUSTOM = "custom"

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
# PERFORMANCE TUNING
# ============================================================================

class PerformanceConfig:
    """Performance and optimization settings"""
    
    # Threading
    MAX_THREADS = 4
    THREAD_POOL_SIZE = 2
    
    # Memory
    MAX_BUFFER_SIZE_MB = 20
    QUEUE_MAX_SIZE = 100
    
    # Timing
    SENSOR_POLL_INTERVAL_MS = 50
    DECISION_INTERVAL_MS = 100
    TELEMETRY_INTERVAL_S = 5
    HEARTBEAT_INTERVAL_S = 10
    
    # Network
    PACKET_MAX_SIZE_BYTES = 1024
    RETRY_MAX_ATTEMPTS = 3
    RETRY_BACKOFF_MS = 1000

# ============================================================================
# HARDWARE PIN CONFIGURATION (ESP32-S3 N16R8)
# ============================================================================

class PinConfig:
    """GPIO pin assignments for ESP32-S3"""
    
    # Motor Control (TB6612FNG)
    MOTOR_LEFT_PWM = 5
    MOTOR_LEFT_FORWARD = 6
    MOTOR_LEFT_BACKWARD = 7
    MOTOR_RIGHT_PWM = 8
    MOTOR_RIGHT_FORWARD = 9
    MOTOR_RIGHT_BACKWARD = 10
    
    # Servo Control
    SERVO_HORIZONTAL = 2
    SERVO_VERTICAL = 3
    
    # Audio
    AUDIO_SCK = 39
    AUDIO_WS = 40
    AUDIO_SD_IN = 41
    AUDIO_SD_OUT = 42
    
    # Sensors
    ULTRASONIC_TRIG_FRONT = 12
    ULTRASONIC_ECHO_FRONT = 13
    
    # Status LEDs
    LED_POWER = 48
    LED_WIFI = 47
    LED_MQTT = 46
    LED_ERROR = 45
    
    # Safety
    EMERGENCY_BUTTON = 11
    
    # I2C
    I2C_SDA = 4
    I2C_SCL = 3

# ============================================================================
# SAFETY THRESHOLDS
# ============================================================================

class SafetyThresholds:
    """Safety-critical thresholds"""
    
    # Battery
    BATTERY_VOLTAGE_MIN = 10.0  # volts
    BATTERY_VOLTAGE_CRITICAL = 8.0  # volts
    BATTERY_VOLTAGE_MAX = 16.8  # volts
    
    # Temperature
    THERMAL_WARNING = 70.0  # celsius
    THERMAL_CRITICAL = 85.0  # celsius
    
    # Motion
    MAX_LINEAR_VELOCITY = 0.5  # m/s
    MAX_ANGULAR_VELOCITY = 180.0  # degrees/s
    MAX_ACCELERATION = 0.2  # m/s²
    
    # Obstacle
    OBSTACLE_DISTANCE_MIN = 0.2  # meters
    OBSTACLE_DETECTION_RANGE = 2.0  # meters
    
    # Tilt
    MAX_TILT_ANGLE = 45.0  # degrees
    MAX_ROLL_ANGLE = 45.0  # degrees

# ============================================================================
# API & CLOUD CONFIGURATION
# ============================================================================

class CloudConfig:
    """Cloud services configuration (optional, not required for operation)"""
    
    # Firebase Configuration
    FIREBASE_ENABLED = False  # Optional for digital twin
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
    
    # AWS IoT Core (Alternative)
    AWS_IOT_ENABLED = False
    AWS_IOT_ENDPOINT = os.getenv("AWS_IOT_ENDPOINT", "")
    AWS_IOT_CERT_PATH = os.getenv("AWS_IOT_CERT_PATH", "")
    
    # Cloud is Optional - Edge-First Architecture
    CLOUD_OPTIONAL = True  # System works without cloud

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_mqtt_topic(agent_name: str) -> str:
    """Get MQTT topic for specific agent"""
    return NetworkConfig.MQTT_TOPICS.get(agent_name, f"vayu/{agent_name}")

def get_agent_config(agent_name: str) -> Dict:
    """Get configuration for specific agent"""
    agent_map = {
        "vision": AgentConfig.VISION_AGENT,
        "voice": AgentConfig.VOICE_AGENT,
        "motion": AgentConfig.MOTION_AGENT,
        "safety": AgentConfig.SAFETY_AGENT,
        "mission": AgentConfig.MISSION_PLANNER,
    }
    return agent_map.get(agent_name, {})

def is_deployment_feature_enabled(feature: str) -> bool:
    """Check if feature is enabled for current deployment mode"""
    mode = DEPLOYMENT_MODE.lower()
    features = DEPLOYMENT_FEATURES.get(mode, {})
    return features.get(feature, False)

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config() -> Tuple[bool, str]:
    """Validate configuration for consistency and safety"""
    
    # Check deployment mode
    valid_modes = [m.value for m in DeploymentModes]
    if DEPLOYMENT_MODE not in valid_modes:
        return False, f"Invalid deployment mode: {DEPLOYMENT_MODE}"
    
    # Check battery thresholds
    if SafetyThresholds.BATTERY_VOLTAGE_CRITICAL >= SafetyThresholds.BATTERY_VOLTAGE_MIN:
        return False, "Critical battery voltage >= min voltage"
    
    # Check temperature thresholds
    if SafetyThresholds.THERMAL_CRITICAL <= SafetyThresholds.THERMAL_WARNING:
        return False, "Thermal critical <= thermal warning"
    
    # Check velocity limits
    if SafetyThresholds.MAX_LINEAR_VELOCITY <= 0:
        return False, "Max linear velocity must be positive"
    
    return True, "Configuration valid"

# ============================================================================
# INITIALIZATION
# ============================================================================

if __name__ == "__main__":
    # Validate configuration on import
    is_valid, msg = validate_config()
    if not is_valid:
        raise RuntimeError(f"Configuration validation failed: {msg}")
    
    print(f"✓ VAYU X Configuration Loaded")
    print(f"  Robot ID: {ROBOT.robot_id}")
    print(f"  Deployment: {DEPLOYMENT_MODE}")
    print(f"  Environment: {ENVIRONMENT}")
