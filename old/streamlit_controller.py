import serial
import time
from flask import Flask, render_template, request

# Serial port configuration
SERIAL_PORT = "/dev/ttyACM0"  # Adjust as needed (e.g., "/dev/ttyUSB0")
BAUD_RATE = 115200  # Matches Arduino's baud rate

app = Flask(__name__)

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for Arduino to initialize
    print(f"Connected to Arduino on {SERIAL_PORT}")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    ser = None

def send_command(command):
    if ser and ser.is_open:
        ser.write((command + "\n").encode())
        print(f"Sent: {command}")

@app.route('/')
def index():
    return '''
    <html>
    <head>
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
        <h1>Arduino Remote Control</h1>
        <button onmousedown="sendCommand('forward')" onmouseup="sendCommand('stop')">Forward</button>
        <button onmousedown="sendCommand('backward')" onmouseup="sendCommand('stop')">Backward</button>
    </body>
    </html>
    '''

@app.route('/control', methods=['POST'])
def control():
    command = request.form.get('command')
    send_command(command)
    return '', 204  # No content response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6600)
