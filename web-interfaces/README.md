# Mecanum Robot Web Interfaces

This directory contains web-based interfaces for remote monitoring and control of the Mecanum robot.

## Components

- **Python Streaming Server:**
  - `webcam-streamer.py` - FFmpeg-based webcam streaming server with web interface

- **Web Control Interfaces:**
  - `flask-controller.py` - Flask-based web interface for robot control

## Features

### Webcam Streaming Server
- Live video feed via web browser
- Automatic port selection
- Cross-platform compatibility
- Mobile-friendly responsive interface
- Compatible with all robot control systems
- Low-latency MJPEG streaming
- Efficient CPU usage with FFmpeg

### Flask Controller
- Web-based control interface
- Mobile-friendly touch controls
- Real-time command execution
- Visual feedback with modern UI
- Works on any browser/device
- Serial communication with robot

## Hardware Requirements

- Webcam (USB or built-in)
- Computer running Python 3.6+
- Network connection for remote viewing
- FFmpeg installed on the system
- Arduino-based robot connected via USB

## Dependencies

The web interfaces require:
- flask>=2.0.0
- pyserial>=3.5
- FFmpeg (system dependency)

All Python dependencies are listed in the root `requirements.txt` file.

## Usage

### Starting the Webcam Stream

1. Ensure your webcam is connected and FFmpeg is installed
2. Run the streaming server:
   ```bash
   python webcam-streamer.py
   ```
   or with options:
   ```bash
   python webcam-streamer.py --port 8080 --device 0 --width 1280 --height 720
   ```

3. Access the stream in a web browser at:
   ```
   http://<your-ip-address>:<port>
   ```
   
### Using the Web Controller

1. Connect your Arduino-based robot to the computer
2. Run the Flask controller:
   ```bash
   python flask-controller.py
   ```
3. Access the control interface in a browser at:
   ```
   http://<your-ip-address>:5000
   ```
4. Use the on-screen buttons to control the robot
   
### Command Line Options

#### Webcam Streaming
- `--port` - Starting port number (default: 6000)
- `--device` - Camera device index (default: 0)
- `--width` - Video width in pixels (default: 640)
- `--height` - Video height in pixels (default: 480)
- `--fps` - Frames per second (default: 25)

## Implementation Details

The webcam streaming implementation uses FFmpeg for efficient video processing:
- FFmpeg handles camera capture and encoding
- MJPEG streaming for low-latency video
- Automatic port selection if default port is in use
- Queue-based approach for stream data handling

## Integration with Robot Control

The web interfaces are designed to work together:
1. Start the webcam streamer first
2. Start the Flask controller
3. Access both interfaces in your web browser
4. Control the robot while viewing the live video feed

## Troubleshooting

1. **Webcam not detected:**
   - Check if FFmpeg is installed
   - Verify webcam is connected and recognized by the system
   - Try different device indices (0, 1, 2, etc.)

2. **Serial port issues:**
   - Check if the robot is connected
   - Verify the correct port name in `flask-controller.py`
   - Ensure no other program is using the serial port

3. **Streaming issues:**
   - Check if the port is available
   - Verify network connectivity
   - Ensure sufficient system resources 