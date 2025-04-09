#!/usr/bin/env python3
"""
line-follower-controller.py
Version: 1.0

Description: Simple controller for a line-following Mecanum robot.
Provides basic commands to start/stop line following in forward or backward directions.

Compatible with:
  - mecanum-line-follower-basic.ino
  - mecanum-line-follower-advanced.ino

Original content follows:
"""

import serial
import time

# Serial port configuration
SERIAL_PORT = "/dev/ttyACM0"  # Adjust as needed (e.g., "/dev/ttyUSB0")
BAUD_RATE = 115200            # Matches Arduino's baud rate

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        print(f"Connected to Arduino on {SERIAL_PORT}")
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    print("Commands: 'f' or 'forward' (move forward), 'b' or 'backward' (move backward), 's' or 'stop' (stop)")
    print("Type 'exit' to quit")

    command_map = {
        "f": "forward",
        "b": "backward",
        "s": "stop",
        "forward": "forward",
        "backward": "backward",
        "stop": "stop"
    }

    while True:
        cmd = input("Enter command: ").strip().lower()
        if cmd == "exit":
            break
        if cmd in command_map:
            ser.write((command_map[cmd] + "\n").encode())
            print(f"Sent: {command_map[cmd]}")
        else:
            print("Invalid command")

    ser.close()
    print("Serial connection closed")

if __name__ == "__main__":
    main() 