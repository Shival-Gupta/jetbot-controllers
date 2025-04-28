# Mecanum Robot Control System

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.6%2B-blue" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" alt="Status">
</div>

<div align="center">
  <h3>🚀 A comprehensive robotics project featuring a Mecanum wheel robot with advanced control capabilities</h3>
</div>

## 📑 Table of Contents
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Documentation](#-documentation)
- [System Components](#-system-components)
- [Setup](#-setup)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

## 🚀 Features

### Advanced Movement Control
- Omnidirectional movement using Mecanum wheels
- IMU (MPU6050) integration for drift correction
- PID-based control system
- Web interface control
- Line following capabilities

### Control Interfaces
- Web interface (Flask)
- Webcam streaming
- Custom command entry

### Advanced Features
- Drift correction using IMU
- Line following with IR sensors
- Multiple movement patterns
- Configurable speed and duration
- Real-time status feedback

## 📁 Project Structure

```
.
├── web-interfaces/          # Web-based control and monitoring
│   ├── flask-controller.py  # Flask-based web interface for robot control
│   ├── webcam-streamer.py   # FFmpeg-based webcam streaming server
│   └── README.md           # Web interfaces documentation
├── utils/                  # Utility scripts and helper functions
│   ├── sensor_utils.py     # Sensor calibration and testing
│   ├── motor_utils.py      # Motor testing and calibration
│   ├── calibration_test.py # Motor calibration utility
│   └── README.md          # Utilities documentation
├── line-following/         # Line following implementation
├── imu-control/           # IMU-based control implementation
├── basic-control/         # Basic control implementation
├── requirements.txt       # Python dependencies
└── README.MD             # This file
```

## 📖 Documentation

### Quick Links
- [Main Documentation](README.MD) - Overview of the Mecanum Robot Control System
- [Web Interfaces Documentation](web-interfaces/README.md) - Guide for web-based control
- [Utilities Documentation](utils/README.md) - Guide for sensor and motor calibration
- [Line Following Documentation](line-following/README.md) - Line following implementation
- [IMU Control Documentation](imu-control/README.md) - IMU-based control system
- [Basic Control Documentation](basic-control/README.md) - Basic robot control

## 🔄 System Components

### 1. Web Interface Control System
- **Python Components**:
  - `flask-controller.py`: Web-based UI with buttons for robot control
  - `webcam-streamer.py`: FFmpeg-based webcam streaming functionality
- **Features**:
  - Browser-based control interface
  - Live video streaming
  - Mobile-friendly control options
  - Real-time command execution

### 2. Utility System
- **Python Components**:
  - `sensor_utils.py`: Sensor calibration and testing
  - `motor_utils.py`: Motor testing and calibration
  - `calibration_test.py`: Motor calibration utility
- **Features**:
  - Sensor calibration tools
  - Motor testing utilities
  - Configuration helpers
  - Diagnostic tools

## 🛠️ Setup

### Prerequisites
- Python 3.6+
- Arduino board with:
  - Two RMCS-2305 dual motor drivers
  - MPU6050 IMU sensor
  - Appropriate wiring and power supply
- FFmpeg (for webcam streaming)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Shival-Gupta/mecanum-robot-control.git
   cd mecanum-robot-control
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install FFmpeg:
   - Windows: Download from https://ffmpeg.org/download.html
   - Linux: `sudo apt-get install ffmpeg`

4. Upload Arduino firmware:
   - Open the appropriate Arduino firmware file
   - Verify pin assignments match your hardware
   - Upload to your Arduino board

## 🎮 Usage

### Web Interface Control
1. Start the Flask controller:
   ```bash
   python web-interfaces/flask-controller.py
   ```

2. Start the webcam streamer:
   ```bash
   python web-interfaces/webcam-streamer.py
   ```

3. Access the interfaces:
   - Control interface: `http://<your-ip-address>:5000`
   - Video stream: `http://<your-ip-address>:6000`

### Utility Tools
1. Run motor calibration:
   ```bash
   python utils/calibration_test.py
   ```

2. Calibrate sensors:
   ```bash
   python utils/sensor_utils.py
   ```

3. Test motors:
   ```bash
   python utils/motor_utils.py
   ```

## 🔧 Configuration

### Serial Port Settings
```python
SERIAL_PORT = "/dev/ttyACM0"  # Change to "COM3" on Windows
BAUD_RATE = 115200
```

### Webcam Streaming
```python
port = 6000
device = '/dev/video0'  # Change as needed
framerate = '25'
video_size = '640x480'
```

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request. See our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments
- JetBot community for inspiration
- Arduino community for hardware support
- Python community for software tools

---

<div align="center">
  <h3>Happy building and controlling your Mecanum robot!!! 🤖</h3>
</div>
