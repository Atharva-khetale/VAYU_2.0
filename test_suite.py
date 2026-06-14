"""
VAYU X - Automated Test Suite
Verify all components work correctly without hardware
Run this before deployment to catch any issues
"""

import sys
import time
import logging
from typing import List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestSuite")

class TestSuite:
    """Comprehensive test suite for VAYU X"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
    
    def run_all_tests(self) -> bool:
        """Run all tests"""
        logger.info("=" * 70)
        logger.info("🧪 VAYU X Test Suite")
        logger.info("=" * 70)
        
        tests = [
            ("Configuration Validation", self.test_config),
            ("Logging System", self.test_logging),
            ("Base Classes", self.test_base_classes),
            ("Edge AI Models", self.test_edge_ai),
            ("Vision Agent", self.test_vision_agent),
            ("Voice Agent", self.test_voice_agent),
            ("Motion Agent", self.test_motion_agent),
            ("Safety Agent", self.test_safety_agent),
            ("Mission Planner", self.test_mission_planner),
            ("Agent Manager", self.test_agent_manager),
            ("Message Bus", self.test_message_bus),
            ("Digital Twin API", self.test_digital_twin),
        ]
        
        for test_name, test_func in tests:
            try:
                logger.info(f"\nRunning: {test_name}")
                logger.info("-" * 70)
                
                success, message = test_func()
                
                if success:
                    logger.info(f"✓ PASSED: {message}")
                    self.tests_passed += 1
                else:
                    logger.error(f"✗ FAILED: {message}")
                    self.tests_failed += 1
                
                self.results.append((test_name, success, message))
            
            except Exception as e:
                logger.error(f"✗ ERROR: {str(e)}")
                self.tests_failed += 1
                self.results.append((test_name, False, str(e)))
        
        # Print summary
        self.print_summary()
        
        return self.tests_failed == 0
    
    def test_config(self) -> Tuple[bool, str]:
        """Test configuration loading"""
        try:
            from config import validate_config, ROBOT, DEPLOYMENT_MODE
            
            is_valid, msg = validate_config()
            if not is_valid:
                return False, f"Config invalid: {msg}"
            
            if not ROBOT.robot_id:
                return False, "Robot ID not set"
            
            if DEPLOYMENT_MODE not in ["museum", "home", "security", "warehouse"]:
                return False, f"Invalid deployment mode: {DEPLOYMENT_MODE}"
            
            return True, f"Config valid (Robot: {ROBOT.robot_id}, Mode: {DEPLOYMENT_MODE})"
        
        except Exception as e:
            return False, str(e)
    
    def test_logging(self) -> Tuple[bool, str]:
        """Test logging system"""
        try:
            from base import get_logger, VAYULogger
            
            logger = get_logger("test_agent")
            logger.info("Test log message")
            
            return True, "Logging system operational"
        
        except Exception as e:
            return False, str(e)
    
    def test_base_classes(self) -> Tuple[bool, str]:
        """Test base agent classes"""
        try:
            from base import Agent, TelemetryEvent, EventType
            
            # Create test agent
            agent = Agent("test_agent_001", "test")
            
            if not agent.startup():
                return False, "Agent startup failed"
            
            status = agent.get_status()
            if not status or not status.get("agent_id"):
                return False, "Agent status invalid"
            
            if not agent.shutdown():
                return False, "Agent shutdown failed"
            
            # Test telemetry
            event = TelemetryEvent(
                EventType.AGENT_STARTUP,
                "test_agent",
                {"status": "ok"}
            )
            
            if not event.to_dict():
                return False, "Event serialization failed"
            
            return True, "Base classes working correctly"
        
        except Exception as e:
            return False, str(e)
    
    def test_edge_ai(self) -> Tuple[bool, str]:
        """Test Edge AI module"""
        try:
            from edge_ai import EdgeAIModelManager, EdgeAIAgent
            
            manager = EdgeAIModelManager()
            if not manager.load_all_models():
                return False, "Failed to load models"
            
            model_info = manager.get_model_info()
            if model_info.get("model_count", 0) == 0:
                return False, "No models loaded"
            
            # Test agent
            agent = EdgeAIAgent()
            if not agent.startup():
                return False, "EdgeAI agent startup failed"
            
            agent.shutdown()
            
            return True, f"Edge AI ready ({model_info.get('model_count')} models)"
        
        except Exception as e:
            return False, str(e)
    
    def test_vision_agent(self) -> Tuple[bool, str]:
        """Test Vision Agent"""
        try:
            from agents import VisionAgent
            
            agent = VisionAgent()
            if not agent.startup():
                return False, "Vision agent startup failed"
            
            # Run a few cycles
            for _ in range(3):
                if not agent.process():
                    return False, "Vision agent process failed"
            
            detections = agent.get_detections()
            agent.shutdown()
            
            return True, "Vision agent operational"
        
        except Exception as e:
            return False, str(e)
    
    def test_voice_agent(self) -> Tuple[bool, str]:
        """Test Voice Agent"""
        try:
            from agents import VoiceAgent
            
            agent = VoiceAgent()
            if not agent.startup():
                return False, "Voice agent startup failed"
            
            agent.speak("Test message")
            
            for _ in range(3):
                if not agent.process():
                    return False, "Voice agent process failed"
            
            agent.shutdown()
            
            return True, "Voice agent operational"
        
        except Exception as e:
            return False, str(e)
    
    def test_motion_agent(self) -> Tuple[bool, str]:
        """Test Motion Agent"""
        try:
            from agents import MotionAgent, MotionCommand
            
            agent = MotionAgent()
            if not agent.startup():
                return False, "Motion agent startup failed"
            
            cmd = MotionCommand(action="forward", speed=0.5, duration=1.0)
            agent.queue_command(cmd)
            
            for _ in range(3):
                if not agent.process():
                    return False, "Motion agent process failed"
            
            pos = agent.get_position()
            if not pos or "x" not in pos:
                return False, "Position data invalid"
            
            agent.shutdown()
            
            return True, "Motion agent operational"
        
        except Exception as e:
            return False, str(e)
    
    def test_safety_agent(self) -> Tuple[bool, str]:
        """Test Safety Agent"""
        try:
            from agents import SafetyAgent
            
            agent = SafetyAgent()
            if not agent.startup():
                return False, "Safety agent startup failed"
            
            for _ in range(3):
                if not agent.process():
                    return False, "Safety agent process failed"
            
            safety_status = agent.get_safety_status()
            if not safety_status or "is_safe" not in safety_status:
                return False, "Safety status invalid"
            
            agent.shutdown()
            
            return True, "Safety agent operational"
        
        except Exception as e:
            return False, str(e)
    
    def test_mission_planner(self) -> Tuple[bool, str]:
        """Test Mission Planner Agent"""
        try:
            from agents import MissionPlannerAgent
            
            agent = MissionPlannerAgent()
            if not agent.startup():
                return False, "Mission planner startup failed"
            
            for _ in range(5):
                if not agent.process():
                    return False, "Mission planner process failed"
            
            mission_status = agent.get_mission_status()
            if not mission_status:
                return False, "Mission status invalid"
            
            agent.shutdown()
            
            return True, "Mission planner operational"
        
        except Exception as e:
            return False, str(e)
    
    def test_agent_manager(self) -> Tuple[bool, str]:
        """Test Agent Manager and Orchestration"""
        try:
            from orchestrator import AgentManager
            from agents import VisionAgent, VoiceAgent, MotionAgent, SafetyAgent, MissionPlannerAgent
            
            manager = AgentManager()
            
            # Register all agents
            agents = [
                VisionAgent("vision_001"),
                VoiceAgent("voice_001"),
                MotionAgent("motion_001"),
                SafetyAgent("safety_001"),
                MissionPlannerAgent("mission_001"),
            ]
            
            for agent in agents:
                if not manager.register_agent(agent):
                    return False, f"Failed to register {agent.agent_id}"
            
            if not manager.startup_all_agents():
                return False, "Startup all agents failed"
            
            time.sleep(0.5)  # Let agents run briefly
            
            health = manager.get_system_health()
            if not health or "agents" not in health:
                return False, "System health invalid"
            
            manager.shutdown_all_agents()
            
            return True, f"Agent manager operational ({len(agents)} agents)"
        
        except Exception as e:
            return False, str(e)
    
    def test_message_bus(self) -> Tuple[bool, str]:
        """Test Message Bus Communication"""
        try:
            from orchestrator import Message, MessageBus, MessageType
            
            bus = MessageBus()
            
            msg = Message(
                MessageType.SENSOR_DATA,
                "sensor_agent",
                "decision_agent",
                {"sensor": "temperature", "value": 25.5}
            )
            
            if not bus.publish(msg):
                return False, "Failed to publish message"
            
            messages = bus.get_messages("decision_agent", timeout=0.1)
            if not messages:
                return False, "Message not received"
            
            return True, "Message bus operational"
        
        except Exception as e:
            return False, str(e)
    
    def test_digital_twin(self) -> Tuple[bool, str]:
        """Test Digital Twin API"""
        try:
            from digital_twin import app
            
            # Test Flask app creation
            if not app:
                return False, "Flask app not created"
            
            # Test client
            client = app.test_client()
            
            # Note: This tests without running the full orchestrator
            # In real deployment, orchestrator would be running
            
            return True, "Digital Twin API ready (orchestrator required for live data)"
        
        except Exception as e:
            return False, str(e)
    
    def print_summary(self) -> None:
        """Print test summary"""
        total = self.tests_passed + self.tests_failed
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 70)
        
        for test_name, success, message in self.results:
            status = "✓ PASS" if success else "✗ FAIL"
            logger.info(f"{status} | {test_name}")
        
        logger.info("-" * 70)
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {self.tests_passed}")
        logger.info(f"Failed: {self.tests_failed}")
        
        if self.tests_failed == 0:
            logger.info("\n✓ ALL TESTS PASSED - System ready for deployment!")
        else:
            logger.warning(f"\n✗ {self.tests_failed} test(s) failed - review errors above")
        
        logger.info("=" * 70)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    suite = TestSuite()
    success = suite.run_all_tests()
    
    sys.exit(0 if success else 1)
