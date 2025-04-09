#!/usr/bin/env python3
import serial
import time

def open_serial(port='/dev/ttyACM0', baud_rate=9600):
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)  # Allow time for the Arduino to reset
        print(f"Connected to {port} at {baud_rate} baud.")
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port {port}: {e}")
        exit(1)

def send_command(ser, command_str):
    """Send a command (e.g., "100,-100,100,-100") to the board."""
    command = command_str.strip() + "\n"
    ser.write(command.encode())
    print(f"Sent: {command_str}")

def read_serial(ser):
    """Read and print any messages available from the board."""
    while ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print("Board:", line)

def print_menu():
    print("\nSelect a command to send:")
    print("1.  Forward              (100,100,100,100)")
    print("2.  Backward             (-100,-100,-100,-100)")
    print("3.  Strafe Left          (-100,100,100,-100)")
    print("4.  Strafe Right         (100,-100,-100,100)")
    print("5.  Rotate Clockwise     (100,-100,100,-100)")
    print("6.  Rotate CounterClock  (-100,100,-100,100)")
    print("7.  Diagonal Forward Left  (100,0,0,100)")
    print("8.  Diagonal Forward Right (0,100,100,0)")
    print("9.  Diagonal Backward Left (-100,0,0,-100)")
    print("10. Diagonal Backward Right(0,-100,-100,0)")
    print("11. Stop                 (0,0,0,0)")
    print("12. Custom command")
    print("13. Read board messages")
    print("14. Exit")

def main():
    ser = open_serial()
    while True:
        print_menu()
        choice = input("Enter your choice (1-14): ").strip()
        if choice == "1":
            command = "100,100,100,100"
        elif choice == "2":
            command = "-100,-100,-100,-100"
        elif choice == "3":
            command = "-100,100,100,-100"
        elif choice == "4":
            command = "100,-100,-100,100"
        elif choice == "5":
            command = "100,-100,100,-100"
        elif choice == "6":
            command = "-100,100,-100,100"
        elif choice == "7":
            command = "100,0,0,100"
        elif choice == "8":
            command = "0,100,100,0"
        elif choice == "9":
            command = "-100,0,0,-100"
        elif choice == "10":
            command = "0,-100,-100,0"
        elif choice == "11":
            command = "0,0,0,0"
        elif choice == "12":
            custom = input("Enter custom speeds as comma-separated values (e.g., 50,-50,50,-50): ")
            parts = custom.split(',')
            if len(parts) != 4:
                print("Invalid format. Please enter exactly 4 comma-separated numbers.")
                continue
            command = custom.strip()
        elif choice == "13":
            print("Reading messages from board:")
            read_serial(ser)
            continue
        elif choice == "14":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
            continue

        send_command(ser, command)
        # Give the board a moment to respond and then read any output.
        time.sleep(0.1)
        read_serial(ser)
        
    ser.close()

if __name__ == "__main__":
    main()
