#!/usr/bin/env python3
"""
Enhanced Mecanum Robot Controller Interface

This script provides a user-friendly interface to control a mecanum wheel robot
with drift correction capability. It sends commands to an Arduino running the
corresponding firmware via serial communication.

Features:
- Intuitive keyboard control interface with preset movement patterns.
- Continuous (hold) movement mode.
- Real-time status feedback from the robot.
- Configurable movement parameters (speed, duration).
- Calibration test to drive each motor individually.
- Custom command entry.

Usage:
  python mecanum_controller.py [-p PORT] [-s SPEED] [-d DURATION]

Author: Combined Example
Version: 2.0
"""

import argparse
import serial
import sys
import time
import threading

# =================== Configuration =================== #
DEFAULT_SERIAL_PORT = "/dev/ttyACM0"  # Adjust for your system (e.g., "COM3" on Windows)
DEFAULT_BAUD_RATE = 9600
DEFAULT_MOVE_DURATION = 2.0       # Default duration for momentary movements (seconds)
DEFAULT_MOTOR_SPEED = 150         # Default speed value (0-255)
SERIAL_TIMEOUT = 1.0              # Serial read timeout
CONNECTION_RETRIES = 3            # Number of connection attempts

# =================== Command Definitions =================== #
# Each command defines the speeds for [Front Left, Front Right, Rear Left, Rear Right]
# Positive values move forward/right, negative values move backward/left.
class Commands:
    def __init__(self, speed=DEFAULT_MOTOR_SPEED):
        self.speed = speed
        self.update_commands()
        
    def update_commands(self):
        """Update all commands based on current speed setting."""
        self.COMMANDS = {
            # Basic movements (with drift correction for forward/backward)
            'w': [self.speed, self.speed, self.speed, self.speed],           # Forward
            's': [-self.speed, -self.speed, -self.speed, -self.speed],        # Backward
            'a': [-self.speed, self.speed, self.speed, -self.speed],          # Strafe Left
            'd': [self.speed, -self.speed, -self.speed, self.speed],          # Strafe Right,
            
            # Rotational movements
            'q': [self.speed, -self.speed, self.speed, -self.speed],          # Rotate Left (CCW)
            'e': [-self.speed, self.speed, -self.speed, self.speed],          # Rotate Right (CW)
            
            # Diagonal movements
            'z': [0, self.speed, self.speed, 0],                              # Diagonal Forward Left
            'x': [self.speed, 0, 0, self.speed],                              # Diagonal Forward Right
            'c': [0, -self.speed, -self.speed, 0],                            # Diagonal Backward Left
            'v': [-self.speed, 0, 0, -self.speed],                            # Diagonal Backward Right
            
            # Curved movements
            'r': [int(self.speed * 1.5), int(self.speed * 0.5),
                  int(self.speed * 1.5), int(self.speed * 0.5)],              # Curved Forward Left
            't': [int(self.speed * 0.5), int(self.speed * 1.5),
                  int(self.speed * 0.5), int(self.speed * 1.5)],              # Curved Forward Right
            'f': [-int(self.speed * 0.5), -int(self.speed * 1.5),
                  -int(self.speed * 0.5), -int(self.speed * 1.5)],            # Curved Backward Left
            'g': [-int(self.speed * 1.5), -int(self.speed * 0.5),
                  -int(self.speed * 1.5), -int(self.speed * 0.5)]             # Curved Backward Right
        }
        # Add stop command
        self.COMMANDS['stop'] = [0, 0, 0, 0]

    def get_speed(self):
        """Return the current speed setting."""
        return self.speed
        
    def set_speed(self, new_speed):
        """Update the speed setting and recalculate commands."""
        self.speed = max(0, min(255, new_speed))
        self.update_commands()
        return self.speed
        
    def increase_speed(self, increment=10):
        """Increase speed by the specified increment."""
        return self.set_speed(self.speed + increment)
        
    def decrease_speed(self, decrement=10):
        """Decrease speed by the specified decrement."""
        return self.set_speed(self.speed - decrement)

# =================== Robot Controller Class =================== #
class RobotController:
    """Manages communication with the robot and executes movement commands."""
    
    def __init__(self, port=DEFAULT_SERIAL_PORT, baud_rate=DEFAULT_BAUD_RATE, 
                 move_duration=DEFAULT_MOVE_DURATION, speed=DEFAULT_MOTOR_SPEED):
        self.port = port
        self.baud_rate = baud_rate
        self.move_duration = move_duration
        self.serial_connection = None
        self.commands = Commands(speed)
        self.is_connected = False
        self.hold_active = False
        self.lock = threading.Lock()
        
    def connect(self):
        """Establish a serial connection to the robot."""
        for attempt in range(CONNECTION_RETRIES):
            try:
                if self.serial_connection:
                    self.serial_connection.close()
                
                self.serial_connection = serial.Serial(
                    self.port, 
                    self.baud_rate,
                    timeout=SERIAL_TIMEOUT
                )
                # Allow Arduino to reset
                time.sleep(2)
                self.serial_connection.reset_input_buffer()
                self.serial_connection.reset_output_buffer()
                
                self.is_connected = True
                print(f"Connected to robot on {self.port}")
                return True
            except serial.SerialException as e:
                print(f"Connection attempt {attempt+1}/{CONNECTION_RETRIES} failed: {str(e)}")
                time.sleep(1)
        print(f"Failed to connect to robot on {self.port}")
        return False
        
    def disconnect(self):
        """Stop motors and close the serial connection."""
        if self.serial_connection:
            self.stop()
            time.sleep(0.1)
            self.serial_connection.close()
            self.is_connected = False
            print("Disconnected from robot")
            
    def send_command(self, speeds):
        """Send a motor speed command to the robot."""
        if not self.is_connected:
            print("Error: Not connected to robot")
            return False
        try:
            with self.lock:
                command = ",".join(map(str, speeds)) + "\n"
                self.serial_connection.write(command.encode('utf-8'))
                self.serial_connection.flush()
                self._read_response()
                return True
        except Exception as e:
            print(f"Error sending command: {str(e)}")
            self.is_connected = False
            return False
            
    def _read_response(self):
        """Read and display any response from the robot (non-blocking)."""
        try:
            response = self.serial_connection.readline().decode('utf-8').strip()
            if response:
                print(f"Robot: {response}")
        except Exception:
            pass
            
    def move(self, direction):
        """Execute a movement in the specified direction."""
        if direction not in self.commands.COMMANDS:
            print(f"Unknown direction: {direction}")
            return False
        motor_speeds = self.commands.COMMANDS[direction]
        return self.send_command(motor_speeds)
        
    def move_for_duration(self, direction):
        """Move in the specified direction for the set duration then stop."""
        if not self.move(direction):
            return False
        time.sleep(self.move_duration)
        return self.stop()
        
    def start_hold(self, direction):
        """Start continuous movement in the specified direction until stopped."""
        if self.hold_active:
            self.stop()
        if direction not in self.commands.COMMANDS:
            print(f"Unknown direction for hold: {direction}")
            return False
        print(f"Holding {direction} direction. Enter 'stop' to halt.")
        self.hold_active = True
        return self.move(direction)
        
    def stop(self):
        """Stop all motors."""
        self.hold_active = False
        return self.send_command(self.commands.COMMANDS['stop'])
        
    def set_speed(self, speed):
        """Update the movement speed and refresh commands."""
        new_speed = self.commands.set_speed(speed)
        print(f"Speed set to {new_speed}")
        return new_speed
        
    def increase_speed(self):
        """Increase the movement speed."""
        new_speed = self.commands.increase_speed()
        print(f"Speed increased to {new_speed}")
        return new_speed
        
    def decrease_speed(self):
        """Decrease the movement speed."""
        new_speed = self.commands.decrease_speed()
        print(f"Speed decreased to {new_speed}")
        return new_speed
        
    def set_move_duration(self, duration):
        """Update the movement duration."""
        self.move_duration = max(0.1, duration)
        print(f"Movement duration set to {self.move_duration:.1f} seconds")
        
    def calibration_test(self):
        """Run a calibration test by sequentially driving each motor individually."""
        print("Starting calibration test...")
        for i in range(4):
            speeds = [0, 0, 0, 0]
            speeds[i] = self.commands.get_speed()
            self.send_command(speeds)
            time.sleep(self.move_duration)
            self.send_command(self.commands.COMMANDS['stop'])
            time.sleep(0.5)
        print("Calibration test complete.")

# =================== Serial Reader Thread =================== #
def read_serial(ser, stop_event):
    """Continuously read and print any messages from the robot."""
    while not stop_event.is_set():
        if ser.in_waiting:
            try:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                if line:
                    print("Robot:", line)
            except Exception:
                pass
        time.sleep(0.1)

# =================== User Interface =================== #
def print_help():
    """Display available command help."""
    help_text = """
Mecanum Robot Controller Commands:
----------------------------------
Movement Controls:
  w - Forward (drift-corrected)
  s - Backward (drift-corrected)
  a - Strafe Left
  d - Strafe Right
  q - Rotate Left (CCW)
  e - Rotate Right (CW)

Diagonal Movement:
  z - Diagonal Forward Left
  x - Diagonal Forward Right
  c - Diagonal Backward Left
  v - Diagonal Backward Right

Curved Movement:
  r - Curved Forward Left
  t - Curved Forward Right
  f - Curved Backward Left
  g - Curved Backward Right

Special Commands:
  hold <direction>   - Hold continuous movement (e.g., hold w)
  stop               - Stop all motors
  calib              - Run calibration test (drive each motor individually)
  speed <value>      - Set motor speed (0-255)
  + or up           - Increase speed
  - or down         - Decrease speed
  duration <sec>     - Set movement duration in seconds
  help               - Show this help message
  exit/quit          - Exit program
"""
    print(help_text)

def interactive_mode(controller):
    """Run the interactive command interface."""
    print_help()
    print(f"\nCurrent settings: Speed={controller.commands.get_speed()}, Duration={controller.move_duration:.1f}s")
    print("Enter command (or 'help' for options):")
    
    while True:
        try:
            user_input = input("> ").strip().lower()
            if not user_input:
                continue
            if user_input in ("exit", "quit"):
                break
            elif user_input == "help":
                print_help()
            elif user_input.startswith("hold"):
                parts = user_input.split()
                if len(parts) < 2:
                    print("Usage: hold <direction>")
                else:
                    controller.start_hold(parts[1])
            elif user_input == "stop":
                controller.stop()
                print("Motors stopped.")
            elif user_input.startswith("speed"):
                parts = user_input.split()
                if len(parts) < 2:
                    print("Usage: speed <value>")
                else:
                    try:
                        value = int(parts[1])
                        controller.set_speed(value)
                    except ValueError:
                        print("Invalid speed value.")
            elif user_input in ("+", "up"):
                controller.increase_speed()
            elif user_input in ("-", "down"):
                controller.decrease_speed()
            elif user_input.startswith("duration"):
                parts = user_input.split()
                if len(parts) < 2:
                    print("Usage: duration <seconds>")
                else:
                    try:
                        dur = float(parts[1])
                        controller.set_move_duration(dur)
                    except ValueError:
                        print("Invalid duration value.")
            elif user_input == "calib":
                controller.calibration_test()
            elif user_input in controller.commands.COMMANDS:
                # Execute momentary movement: move for the set duration then stop.
                controller.move_for_duration(user_input)
            else:
                print("Unknown command. Type 'help' for available options.")
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt received. Exiting interactive mode.")
            break

# =================== Main Function =================== #
def main():
    parser = argparse.ArgumentParser(description="Mecanum Robot Controller")
    parser.add_argument("-p", "--port", default=DEFAULT_SERIAL_PORT, help="Serial port to use (default: /dev/ttyACM0)")
    parser.add_argument("-s", "--speed", type=int, default=DEFAULT_MOTOR_SPEED, help="Default motor speed (0-255)")
    parser.add_argument("-d", "--duration", type=float, default=DEFAULT_MOVE_DURATION, help="Movement duration in seconds")
    args = parser.parse_args()

    controller = RobotController(port=args.port, baud_rate=DEFAULT_BAUD_RATE, move_duration=args.duration, speed=args.speed)
    
    if not controller.connect():
        sys.exit(1)
        
    # Start a background thread to continuously read robot responses.
    stop_event = threading.Event()
    reader_thread = threading.Thread(target=read_serial, args=(controller.serial_connection, stop_event), daemon=True)
    reader_thread.start()
    
    try:
        interactive_mode(controller)
    finally:
        stop_event.set()
        reader_thread.join()
        controller.disconnect()
        
if __name__ == "__main__":
    main()
