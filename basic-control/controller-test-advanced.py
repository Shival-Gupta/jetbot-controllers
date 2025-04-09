#!/usr/bin/env python3
"""
controller-test-advanced.py
Version: 2.0

Description: Advanced test controller for a 4-wheel Mecanum robot. Provides comprehensive
movement options including diagonal and curved motion patterns through serial commands.

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

# Movement duration (seconds)
MOVE_DURATION = 2  # Change this value if you want a different duration

# Define motor commands for each type of motion.
# Motor order: [Front Left, Front Right, Rear Left, Rear Right]
COMMANDS = {
    'w': [150, 150, 150, 150],     # Forward
    's': [-150, -150, -150, -150], # Backward
    'a': [-150, 150, 150, -150],   # Strafe Left
    'd': [150, -150, -150, 150],   # Strafe Right
    'q': [150, -150, 150, -150],   # Rotate Left (In-Place)
    'e': [-150, 150, -150, 150],   # Rotate Right (In-Place)
    'z': [0, 150, 150, 0],         # Diagonal Forward Left
    'x': [150, 0, 0, 150],         # Diagonal Forward Right
    'c': [0, -150, -150, 0],       # Diagonal Backward Left
    'v': [-150, 0, 0, -150],       # Diagonal Backward Right
    'r': [225, 75, 225, 75],       # Curved Forward Left (Forward + slight left rotation)
    't': [75, 225, 75, 225],       # Curved Forward Right (Forward + slight right rotation)
    'f': [-75, -225, -75, -225],   # Curved Backward Left (Backward + slight left rotation)
    'g': [-225, -75, -225, -75]    # Curved Backward Right (Backward + slight right rotation)
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
    print("  a - Strafe Left")
    print("  d - Strafe Right")
    print("  q - Rotate Left (In-Place)")
    print("  e - Rotate Right (In-Place)")
    print("  z - Diagonal Forward Left")
    print("  x - Diagonal Forward Right")
    print("  c - Diagonal Backward Left")
    print("  v - Diagonal Backward Right")
    print("  r - Curved Forward Left")
    print("  t - Curved Forward Right")
    print("  f - Curved Backward Left")
    print("  g - Curved Backward Right")
    print("Type 'exit' to quit.")

    while True:
        direction = input("Enter command: ").strip().lower()
        if direction == "exit":
            break

        if direction in COMMANDS:
            # Send the movement command
            send_command(ser, COMMANDS[direction])
            # Keep the motors running for MOVE_DURATION seconds
            time.sleep(MOVE_DURATION)
            # Send stop command (all motors off)
            send_command(ser, [0, 0, 0, 0])
        else:
            print("Invalid command. Please enter one of the valid commands.")

    ser.close()
    print("Serial connection closed. Exiting...")

if __name__ == "__main__":
    main() 