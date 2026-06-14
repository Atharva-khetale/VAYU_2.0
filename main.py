"""
VAYU X - Main Entry Point
Complete robotic assistance platform launcher
Supports simulation, development, and production modes
"""

import sys
import os
import argparse
import time
import signal
import threading
from typing import Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base import get_logger, VAYULogger
from config import validate_config, ROBOT, DEPLOYMENT_MODE, ENVIRONMENT
from orchestrator import VAYUOrchestrator

# ============================================================================
# SYSTEM LAUNCHER
# ============================================================================

class VAYUSystemLauncher:
    """Main system launcher and orchestration"""
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.logger = get_logger("Launcher")
        self.orchestrator: Optional[VAYUOrchestrator] = None
        self.running = False
        
        # Register signal handlers for graceful shutdown
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
    
    def initialize_system(self) -> bool:
        """Initialize VAYU X system"""
        self.logger.info("Initializing VAYU X system...")
        
        try:
            self.orchestrator = VAYUOrchestrator()
            
            if not self.orchestrator.initialize():
                self.logger.error("System initialization failed")
                return False
            
            self.running = True
            self.logger.info("✓ VAYU X system initialized")
            return True
        
        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            return False
    
    def launch_dashboard(self) -> bool:
        """Launch web dashboard"""
        if not self.args.dashboard:
            return True
        
        try:
            self.logger.info("Launching digital twin dashboard...")
            
            # Import Flask app
            from digital_twin import app, initialize_system as init_dashboard
            
            # Initialize dashboard with existing orchestrator
            import digital_twin
            digital_twin.orchestrator = self.orchestrator
            
            # Run Flask in separate thread
            def run_flask():
                app.run(
                    host='0.0.0.0',
                    port=self.args.port,
                    debug=False,
                    use_reloader=False
                )
            
            flask_thread = threading.Thread(target=run_flask, daemon=True)
            flask_thread.start()
            
            self.logger.info(f"✓ Dashboard launched on http://localhost:{self.args.port}")
            self.logger.info(f"  Open browser to http://localhost:{self.args.port}/dashboard")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Dashboard launch failed: {e}")
            return False
    
    def run_simulation_mode(self) -> None:
        """Run in simulation mode with active monitoring"""
        self.logger.info("Running in SIMULATION mode")
        self.logger.info("=" * 60)
        
        try:
            while self.running:
                time.sleep(5)
                
                # Print periodic status
                status = self.orchestrator.get_status()
                
                self.logger.info("-" * 60)
                self.logger.info(f"VAYU X Status Report @ {time.strftime('%H:%M:%S')}")
                self.logger.info(f"  Robot ID: {status['robot_id']}")
                self.logger.info(f"  Deployment: {status['deployment_mode'].upper()}")
                self.logger.info(f"  Agents: {status['agent_count']}")
                self.logger.info(f"  Healthy: {sum(1 for a in status['agents'].values() if a['is_healthy'])}/{status['agent_count']}")
                
                context = status['context']
                self.logger.info(f"  Battery: {context['battery_percentage']}% ({context['battery_voltage']:.1f}V)")
                self.logger.info(f"  Temperature: {context['temperature_celsius']:.1f}°C")
                self.logger.info(f"  State: {context['state'].upper()}")
                self.logger.info(f"  Detected Objects: {len(context['detected_persons'])} persons")
                
                # Print agent details
                self.logger.info("  Agent Status:")
                for agent_id, agent_status in status['agents'].items():
                    health_indicator = "✓" if agent_status['is_healthy'] else "✗"
                    self.logger.info(f"    {health_indicator} {agent_id}: {agent_status['uptime_seconds']:.1f}s uptime")
        
        except KeyboardInterrupt:
            self.logger.info("Simulation interrupted by user")
        except Exception as e:
            self.logger.error(f"Simulation error: {e}")
    
    def run_interactive_mode(self) -> None:
        """Run in interactive mode with command line interface"""
        self.logger.info("Running in INTERACTIVE mode")
        self.logger.info("Type 'help' for available commands")
        self.logger.info("=" * 60)
        
        while self.running:
            try:
                cmd = input("\n>> ").strip().lower()
                
                if not cmd:
                    continue
                
                if cmd == "help":
                    self.print_help()
                
                elif cmd == "status":
                    status = self.orchestrator.get_status()
                    self.print_status(status)
                
                elif cmd == "agents":
                    agents = self.orchestrator.agent_manager.get_all_agents()
                    self.print_agents(agents)
                
                elif cmd == "mission":
                    mission_agent = self.orchestrator.agent_manager.get_agent("mission_001")
                    if mission_agent:
                        mission_status = mission_agent.get_mission_status()
                        self.logger.info(f"Mission Status: {mission_status}")
                
                elif cmd == "speak":
                    text = input("Enter text to speak: ")
                    voice_agent = self.orchestrator.agent_manager.get_agent("voice_001")
                    if voice_agent:
                        voice_agent.speak(text)
                        self.logger.info("Speech queued")
                
                elif cmd == "emergency":
                    safety_agent = self.orchestrator.agent_manager.get_agent("safety_001")
                    if safety_agent:
                        safety_agent.emergency_stop_active = True
                        self.logger.warning("EMERGENCY STOP ACTIVATED")
                
                elif cmd == "exit":
                    self.shutdown()
                
                else:
                    self.logger.warning(f"Unknown command: {cmd}")
            
            except KeyboardInterrupt:
                self.shutdown()
            except Exception as e:
                self.logger.error(f"Command error: {e}")
    
    def print_help(self) -> None:
        """Print help message"""
        help_text = """
        Available Commands:
        ==================
        help              - Show this help message
        status            - Print system status
        agents            - List all agents
        mission           - Show mission status
        speak <text>      - Queue text for speech synthesis
        emergency         - Trigger emergency stop
        exit              - Shutdown system
        """
        self.logger.info(help_text)
    
    def print_status(self, status: dict) -> None:
        """Print detailed status"""
        self.logger.info(f"\n=== VAYU X System Status ===")
        self.logger.info(f"Robot ID: {status['robot_id']}")
        self.logger.info(f"Deployment: {status['deployment_mode']}")
        self.logger.info(f"Agents: {status['agent_count']}")
        context = status['context']
        self.logger.info(f"Battery: {context['battery_percentage']}%")
        self.logger.info(f"Temperature: {context['temperature_celsius']:.1f}°C")
        self.logger.info(f"State: {context['state']}")
    
    def print_agents(self, agents: dict) -> None:
        """Print agent list"""
        self.logger.info(f"\n=== {len(agents)} Agents ===")
        for agent_id, agent in agents.items():
            status = agent.get_status()
            health = "✓" if status['is_healthy'] else "✗"
            self.logger.info(f"{health} {agent_id} ({agent.agent_type})")
    
    def shutdown(self) -> None:
        """Shutdown system gracefully"""
        if not self.running:
            return
        
        self.running = False
        self.logger.info("Shutting down VAYU X system...")
        
        try:
            if self.orchestrator:
                self.orchestrator.shutdown()
            self.logger.info("✓ System shutdown complete")
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
    
    def run(self) -> int:
        """Main run loop"""
        try:
            # Validate environment
            if not self.validate_environment():
                return 1
            
            # Initialize system
            if not self.initialize_system():
                return 1
            
            # Launch dashboard if requested
            if not self.launch_dashboard():
                return 1
            
            # Wait for initial startup
            time.sleep(2)
            
            # Run mode
            if self.args.interactive:
                self.run_interactive_mode()
            else:
                self.run_simulation_mode()
            
            return 0
        
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            return 1
        
        finally:
            self.shutdown()

# ============================================================================
# ARGUMENT PARSER
# ============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="VAYU X - Edge-Native Multi-Agent Autonomous Assistance Platform",
        epilog="Example: python main.py --dashboard --port 5000 --mode museum"
    )
    
    parser.add_argument(
        "--dashboard",
        action="store_true",
        default=True,
        help="Launch web dashboard (default: True)"
    )
    
    parser.add_argument(
        "--no-dashboard",
        action="store_false",
        dest="dashboard",
        help="Disable web dashboard"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Dashboard port (default: 5000)"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive CLI mode instead of simulation monitoring"
    )
    
    parser.add_argument(
        "--mode",
        choices=["museum", "home", "security", "warehouse"],
        help="Deployment mode (overrides config)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--robot-id",
        type=str,
        help="Robot identifier (default: vayu_001)"
    )
    
    return parser

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Override environment variables if provided
    if args.mode:
        os.environ["DEPLOYMENT_MODE"] = args.mode
    
    if args.log_level:
        os.environ["LOG_LEVEL"] = args.log_level
    
    if args.robot_id:
        os.environ["ROBOT_ID"] = args.robot_id
    
    # Print banner
    print("\n" + "=" * 70)
    print(" 🤖 VAYU X - Edge-Native Multi-Agent Autonomous Assistance Platform")
    print(" Version: 2.0.0 | Environment: Production-Ready")
    print("=" * 70 + "\n")
    
    # Launch system
    launcher = VAYUSystemLauncher(args)
    exit_code = launcher.run()
    
    sys.exit(exit_code)
