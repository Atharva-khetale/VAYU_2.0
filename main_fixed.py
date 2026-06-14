"""
VAYU X - Fixed Main Entry Point
Proper agent registration and simulation mode
"""

import sys
import os
import time
import signal
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base import get_logger
from config_fixed import validate_config, ROBOT, DEPLOYMENT_MODE, ENVIRONMENT
from simulator import VAYUSimulator, TerminalVisualizer

# Import agent classes (these need to be available)
try:
    from agents import VisionAgent, VoiceAgent, MotionAgent, SafetyAgent, MissionPlannerAgent
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    print("⚠️  Agent modules not available - running in pure simulator mode")

# ============================================================================
# MAIN LAUNCHER
# ============================================================================

class VAYULauncher:
    """Fixed VAYU X launcher with proper initialization"""
    
    def __init__(self):
        self.logger = get_logger("Launcher")
        self.simulator = None
        self.agents = {}
        self.running = False
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info("Shutdown signal received")
        self.shutdown()
        sys.exit(0)
    
    def validate_environment(self) -> bool:
        """Validate system environment"""
        self.logger.info("Validating environment...")
        is_valid, msg = validate_config()
        if not is_valid:
            self.logger.error(f"Configuration validation failed: {msg}")
            return False
        
        self.logger.info("✓ Environment validation passed")
        return True
    
    def initialize_simulator(self) -> bool:
        """Initialize software-in-the-loop simulator"""
        try:
            self.logger.info("Initializing simulator...")
            self.simulator = VAYUSimulator(num_robots=1)
            self.simulator.start()
            self.logger.info("✓ Simulator initialized and running")
            return True
        except Exception as e:
            self.logger.error(f"Simulator initialization failed: {e}")
            return False
    
    def initialize_agents(self) -> bool:
        """Initialize all agents"""
        if not AGENTS_AVAILABLE:
            self.logger.warning("Agents not available - using simulator only")
            return True
        
        try:
            self.logger.info("Initializing agents...")
            
            # Create agents
            agents_list = [
                VisionAgent("vision_001"),
                VoiceAgent("voice_001"),
                MotionAgent("motion_001"),
                SafetyAgent("safety_001"),
                MissionPlannerAgent("mission_001"),
            ]
            
            # Startup agents
            for agent in agents_list:
                if agent.startup():
                    self.agents[agent.agent_id] = agent
                    self.logger.info(f"✓ Agent started: {agent.agent_id}")
                else:
                    self.logger.warning(f"⚠️  Agent startup failed: {agent.agent_id}")
            
            if self.agents:
                self.logger.info(f"✓ {len(self.agents)} agents initialized")
                return True
            else:
                self.logger.warning("⚠️  No agents available")
                return True  # Continue with simulator only
        
        except Exception as e:
            self.logger.error(f"Agent initialization error: {e}")
            return True  # Continue with simulator
    
    def run_interactive_mode(self):
        """Run interactive monitoring mode"""
        self.logger.info("="*70)
        self.logger.info("INTERACTIVE MONITORING MODE")
        self.logger.info("="*70)
        self.logger.info("Commands: status, move, temperature, people, exit")
        
        self.running = True
        
        try:
            while self.running:
                cmd = input("\n>> ").strip().lower()
                
                if cmd == "status":
                    self.show_status()
                
                elif cmd == "move":
                    vx = float(input("  Velocity X (-1 to 1): ") or "0.5")
                    vy = float(input("  Velocity Y (-1 to 1): ") or "0")
                    self.simulator.move_robot("vayu_001", vx, vy)
                    self.logger.info(f"✓ Moving robot: vx={vx}, vy={vy}")
                
                elif cmd == "temperature":
                    temp = float(input("  Temperature (°C): ") or "25")
                    self.simulator.set_robot_temperature("vayu_001", temp)
                    self.logger.info(f"✓ Temperature set to {temp}°C")
                
                elif cmd == "people":
                    x = float(input("  Person X position: ") or "5")
                    y = float(input("  Person Y position: ") or "5")
                    self.simulator.add_person(x, y)
                    self.logger.info(f"✓ Added person at ({x}, {y})")
                
                elif cmd == "exit":
                    self.shutdown()
                
                else:
                    self.logger.info("Unknown command")
        
        except KeyboardInterrupt:
            self.shutdown()
    
    def run_monitoring_mode(self):
        """Run continuous monitoring mode"""
        self.logger.info("="*70)
        self.logger.info("MONITORING MODE (Press Ctrl+C to stop)")
        self.logger.info("="*70)
        
        self.running = True
        
        try:
            while self.running:
                time.sleep(2)
                self.show_status()
        
        except KeyboardInterrupt:
            self.shutdown()
    
    def show_status(self):
        """Show current system status"""
        all_status = self.simulator.get_all_status()
        TerminalVisualizer.print_all_robots(all_status)
        
        # Also print agent status if available
        if self.agents:
            self.logger.info(f"Agents: {len(self.agents)} running")
            for agent_id, agent in self.agents.items():
                status = agent.get_status()
                self.logger.info(f"  ✓ {agent_id}: {status['uptime_seconds']:.1f}s uptime")
    
    def shutdown(self):
        """Shutdown system gracefully"""
        if not self.running:
            return
        
        self.running = False
        self.logger.info("Shutting down system...")
        
        # Stop simulator
        if self.simulator:
            self.simulator.stop()
        
        # Stop agents
        for agent_id, agent in self.agents.items():
            agent.shutdown()
        
        self.logger.info("✓ System shutdown complete")
    
    def run(self):
        """Main run method"""
        try:
            # Validate
            if not self.validate_environment():
                return 1
            
            # Initialize
            if not self.initialize_simulator():
                return 1
            
            if not self.initialize_agents():
                return 1
            
            # Show menu
            print("\n" + "="*70)
            print("🤖 VAYU X Simulation Environment")
            print("="*70)
            print("\n1. Interactive Mode (type commands)")
            print("2. Monitoring Mode (auto-update status)")
            print("3. Exit")
            print("\n", end="")
            
            choice = input("Select mode (1-3): ").strip()
            
            if choice == "1":
                self.run_interactive_mode()
            elif choice == "2":
                self.run_monitoring_mode()
            else:
                self.shutdown()
            
            return 0
        
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            return 1
        
        finally:
            self.shutdown()

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" 🤖 VAYU X - Software-in-the-Loop Simulator")
    print(" Production-Ready Edge-Native Multi-Agent Platform")
    print("="*70 + "\n")
    
    launcher = VAYULauncher()
    exit_code = launcher.run()
    sys.exit(exit_code)
