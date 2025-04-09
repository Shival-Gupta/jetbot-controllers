#!/usr/bin/env python3
"""
controller-test-basic.py
Version: 1.0

Description: Basic test controller for a 4-wheel Mecanum robot. Provides simple
forward, backward, left, and right movement controls through serial commands.

Compatible with:
  - mecanum-basic-controller.ino
  - mecanum-advanced-controller.ino

Original content follows:
"""

import serial
import time

# Serial port configuration
SERIAL_PORT = "/dev/ttyACM0"  # Adjust for your system (e.g., "COM3" on Windows)
BAUD_RATE = 9600

# Define motor commands for each direction.
# These values are examples; adjust them according to your robot's motor configuration.
COMMANDS = {
    'w': [150, 150, 150, 150],   # Forward
    's': [-150, -150, -150, -150],# Backward
    'a': [-150, 150, -150, 150],  # Strafe left
    'd': [150, -150, 150, -150]   # Strafe right
}

def send_command(ser, speeds):
    """
    Format and send a command to the Arduino.
    :param ser: The serial connection.
    :param speeds: List of 4 integers representing motor speeds.
    """
    cmd = ",".join(str(s) for s in speeds) + "\n"
    ser.write(cmd.encode('utf-8'))
    print("Sent command:", cmd.strip())

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow time for the Arduino to reset
        print("Connected to Arduino on", SERIAL_PORT)
    except serial.SerialException as e:
        print("Error opening serial port:", e)
        return

    print("Enter a direction command:")
    print("  w - Forward")
    print("  s - Backward")
    print("  a - Left")
    print("  d - Right")
    print("Type 'exit' to quit.")

    while True:
        direction = input("Enter command: ").strip().lower()
        if direction == "exit":
            break

        if direction in COMMANDS:
            # Send the movement command
            send_command(ser, COMMANDS[direction])
            # Keep the motors running for 2 seconds
            time.sleep(2)
            # Send stop command (all motors off)
            send_command(ser, [0, 0, 0, 0])
        else:
            print("Invalid command. Please enter w, a, s, d, or exit.")

    ser.close()
    print("Serial connection closed. Exiting...")

if __name__ == "__main__":
    main() 