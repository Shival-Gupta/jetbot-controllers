# Mecanum Robot Utilities

This directory contains utility scripts and helper functions for the Mecanum robot system.

## Purpose

The utilities folder is intended for:

- Common functions shared across different control systems
- Diagnostic and calibration tools
- Configuration and setup scripts
- Helper classes for sensors and actuators

## Available Utilities

### 1. Sensor Utilities (`sensor_utils.py`)
- **Purpose**: Calibration and testing of robot sensors
- **Features**:
  - IR sensor calibration
  - MPU6050 IMU calibration
  - Sensor data collection and analysis
  - Calibration data saving and loading
- **Usage**:
  ```python
  from sensor_utils import calibrate_ir_sensors, calibrate_mpu6050
  
  # Calibrate IR sensors
  calibration = calibrate_ir_sensors(port="/dev/ttyACM0", samples=50)
  
  # Calibrate MPU6050
  calibration = calibrate_mpu6050(port="/dev/ttyACM0", duration=10)
  ```

### 2. Motor Utilities (`motor_utils.py`)
- **Purpose**: Testing and calibration of robot motors
- **Features**:
  - Individual motor testing
  - Speed calibration
  - Motor direction verification
  - Diagnostic functions
- **Usage**:
  ```python
  from motor_utils import test_motors, calibrate_motor_speeds
  
  # Test all motors
  test_motors(port="/dev/ttyACM0", test_duration=1.0)
  
  # Calibrate motor speeds
  calibration = calibrate_motor_speeds(port="/dev/ttyACM0")
  ```

### 3. Calibration Test (`calibration_test.py`)
- **Purpose**: Comprehensive motor calibration utility
- **Features**:
  - Interactive motor testing
  - Direction verification
  - Speed testing
  - Connection testing
- **Usage**:
  ```bash
  python calibration_test.py
  ```
  or with custom port:
  ```bash
  python calibration_test.py --port COM3
  ```

## Dependencies

- pyserial>=3.5
- numpy>=1.19.0

## Configuration

### Serial Port Settings
- Default port: "/dev/ttyACM0" (Linux) or "COM3" (Windows)
- Default baud rate: 9600 (calibration) or 115200 (operation)

### Calibration Parameters
- IR sensor samples: 50 (default)
- IMU calibration duration: 10 seconds (default)
- Motor test duration: 1.0 seconds (default)

## Integration

Import utilities in your Python scripts:
```python
import sys
import os

# Add the utils directory to the path if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

# Import specific utilities
from sensor_utils import calibrate_sensors
from motor_utils import test_motors
```

## Troubleshooting

1. **Serial Port Issues:**
   - Check if the robot is connected
   - Verify the correct port name
   - Ensure no other program is using the serial port

2. **Calibration Issues:**
   - Ensure stable power supply
   - Check sensor connections
   - Verify motor wiring
   - Increase sample count if needed

3. **Import Errors:**
   - Verify Python path includes utils directory
   - Check all dependencies are installed
   - Ensure correct Python version (3.6+)

## Contributing

When adding new utilities:
1. Create self-contained modules with descriptive names
2. Include clear documentation and examples
3. Make utilities reusable across different control systems
4. Add appropriate error handling and validation
5. Update this README with new utility information 