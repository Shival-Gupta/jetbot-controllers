# Mecanum Robot Control System

A comprehensive robotics project featuring a Mecanum wheel robot with advanced control capabilities, including IMU-based drift correction, line following, and web interface control.

## 🚀 Features

- **Advanced Movement Control**
  - Omnidirectional movement using Mecanum wheels
  - IMU (MPU6050) integration for drift correction
  - PID-based control system
  - Web interface control
  - Line following capabilities

- **Control Interfaces**
  - Web interface (Flask)
  - Webcam streaming
  - Custom command entry

- **Advanced Features**
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

## 📖 Documentation Links

- [Main Documentation](README.MD) - Overview of the Mecanum Robot Control System, including features, setup, and usage instructions
- [Web Interfaces Documentation](web-interfaces/README.md) - Guide for web-based control and video streaming interfaces, including FFmpeg setup and troubleshooting
- [Utilities Documentation](utils/README.md) - Guide for sensor and motor calibration utilities, including usage examples and configuration
- [Line Following Documentation](line-following/README.md) - Documentation for line following implementation and configuration
- [IMU Control Documentation](imu-control/README.md) - Guide for IMU-based control system and drift correction
- [Basic Control Documentation](basic-control/README.md) - Documentation for basic robot control implementation

## 🔄 System Components

1. **Web Interface Control System**
   - Python: 
     - `flask-controller.py`: Web-based UI with buttons for robot control
     - `webcam-streamer.py`: FFmpeg-based webcam streaming functionality
   - Features:
     - Browser-based control interface
     - Live video streaming
     - Mobile-friendly control options
     - Real-time command execution

2. **Utility System**
   - Python:
     - `sensor_utils.py`: Sensor calibration and testing
     - `motor_utils.py`: Motor testing and calibration
     - `calibration_test.py`: Motor calibration utility
   - Features:
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
   git clone [repository-url]
   cd [repository-name]
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

- Adjust serial port settings in `flask-controller.py`:
  ```python
  SERIAL_PORT = "/dev/ttyACM0"  # Change to "COM3" on Windows
  BAUD_RATE = 115200
  ```

- Configure webcam streaming in `webcam-streamer.py`:
  ```python
  port = 6000
  device = '/dev/video0'  # Change as needed
  framerate = '25'
  video_size = '640x480'
  ```

## 📚 Documentation

- `web-interfaces/README.md`: Web interface documentation
- `utils/README.md`: Utility tools documentation
- Each Python file contains detailed docstrings and comments

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- JetBot community for inspiration
- Arduino community for hardware support
- Python community for software tools

---

Happy building and controlling your Mecanum robot! 🤖
