#!/usr/bin/env python3
"""
Motor utility functions for Mecanum robot
This module provides testing and diagnostic functions for motors
"""

import time
import sys
import os
try:
    import serial
except ImportError:
    print("PySerial not installed. Run: pip install pyserial")
    sys.exit(1)

def test_motors(port, baud_rate=9600, test_duration=1.0):
    """
    Test all motors in sequence to verify functionality
    
    Args:
        port (str): Serial port connected to Arduino (e.g., '/dev/ttyACM0')
        baud_rate (int): Baud rate for serial communication
        test_duration (float): Duration to run each motor test in seconds
        
    Returns:
        bool: True if test completed successfully, False otherwise
    """
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Connected to {port} at {baud_rate} baud")
        time.sleep(2)  # Wait for Arduino to reset
        
        print("\nTesting motors in sequence:")
        
        # Test front left motor
        print("Testing front left motor...")
        ser.write(b"100,0,0,0\n")
        time.sleep(test_duration)
        ser.write(b"0,0,0,0\n")
        time.sleep(0.5)
        
        # Test front right motor
        print("Testing front right motor...")
        ser.write(b"0,100,0,0\n")
        time.sleep(test_duration)
        ser.write(b"0,0,0,0\n")
        time.sleep(0.5)
        
        # Test rear left motor
        print("Testing rear left motor...")
        ser.write(b"0,0,100,0\n")
        time.sleep(test_duration)
        ser.write(b"0,0,0,0\n")
        time.sleep(0.5)
        
        # Test rear right motor
        print("Testing rear right motor...")
        ser.write(b"0,0,0,100\n")
        time.sleep(test_duration)
        ser.write(b"0,0,0,0\n")
        time.sleep(0.5)
        
        # Close the connection
        ser.close()
        print("\nMotor test completed successfully")
        return True
        
    except serial.SerialException as e:
        print(f"Error: {e}")
        return False

def calibrate_motor_speeds(port, baud_rate=9600):
    """
    Interactive calibration of motor speeds to ensure straight driving
    
    Args:
        port (str): Serial port connected to Arduino
        baud_rate (int): Baud rate for serial communication
        
    Returns:
        dict: Calibration values for each motor
    """
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Connected to {port} at {baud_rate} baud")
        time.sleep(2)  # Wait for Arduino to reset
        
        # Initialize with default values (100% power)
        calibration = {
            "front_left": 1.0,
            "front_right": 1.0,
            "rear_left": 1.0,
            "rear_right": 1.0
        }
        
        print("\nMotor Calibration")
        print("=================")
        print("This utility helps calibrate motors for straight driving.")
        print("Observe the robot's movement and adjust motor power as needed.")
        print("Enter values between 0.5 and 1.0 for each motor.")
        
        # Interactive calibration
        print("\nTesting forward movement...")
        ser.write(b"100,100,100,100\n")
        time.sleep(3)
        ser.write(b"0,0,0,0\n")
        
        # Collect calibration values
        for motor in calibration:
            value = input(f"Enter calibration for {motor} (0.5-1.0): ")
            try:
                cal_value = float(value)
                if 0.5 <= cal_value <= 1.0:
                    calibration[motor] = cal_value
                else:
                    print("Value out of range, using default 1.0")
            except ValueError:
                print("Invalid input, using default 1.0")
        
        # Test calibrated values
        fl = int(100 * calibration["front_left"])
        fr = int(100 * calibration["front_right"])
        rl = int(100 * calibration["rear_left"])
        rr = int(100 * calibration["rear_right"])
        
        print(f"\nTesting calibrated values: {fl},{fr},{rl},{rr}")
        ser.write(f"{fl},{fr},{rl},{rr}\n".encode())
        time.sleep(3)
        ser.write(b"0,0,0,0\n")
        
        ser.close()
        print("\nCalibration completed.")
        return calibration
        
    except serial.SerialException as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Example usage when run as script
    if len(sys.argv) < 2:
        print("Usage: python motor_utils.py <serial_port> [test|calibrate]")
        sys.exit(1)
        
    port = sys.argv[1]
    action = "test" if len(sys.argv) < 3 else sys.argv[2]
    
    if action == "test":
        test_motors(port)
    elif action == "calibrate":
        calibrate_motor_speeds(port)
    else:
        print(f"Unknown action: {action}")
        print("Valid actions: test, calibrate") 