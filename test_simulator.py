#!/usr/bin/env python3
"""
VAYU X - Quick Test Script
Verify simulator and all components work before hackathon
Run this to check everything is functioning
"""

import sys
import time
import numpy as np

def test_imports():
    """Test that all required modules can be imported"""
    print("\n" + "="*70)
    print("TEST 1: Import Validation")
    print("="*70)
    
    tests = [
        ("numpy", "import numpy as np"),
        ("threading", "import threading"),
        ("dataclasses", "from dataclasses import dataclass"),
        ("typing", "from typing import Dict, List, Any"),
    ]
    
    for name, code in tests:
        try:
            exec(code)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - MISSING")
            return False
    
    return True

def test_simulator():
    """Test virtual simulator components"""
    print("\n" + "="*70)
    print("TEST 2: Virtual Simulator")
    print("="*70)
    
    try:
        from simulator import VirtualCamera, VirtualMotors, VirtualIMU, VirtualBattery
        from simulator import VirtualRobot, VirtualEnvironment, VAYUSimulator
        
        # Test camera
        print("Testing VirtualCamera...")
        camera = VirtualCamera(320, 240)
        frame = camera.capture_frame()
        assert frame.shape == (240, 320, 3), "Camera frame shape wrong"
        assert frame.dtype == np.uint8, "Camera frame dtype wrong"
        print("  ✓ VirtualCamera working")
        
        # Test motors
        print("Testing VirtualMotors...")
        motors = VirtualMotors()
        motors.set_speed(0.5, 0.5)
        assert motors.left_speed == 0.5, "Motor speed not set"
        print("  ✓ VirtualMotors working")
        
        # Test IMU
        print("Testing VirtualIMU...")
        imu = VirtualIMU()
        reading = imu.read()
        assert "pitch" in reading and "roll" in reading, "IMU data incomplete"
        print("  ✓ VirtualIMU working")
        
        # Test Battery
        print("Testing VirtualBattery...")
        battery = VirtualBattery()
        status = battery.read()
        assert 0 <= status["percentage"] <= 100, "Battery percentage invalid"
        assert status["voltage"] > 0, "Battery voltage invalid"
        print("  ✓ VirtualBattery working")
        
        # Test Robot
        print("Testing VirtualRobot...")
        robot = VirtualRobot("test_robot")
        robot.step(0.05)
        status = robot.get_status()
        assert "position" in status, "Robot status missing position"
        assert "battery" in status, "Robot status missing battery"
        assert "temperature" in status, "Robot status missing temperature"
        print("  ✓ VirtualRobot working")
        
        # Test Environment
        print("Testing VirtualEnvironment...")
        env = VirtualEnvironment()
        env.add_person(5, 5, "visitor")
        assert len(env.people) == 1, "Person not added to environment"
        print("  ✓ VirtualEnvironment working")
        
        # Test Simulator
        print("Testing VAYUSimulator...")
        simulator = VAYUSimulator(num_robots=1)
        assert len(simulator.robots) == 1, "Simulator robot not created"
        simulator.start()
        time.sleep(0.2)
        status = simulator.get_robot_status("vayu_001")
        assert status is not None, "Simulator robot status unavailable"
        simulator.stop()
        print("  ✓ VAYUSimulator working")
        
        return True
    
    except Exception as e:
        print(f"✗ Simulator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration system"""
    print("\n" + "="*70)
    print("TEST 3: Configuration System")
    print("="*70)
    
    try:
        from config_fixed import (
            validate_config, 
            ROBOT, 
            DEPLOYMENT_MODE,
            SafetyThresholds,
            MLConfig
        )
        
        # Test validation
        print("Testing configuration validation...")
        is_valid, msg = validate_config()
        assert is_valid, f"Config invalid: {msg}"
        print("  ✓ Configuration valid")
        
        # Test robot config
        print("Testing robot configuration...")
        assert ROBOT.robot_id, "Robot ID not set"
        assert ROBOT.robot_name, "Robot name not set"
        print(f"  ✓ Robot configured: {ROBOT.robot_id}")
        
        # Test safety thresholds
        print("Testing safety thresholds...")
        assert SafetyThresholds.BATTERY_CRITICAL < SafetyThresholds.BATTERY_VOLTAGE_MIN
        assert SafetyThresholds.THERMAL_WARNING < SafetyThresholds.THERMAL_CRITICAL
        print("  ✓ Safety thresholds valid")
        
        # Test ML models
        print("Testing ML model configuration...")
        models = MLConfig.TFLITE_MODELS
        assert "person_detection" in models
        assert "keyword_detection" in models
        assert "input_size" in models["keyword_detection"], "Keyword model missing input_size"
        print("  ✓ ML models configured")
        
        # Test deployment
        print(f"Testing deployment mode: {DEPLOYMENT_MODE}...")
        valid_modes = ["museum", "home", "security", "warehouse"]
        assert DEPLOYMENT_MODE in valid_modes, f"Invalid deployment mode: {DEPLOYMENT_MODE}"
        print(f"  ✓ Deployment mode: {DEPLOYMENT_MODE}")
        
        return True
    
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_physics():
    """Test physics simulation"""
    print("\n" + "="*70)
    print("TEST 4: Physics Simulation")
    print("="*70)
    
    try:
        from simulator import VirtualRobot
        
        robot = VirtualRobot("physics_test")
        
        # Test movement
        print("Testing robot movement...")
        initial_x = robot.position["x"]
        robot.motors.set_speed(1.0, 1.0)
        robot.step(0.1)
        assert robot.position["x"] > initial_x, "Robot should have moved forward"
        print("  ✓ Movement working")
        
        # Test battery drain
        print("Testing battery drain...")
        initial_capacity = robot.battery.current_mah
        robot.motors.set_speed(1.0, 1.0)
        robot.battery.drain(1000, 0.1)  # 1A for 0.1s
        assert robot.battery.current_mah < initial_capacity, "Battery should drain"
        print("  ✓ Battery drain working")
        
        # Test friction
        print("Testing friction/deceleration...")
        robot.motors.set_speed(1.0, 1.0)
        robot.step(0.05)
        velocity_before = robot.velocity["vx"]
        robot.step(0.05)
        velocity_after = robot.velocity["vx"]
        assert velocity_after < velocity_before, "Velocity should decrease (friction)"
        print("  ✓ Friction working")
        
        # Test obstacle detection
        print("Testing obstacle detection...")
        obstacles = robot.environment.get_obstacles_in_range(0, 0, 5.0)
        assert isinstance(obstacles, list), "Should return list of obstacles"
        print(f"  ✓ Obstacle detection working ({len(obstacles)} detected)")
        
        return True
    
    except Exception as e:
        print(f"✗ Physics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_visualization():
    """Test visualization system"""
    print("\n" + "="*70)
    print("TEST 5: Visualization System")
    print("="*70)
    
    try:
        from simulator import TerminalVisualizer, VAYUSimulator
        
        # Create simulator
        simulator = VAYUSimulator(num_robots=1)
        simulator.start()
        time.sleep(0.1)
        
        # Get status
        status = simulator.get_robot_status("vayu_001")
        
        # Test visualization (just make sure it doesn't crash)
        print("Testing status visualization...")
        TerminalVisualizer.print_robot_status(status)
        print("  ✓ Robot status visualization working")
        
        # Test all robots visualization
        print("Testing multi-robot visualization...")
        all_status = simulator.get_all_status()
        TerminalVisualizer.print_all_robots(all_status)
        print("  ✓ Multi-robot visualization working")
        
        simulator.stop()
        return True
    
    except Exception as e:
        print(f"✗ Visualization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "🤖 VAYU X - SYSTEM TEST SUITE" + " "*24 + "║")
    print("╚" + "="*68 + "╝")
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Simulator", test_simulator()))
    results.append(("Configuration", test_configuration()))
    results.append(("Physics", test_physics()))
    results.append(("Visualization", test_visualization()))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} | {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("="*70)
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED!")
        print("\nYou're ready to run:")
        print("  python simulator.py")
        print("  python main_fixed.py")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed")
        print("\nFix the errors above and try again")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
