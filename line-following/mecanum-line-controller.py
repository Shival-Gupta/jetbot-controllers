#!/usr/bin/env python3
"""
mecanum-line-controller.py
Version: 2.0

Description: Advanced controller for a line-following Mecanum robot.
Provides a full-featured interface with error handling, response reading,
and port configuration for controlling line following in both directions.

Compatible with:
  - mecanum-line-follower-basic.ino
  - mecanum-line-follower-advanced.ino

Original content follows:
"""

"""
Mecanum Line Follower Controller

This script provides a command-line interface to control a Mecanum wheel robot
over a serial connection. It supports 'forward'/'f', 'backward'/'b', and 'stop'/'s'
commands to make the robot follow a line.

Usage:
    python3 line_follower_controller.py [-p PORT] [-b BAUD]

Arguments:
    -p, --port    Serial port (default: /dev/ttyACM0)
    -b, --baud    Baud rate (default: 115200)

Controls:
    - 'forward' or 'f': Move robot forward along the line
    - 'backward' or 'b': Move robot backward along the line
    - 'stop' or 's': Stop the robot
    - 'exit': Quit the script
    - Ctrl+C: Exit gracefully
"""

import serial
import argparse
import time
import sys
from typing import Optional

class RobotController:
    """Manages serial communication with the robot."""
    
    def __init__(self, port: str, baud_rate: int):
        """Initialize the controller with serial port and baud rate."""
        self.port = port
        self.baud_rate = baud_rate
        self.serial: Optional[serial.Serial] = None

    def connect(self) -> bool:
        """Establish serial connection to the robot."""
        try:
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Allow Arduino to reset
            print(f"Connected to {self.port} at {self.baud_rate} baud")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")
            return False

    def send_command(self, command: str) -> None:
        """Send a command to the robot."""
        if self.serial and self.serial.is_open:
            try:
                # Map short commands to full commands
                command_map = {'f': 'forward', 'b': 'backward', 's': 'stop'}
                full_command = command_map.get(command, command)
                self.serial.write(f"{full_command}\n".encode('utf-8'))
                print(f"Sent: {full_command}")
            except serial.SerialException as e:
                print(f"Error sending command: {e}")
        else:
            print("Error: Not connected to robot")

    def close(self) -> None:
        """Close the serial connection."""
        if self.serial and self.serial.is_open:
            # Send stop command before closing to ensure robot halts
            self.serial.write("stop\n".encode('utf-8'))
            self.serial.close()
            print("Serial connection closed")

    def read_response(self) -> None:
        """Read and display response from the robot."""
        if self.serial and self.serial.in_waiting > 0:
            response = self.serial.readline().decode('utf-8').strip()
            if response:
                print(f"Robot: {response}")

def main():
    """Main function to run the controller."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Mecanum Line Follower Controller")
    parser.add_argument('-p', '--port', default='/dev/ttyACM0', help='Serial port (e.g., /dev/ttyACM0 or COM3)')
    parser.add_argument('-b', '--baud', type=int, default=115200, help='Baud rate (e.g., 115200)')
    args = parser.parse_args()

    # Initialize controller
    controller = RobotController(args.port, args.baud)
    if not controller.connect():
        sys.exit(1)

    # Display instructions
    print("\nAvailable commands:")
    print("  'forward' or 'f'  - Move forward along the line")
    print("  'backward' or 'b' - Move backward along the line")
    print("  'stop' or 's'     - Stop the robot")
    print("  'exit'            - Quit the script")
    print("  Ctrl+C            - Exit gracefully")
    print("----------------------------------------")

    try:
        while True:
            command = input("Enter command: ").strip().lower()
            if command == 'exit':
                break
            elif command in ['forward', 'f', 'backward', 'b', 'stop', 's']:
                controller.send_command(command)
                time.sleep(0.1)  # Brief delay to allow response
                controller.read_response()
            else:
                print("Invalid command. Use 'forward'/'f', 'backward'/'b', 'stop'/'s', or 'exit'")
    except KeyboardInterrupt:
        print("\nInterrupted by Ctrl+C")
        controller.close()  # Ensure clean exit on Ctrl+C
        sys.exit(0)
    finally:
        controller.close()  # Ensure connection is closed on normal exit

if __name__ == "__main__":
    main() 