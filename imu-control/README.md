# Mecanum Robot IMU Control System

This directory contains the enhanced motion control system with IMU-based drift correction for a mecanum-wheeled robot. It provides precise control with drift correction capabilities using the MPU6050 IMU sensor.

## Components

- **Arduino Firmware:**
  - `mecanum-imu-controller.ino` - Enhanced controller with MPU6050 IMU integration for drift correction

- **Python Control Script:**
  - `controller-imu.py` - Advanced control interface with comprehensive movement patterns and continuous mode

## Features

### IMU-Based Controller
- MPU6050 IMU integration for motion sensing
- PID-based straight-line drift correction
- Automatic yaw correction during forward/backward movement
- Comprehensive error handling and status reporting
- Real-time motion data feedback
- Multiple driving modes (with/without drift correction)

### Advanced Controller Interface
- Intuitive keyboard control
- Comprehensive movement commands including:
  - Basic movements (forward, backward, strafe)
  - Rotational movements (clockwise, counter-clockwise)
  - Diagonal movements
  - Curved trajectory movements
- Continuous (hold) movement mode
- Adjustable speed and movement duration
- Real-time status display

## Hardware Requirements

- Arduino (UNO, Mega, etc.)
- 4 DC motors with Mecanum wheels
- Two RMCS-2305 dual motor drivers
- MPU6050 IMU sensor

## Connection Diagram

```
Arduino Pins Configuration:
- Motor Driver 1 (Front):
    • Front Left: DIR pin 2, PWM pin 3
    • Front Right: DIR pin 4, PWM pin 5
- Motor Driver 2 (Rear):
    • Rear Left: DIR pin 8, PWM pin 9
    • Rear Right: DIR pin 10, PWM pin 11
- MPU6050:
    • SDA: A4
    • SCL: A5
```

## Usage

1. Upload `mecanum-imu-controller.ino` to your Arduino
2. Run the Python controller script:
   ```
   python controller-imu.py
   ```
3. Use the keyboard to control the robot:
   - `w`: Forward
   - `s`: Backward
   - `a`: Strafe Left
   - `d`: Strafe Right
   - `q`: Rotate Left
   - `e`: Rotate Right
   - `z`, `x`, `c`, `v`: Diagonal movements
   - `r`, `t`, `f`, `g`: Curved movements
   - `hold <key>`: Activate continuous movement
   - `stop`: Stop all motors
   - `speed <value>`: Set motor speed (0-255)
   - `+` or `-`: Increase/decrease speed
   - `duration <seconds>`: Set movement duration
   - `help`: Display command help
   - `exit` or `quit`: Exit the program

## Drift Correction System

The IMU-based drift correction works by:

1. Monitoring the yaw angle (rotation around vertical axis) using the MPU6050 gyroscope
2. When straight-line motion is detected (same speed for all motors), the correction system activates
3. PID controller adjusts motor speeds to maintain the initial heading
4. Correction is applied differentially (left vs. right side) to counteract drift

## Advanced Functions

The controller supports several advanced features:

- **Calibration Mode**: 
  - Run with `--calibrate` flag to enter calibration mode
  - Use to find optimal PID values for your specific robot

- **Status Messages**:
  - Real-time status feedback from the Arduino
  - Includes yaw angle, correction values, and system state

- **Auto-reconnection**:
  - Automatically attempts to reconnect if serial connection is lost 