import serial
import time

# Serial port configuration
SERIAL_PORT = "/dev/ttyACM0"  # Adjust as needed
BAUD_RATE = 9600
MOVE_DURATION = 2  # Movement duration in seconds
DEFAULT_SPEED = 150

# Motor control mappings
COMMANDS = {
    'w': [DEFAULT_SPEED, DEFAULT_SPEED, DEFAULT_SPEED, DEFAULT_SPEED],     # Forward
    's': [-DEFAULT_SPEED, -DEFAULT_SPEED, -DEFAULT_SPEED, -DEFAULT_SPEED], # Backward
    'a': [-DEFAULT_SPEED, DEFAULT_SPEED, DEFAULT_SPEED, -DEFAULT_SPEED],   # Strafe Left
    'd': [DEFAULT_SPEED, -DEFAULT_SPEED, -DEFAULT_SPEED, DEFAULT_SPEED],   # Strafe Right
    'q': [DEFAULT_SPEED, -DEFAULT_SPEED, DEFAULT_SPEED, -DEFAULT_SPEED],   # Rotate Left
    'e': [-DEFAULT_SPEED, DEFAULT_SPEED, -DEFAULT_SPEED, DEFAULT_SPEED],   # Rotate Right
    'z': [0, DEFAULT_SPEED, DEFAULT_SPEED, 0],         # Diagonal Forward Left
    'x': [DEFAULT_SPEED, 0, 0, DEFAULT_SPEED],         # Diagonal Forward Right
    'c': [0, -DEFAULT_SPEED, -DEFAULT_SPEED, 0],      # Diagonal Backward Left
    'v': [-DEFAULT_SPEED, 0, 0, -DEFAULT_SPEED],      # Diagonal Backward Right
    'stop': [0, 0, 0, 0]                              # Stop
}

# Calibration test sequence
def calibration_test(ser):
    for i in range(4):
        speeds = [0, 0, 0, 0]
        speeds[i] = DEFAULT_SPEED
        send_command(ser, speeds)
        time.sleep(MOVE_DURATION)
        send_command(ser, [0, 0, 0, 0])
        time.sleep(1)
    print("Calibration test complete.")

# Send command to Arduino
def send_command(ser, speeds):
    cmd = ",".join(map(str, speeds)) + "\n"
    ser.write(cmd.encode('utf-8'))
    print(f"Sent command: {cmd.strip()}")

# Main function
def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow Arduino to reset
        print("Connected to Arduino.")
    except serial.SerialException as e:
        print("Error opening serial port:", e)
        return

    print("Enter a command (w, s, a, d, q, e, z, x, c, v, stop, calib, exit):")
    
    while True:
        command = input("> ").strip().lower()
        if command == "exit":
            break
        elif command == "calib":
            calibration_test(ser)
        elif command in COMMANDS:
            send_command(ser, COMMANDS[command])
            time.sleep(MOVE_DURATION)
            send_command(ser, COMMANDS['stop'])
        else:
            print("Invalid command.")
    
    ser.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()
