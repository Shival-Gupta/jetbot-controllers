# Mecanum Robot Web Interface Summary

## Overview
The Mecanum Robot Web Interface consists of several Python components that provide remote control and monitoring capabilities for a Mecanum wheeled robot. The system uses web-based interfaces for control and video streaming, making it accessible from any device with a web browser.

## Key Components

### 1. Flask-based Robot Controller (`flask-controller.py`)
- **Purpose**: Provides a web interface for controlling the Mecanum robot remotely
- **Features**:
  - Mobile-friendly touch controls via HTML interface
  - Real-time command execution via serial communication
  - Visual feedback and modern UI layout
- **Technical Details**:
  - Uses Flask web framework to serve HTTP requests
  - Communicates with Arduino via serial port (default: /dev/ttyACM0 at 115200 baud)
  - Command mapping for various robot movements (forward, backward, left, right, rotate)
  - Runs on port 5000 by default

### 2. OpenCV-based Webcam Streamer (`webcam_steam.py`)
- **Purpose**: Streams live video from a webcam to a web browser
- **Features**:
  - Low-latency MJPEG streaming
  - Automatic port selection
  - Configurable resolution and frame rate
- **Technical Details**:
  - Uses OpenCV for camera frame capture
  - Multi-threaded design with separate camera and HTTP handler threads
  - Implements MJPEG streaming via HTTP
  - Runs on port 8000 by default with configurable parameters

### 3. FFmpeg-based Webcam Streamer (`webcam-streamer.py`)
- **Purpose**: Alternative implementation using FFmpeg for webcam streaming
- **Features**:
  - More efficient CPU usage compared to OpenCV version
  - Better handling of various camera types
- **Technical Details**:
  - Uses FFmpeg as a separate process for video processing
  - Implements a queue-based approach for stream data handling
  - Runs on port 6000 by default

## Integration
- The components are designed to work independently but can be combined for a complete remote robot operation experience
- Users can run both the webcam streamer and controller simultaneously on the same machine
- The web interfaces can be accessed from any device on the same network
- Hardware requirements include a webcam, computer running Python 3.6+, and network connection

## Usage
- Start the webcam stream with `python webcam_steam.py` (or the FFmpeg version)
- Launch the controller with `python flask-controller.py`
- Access the interfaces via web browser at the appropriate IP addresses and ports
- Control the robot while viewing the live video feed 