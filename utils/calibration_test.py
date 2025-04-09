#!/usr/bin/env python3
"""
Calibration test utility for Mecanum robot motors.
Run this script to individually test each motor and verify proper connections.
"""

import serial
import time
import sys

# Serial port configuration
DEFAULT_PORT = "/dev/ttyACM0"  # Adjust as needed
BAUD_RATE = 9600
TEST_DURATION = 2  # Movement duration in seconds
DEFAULT_SPEED = 150

def calibration_test(ser):
    """
    Run a calibration test sequence that activates each motor individually.
    Allows verification of motor connections and direction.
    
    Args:
        ser: Serial connection to Arduino
    """
    print("\nRunning motor calibration test sequence...")
    print("Each motor will run for {} seconds in sequence.".format(TEST_DURATION))
    
    motor_names = ["Front Left", "Front Right", "Rear Left", "Rear Right"]
    
    for i in range(4):
        print("\nTesting {} motor...".format(motor_names[i]))
        speeds = [0, 0, 0, 0]
        speeds[i] = DEFAULT_SPEED
        send_command(ser, speeds)
        time.sleep(TEST_DURATION)
        send_command(ser, [0, 0, 0, 0])
        time.sleep(1)
    
    print("\nCalibration test complete.")

def send_command(ser, speeds):
    """
    Send a command to the Arduino.
    
    Args:
        ser: Serial connection to Arduino
        speeds: List of 4 integers representing motor speeds
    """
    cmd = ",".join(map(str, speeds)) + "\n"
    ser.write(cmd.encode('utf-8'))
    print(f"Sent command: {cmd.strip()}")

def main():
    """Main function to run the calibration test."""
    # Get serial port from command line or use default
    port = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PORT
    
    print("Motor Calibration Utility")
    print("========================")
    print("This utility helps verify motor connections.")
    print("Each motor will be activated in sequence.")
    
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow Arduino to reset
        print(f"Connected to Arduino on {port}.")
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return
    
    try:
        calibration_test(ser)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        send_command(ser, [0, 0, 0, 0])  # Ensure motors are stopped
        ser.close()
        print("Connection closed.")

if __name__ == "__main__":
    main() 