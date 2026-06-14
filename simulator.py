"""
VAYU X - Software-in-the-Loop Simulator
Complete simulation environment without Flask dependency
Pure Python simulation that mimics real hardware behavior
"""

import time
import threading
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# ============================================================================
# VIRTUAL HARDWARE SIMULATION
# ============================================================================

@dataclass
class VirtualSensor:
    """Simulated sensor with realistic data"""
    name: str
    min_value: float
    max_value: float
    noise_level: float = 0.01
    
    def read(self) -> float:
        """Read sensor with realistic noise"""
        value = np.random.uniform(self.min_value, self.max_value)
        noise = np.random.normal(0, self.noise_level)
        return value + noise

class VirtualCamera:
    """Simulated camera that generates realistic frames"""
    
    def __init__(self, width: int = 320, height: int = 240):
        self.width = width
        self.height = height
        self.frame_count = 0
    
    def capture_frame(self) -> np.ndarray:
        """Simulate camera capture"""
        # Simulate video noise and objects
        frame = np.random.randint(50, 150, (self.height, self.width, 3), dtype=np.uint8)
        
        # Add simulated person/object detection areas
        if np.random.random() > 0.7:
            # Random rectangle as detected object
            x = np.random.randint(0, self.width - 100)
            y = np.random.randint(0, self.height - 100)
            frame[y:y+100, x:x+100] = np.random.randint(150, 200, (100, 100, 3))
        
        self.frame_count += 1
        return frame

class VirtualMotors:
    """Simulated motor control"""
    
    def __init__(self):
        self.left_speed = 0.0
        self.right_speed = 0.0
        self.left_power = 0.0
        self.right_power = 0.0
    
    def set_speed(self, left: float, right: float):
        """Set motor speeds (-1.0 to 1.0)"""
        self.left_speed = np.clip(left, -1.0, 1.0)
        self.right_speed = np.clip(right, -1.0, 1.0)
    
    def get_current(self) -> Dict[str, float]:
        """Get motor current (for load estimation)"""
        return {
            "left_current": abs(self.left_speed) * 2.0,  # Simulate 0-2A
            "right_current": abs(self.right_speed) * 2.0
        }

class VirtualIMU:
    """Simulated Inertial Measurement Unit"""
    
    def __init__(self):
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
    
    def read(self) -> Dict[str, float]:
        """Read IMU data with noise"""
        return {
            "pitch": self.pitch + np.random.normal(0, 0.5),
            "roll": self.roll + np.random.normal(0, 0.5),
            "yaw": self.yaw + np.random.normal(0, 0.5),
            "accel_x": np.random.normal(0, 0.1),
            "accel_y": np.random.normal(0, 0.1),
            "accel_z": 9.81 + np.random.normal(0, 0.1)
        }

class VirtualBattery:
    """Simulated battery system"""
    
    def __init__(self, capacity_mah: float = 5000):
        self.capacity_mah = capacity_mah
        self.current_mah = capacity_mah * 0.8  # Start at 80%
        self.charging = False
    
    def read(self) -> Dict[str, float]:
        """Read battery status"""
        percentage = (self.current_mah / self.capacity_mah) * 100
        voltage = 8.0 + (percentage / 100) * 4.8  # 8V to 12.8V range
        
        return {
            "voltage": voltage,
            "percentage": percentage,
            "current_ma": 500,  # Assumed 500mA draw
            "temperature": 35 + np.random.normal(0, 2)
        }
    
    def drain(self, current_ma: float, delta_time: float):
        """Drain battery over time"""
        self.current_mah -= (current_ma * delta_time / 3600)
        self.current_mah = max(0, self.current_mah)

class VirtualEnvironment:
    """Simulated environment and obstacles"""
    
    def __init__(self, width: float = 20, height: float = 20):
        self.width = width
        self.height = height
        self.obstacles = [
            {"x": 5, "y": 5, "radius": 1.0},
            {"x": 10, "y": 15, "radius": 0.8},
            {"x": 15, "y": 8, "radius": 1.2},
        ]
        self.people = []
    
    def get_obstacles_in_range(self, robot_x: float, robot_y: float, range_m: float) -> List[Dict]:
        """Get obstacles within detection range"""
        detected = []
        for obs in self.obstacles:
            distance = np.sqrt((obs["x"] - robot_x)**2 + (obs["y"] - robot_y)**2)
            if distance <= range_m:
                detected.append({
                    "x": obs["x"],
                    "y": obs["y"],
                    "distance": distance,
                    "radius": obs["radius"]
                })
        return detected
    
    def add_person(self, x: float, y: float, name: str = "visitor"):
        """Add person to environment"""
        self.people.append({"x": x, "y": y, "name": name, "id": len(self.people)})
    
    def remove_person(self, person_id: int):
        """Remove person from environment"""
        self.people = [p for p in self.people if p["id"] != person_id]

# ============================================================================
# VIRTUAL ROBOT SIMULATOR
# ============================================================================

class VirtualRobot:
    """Complete virtual robot simulation"""
    
    def __init__(self, robot_id: str = "vayu_001"):
        self.robot_id = robot_id
        self.position = {"x": 0.0, "y": 0.0, "heading": 0.0}
        self.velocity = {"vx": 0.0, "vy": 0.0, "omega": 0.0}
        
        # Virtual hardware
        self.camera = VirtualCamera()
        self.motors = VirtualMotors()
        self.imu = VirtualIMU()
        self.battery = VirtualBattery()
        
        # Virtual sensors
        self.temperature_sensor = VirtualSensor("temperature", 20, 40, 0.5)
        self.distance_sensor = VirtualSensor("ultrasonic", 0.05, 5.0, 0.1)
        
        # Environment
        self.environment = VirtualEnvironment()
        
        # Simulation time
        self.last_update = time.time()
        self.simulation_step = 0
    
    def step(self, delta_time: float = 0.05):
        """Simulate one time step"""
        # Update position based on velocity
        self.position["x"] += self.velocity["vx"] * delta_time
        self.position["y"] += self.velocity["vy"] * delta_time
        self.position["heading"] += self.velocity["omega"] * delta_time
        
        # Wrap heading to 0-360
        self.position["heading"] = self.position["heading"] % 360
        
        # Update velocity (friction/deceleration)
        self.velocity["vx"] *= 0.95
        self.velocity["vy"] *= 0.95
        self.velocity["omega"] *= 0.95
        
        # Motor-to-velocity conversion
        wheel_speed = 0.5  # m/s per unit speed
        self.velocity["vx"] = (self.motors.left_speed + self.motors.right_speed) / 2 * wheel_speed
        
        # Drain battery
        total_current = np.sqrt(
            self.motors.left_speed**2 + self.motors.right_speed**2
        ) * 1000  # Convert to mA
        self.battery.drain(total_current, delta_time)
        
        self.simulation_step += 1
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete robot status"""
        battery = self.battery.read()
        imu = self.imu.read()
        obstacles = self.environment.get_obstacles_in_range(
            self.position["x"], self.position["y"], 2.0
        )
        
        return {
            "robot_id": self.robot_id,
            "timestamp": time.time(),
            "position": self.position.copy(),
            "velocity": self.velocity.copy(),
            "battery": battery,
            "temperature": self.temperature_sensor.read(),
            "imu": imu,
            "obstacles": obstacles,
            "people": self.environment.people.copy(),
            "simulation_step": self.simulation_step
        }
    
    def move(self, vx: float, vy: float, omega: float = 0):
        """Command robot movement"""
        self.motors.set_speed(vx, vy)
        self.velocity["vx"] = vx * 0.5
        self.velocity["vy"] = vy * 0.5
        self.velocity["omega"] = omega
    
    def capture_frame(self) -> np.ndarray:
        """Capture camera frame"""
        return self.camera.capture_frame()
    
    def set_temperature(self, temp: float):
        """Set internal temperature (for testing)"""
        self.imu.pitch = temp - 25  # Convert to pitch simulation

# ============================================================================
# SIMULATOR MANAGER
# ============================================================================

class VAYUSimulator:
    """Manages complete VAYU X simulation environment"""
    
    def __init__(self, num_robots: int = 1):
        self.robots: Dict[str, VirtualRobot] = {}
        self.environment = VirtualEnvironment()
        self.running = False
        self.simulation_speed = 1.0  # 1.0 = real-time
        self.dt = 0.05  # 50ms simulation step
        self.simulator_thread = None
        
        # Create robots
        for i in range(num_robots):
            robot_id = f"vayu_{str(i+1).zfill(3)}"
            self.robots[robot_id] = VirtualRobot(robot_id)
        
        print(f"✓ VAYUSimulator initialized with {num_robots} robot(s)")
    
    def start(self):
        """Start simulation"""
        self.running = True
        self.simulator_thread = threading.Thread(target=self._run, daemon=True)
        self.simulator_thread.start()
        print("✓ Simulation started")
    
    def stop(self):
        """Stop simulation"""
        self.running = False
        if self.simulator_thread:
            self.simulator_thread.join(timeout=2)
        print("✓ Simulation stopped")
    
    def _run(self):
        """Main simulation loop"""
        while self.running:
            start_time = time.time()
            
            # Step all robots
            for robot in self.robots.values():
                robot.step(self.dt * self.simulation_speed)
            
            # Control frame rate
            elapsed = time.time() - start_time
            sleep_time = (self.dt * self.simulation_speed) - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def get_robot_status(self, robot_id: str) -> Dict[str, Any]:
        """Get specific robot status"""
        if robot_id in self.robots:
            return self.robots[robot_id].get_status()
        return {}
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all robots"""
        return {
            robot_id: robot.get_status()
            for robot_id, robot in self.robots.items()
        }
    
    def move_robot(self, robot_id: str, vx: float, vy: float, omega: float = 0):
        """Command robot movement"""
        if robot_id in self.robots:
            self.robots[robot_id].move(vx, vy, omega)
    
    def add_person(self, x: float, y: float):
        """Add simulated person to environment"""
        for robot in self.robots.values():
            robot.environment.add_person(x, y)
    
    def set_robot_temperature(self, robot_id: str, temp: float):
        """Set robot temperature (for testing)"""
        if robot_id in self.robots:
            self.robots[robot_id].set_temperature(temp)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get simulation statistics"""
        return {
            "total_robots": len(self.robots),
            "simulation_running": self.running,
            "simulation_speed": self.simulation_speed,
            "timestamp": time.time(),
            "robot_statuses": self.get_all_status()
        }

# ============================================================================
# VISUALIZATION (Terminal-based)
# ============================================================================

class TerminalVisualizer:
    """Terminal-based visualization of simulation"""
    
    @staticmethod
    def print_robot_status(robot_status: Dict[str, Any]):
        """Print formatted robot status"""
        print("\n" + "="*70)
        print(f"🤖 {robot_status['robot_id']} - Status Report")
        print("="*70)
        
        pos = robot_status['position']
        print(f"Position: X={pos['x']:.2f}m, Y={pos['y']:.2f}m, Heading={pos['heading']:.1f}°")
        
        vel = robot_status['velocity']
        print(f"Velocity: VX={vel['vx']:.2f}m/s, VY={vel['vy']:.2f}m/s, Omega={vel['omega']:.2f}°/s")
        
        bat = robot_status['battery']
        print(f"Battery: {bat['percentage']:.1f}% ({bat['voltage']:.2f}V) - {bat['temperature']:.1f}°C")
        
        temp = robot_status['temperature']
        print(f"Temperature: {temp:.1f}°C")
        
        obstacles = robot_status['obstacles']
        if obstacles:
            print(f"Obstacles Detected: {len(obstacles)}")
            for obs in obstacles:
                print(f"  - Distance: {obs['distance']:.2f}m")
        else:
            print("Obstacles: None detected")
        
        people = robot_status['people']
        if people:
            print(f"People Detected: {len(people)}")
        
        print("="*70)
    
    @staticmethod
    def print_all_robots(all_status: Dict[str, Any]):
        """Print all robots in tabular format"""
        print("\n" + "="*100)
        print(f"{'Robot ID':<15} {'Position (X,Y)':<20} {'Battery':<12} {'Temp':<8} {'Status':<10}")
        print("="*100)
        
        for robot_id, status in all_status.items():
            pos = status['position']
            bat = status['battery']
            temp = status['temperature']
            
            pos_str = f"({pos['x']:.1f}, {pos['y']:.1f})"
            bat_str = f"{bat['percentage']:.0f}%"
            temp_str = f"{temp:.1f}°C"
            status_str = "🟢 OK" if bat['percentage'] > 10 else "🔴 Low"
            
            print(f"{robot_id:<15} {pos_str:<20} {bat_str:<12} {temp_str:<8} {status_str:<10}")
        
        print("="*100)

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("\n🎮 VAYU X Software-in-the-Loop Simulator")
    print("="*70)
    
    # Create simulator
    simulator = VAYUSimulator(num_robots=3)
    
    # Start simulation
    simulator.start()
    
    # Add obstacles and people
    simulator.add_person(5, 5)
    simulator.add_person(10, 10)
    
    # Run simulation
    try:
        for i in range(20):
            time.sleep(0.5)
            
            # Get all status
            all_status = simulator.get_all_status()
            TerminalVisualizer.print_all_robots(all_status)
            
            # Move first robot
            if i < 10:
                simulator.move_robot("vayu_001", 0.5, 0.2)
            
            # Move second robot
            if i >= 10:
                simulator.move_robot("vayu_002", -0.3, 0.4)
    
    except KeyboardInterrupt:
        print("\n⏹️ Stopping simulation...")
    
    finally:
        simulator.stop()
        print("✓ Simulation closed")
