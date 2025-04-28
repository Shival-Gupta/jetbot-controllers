#!/usr/bin/env python3
"""
flask-controller.py
Version: 1.0

Description: Web-based interface for controlling a Mecanum robot using Flask.
Provides a simple HTML interface with buttons for remote control operations.

Compatible with:
  - All Mecanum robot Arduino firmware files
  - Can be used alongside webcam streaming
"""

import serial
import time
from flask import Flask, render_template, request

# Serial port configuration
SERIAL_PORT = "/dev/ttyACM0"  # Adjust as needed (e.g., "/dev/ttyUSB0" or "COM3" on Windows)
BAUD_RATE = 115200  # Matches Arduino's baud rate

app = Flask(__name__)

# Initialize serial connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for Arduino to initialize
    print(f"Connected to Arduino on {SERIAL_PORT}")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    ser = None

def send_command(command):
    """
    Send a command to the Arduino via serial
    
    Args:
        command: String command to send to the Arduino
    """
    if ser and ser.is_open:
        try:
            ser.write((command + "\n").encode())
            print(f"Sent: {command}")
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    else:
        print("Serial port not connected")
        return False

@app.route('/')
def index():
    """
    Render the main control interface
    """
    return '''
    <html>
    <head>
        <title>Mecanum Robot Control</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin: 20px;
            }
            .control-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
                margin: 20px auto;
                max-width: 300px;
            }
            button {
                padding: 15px;
                font-size: 18px;
                cursor: pointer;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            button:active {
                background-color: #3e8e41;
            }
            .stop-button {
                grid-column: span 3;
                background-color: #f44336;
            }
            .stop-button:active {
                background-color: #d32f2f;
            }
        </style>
        <script>
            function sendCommand(command) {
                fetch('/control', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'command=' + command
                });
            }
        </script>
    </head>
    <body>
        <h1>Mecanum Robot Control</h1>
        
        <div class="control-grid">
            <!-- Directional controls -->
            <button onmousedown="sendCommand('forward')" onmouseup="sendCommand('stop')">↑</button>
            <button onmousedown="sendCommand('backward')" onmouseup="sendCommand('stop')">↓</button>
            <button onmousedown="sendCommand('right')" onmouseup="sendCommand('stop')">→</button>
            <button onmousedown="sendCommand('left')" onmouseup="sendCommand('stop')">←</button>
            
            <!-- Rotation controls -->
            <button onmousedown="sendCommand('rotate_left')" onmouseup="sendCommand('stop')">↺</button>
            <button onmousedown="sendCommand('rotate_right')" onmouseup="sendCommand('stop')">↻</button>
            
            <!-- Stop button -->
            <button class="stop-button" onclick="sendCommand('stop')">STOP</button>
        </div>
    </body>
    </html>
    '''

@app.route('/control', methods=['POST'])
def control():
    """
    Handle control commands from the web interface
    """
    command = request.form.get('command')
    send_command(command)
    return '', 204  # No content response

# Command mapping for different control systems
# These can be adjusted based on the specific Arduino firmware being used
COMMAND_MAP = {
    'forward': 'forward',       # For advanced firmware
    'backward': 'backward',     # For advanced firmware
    'left': 'left',             # For advanced firmware
    'right': 'right',           # For advanced firmware
    'rotate_left': 'rotate_left',
    'rotate_right': 'rotate_right',
    'stop': 'stop'
}

if __name__ == "__main__":
    print("Starting Flask web server...")
    print("Access the control panel at http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=6500) 
