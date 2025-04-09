# Mecanum Robot Basic Control

This directory contains the core motion control system for a mecanum-wheeled robot. It includes both basic and advanced implementations of the controller firmware and test scripts.

## Components

- **Arduino Firmware:**
  - `mecanum-basic-controller.ino` - Basic 4-wheel controller without IMU
  - `mecanum-advanced-controller.ino` - Enhanced controller with IMU, balancing, and heading control

- **Python Control Scripts:**
  - `controller-test-basic.py` - Simple directional control (forward, backward, left, right)
  - `controller-test-advanced.py` - Advanced movement patterns (strafing, diagonal, curved motion)

## Features

### Basic Controller
- Serial command interface (comma-separated values format)
- Four-motor control with independent speed settings
- Direction and PWM control for each motor
- Simple debugging output

### Advanced Controller
- All features of the basic controller
- MPU6050 IMU integration for motion sensing
- Self-balancing capability for platform stabilization
- Heading control for maintaining course
- Tip-over detection and protection
- Basic inertial odometry

## Hardware Requirements

- Arduino (UNO, Mega, etc.)
- 4 DC motors with Mecanum wheels
- Two RMCS-2305 dual motor drivers
- MPU6050 IMU sensor (for advanced controller only)

## Connection Diagram

```
Arduino Pins Configuration:
- Motor Driver 1 (Front):
    • Front Left: DIR pin 2, PWM pin 3
    • Front Right: DIR pin 4, PWM pin 5
- Motor Driver 2 (Rear):
    • Rear Left: DIR pin 8, PWM pin 9
    • Rear Right: DIR pin 10, PWM pin 11
- MPU6050 (for advanced controller):
    • SDA: A4
    • SCL: A5
```

## Usage

### With Basic Controller

1. Upload `mecanum-basic-controller.ino` to your Arduino
2. Run one of the Python test scripts:
   ```
   python controller-test-basic.py
   ```
   or
   ```
   python controller-test-advanced.py
   ```
3. Follow the on-screen commands to control the robot

### With Advanced Controller

1. Upload `mecanum-advanced-controller.ino` to your Arduino
2. Run one of the Python test scripts as above
3. For balancing and heading control features, use the serial commands:
   - `BALANCE,ON` or `BALANCE,OFF`
   - `HEADING,ON` or `HEADING,OFF`
   - `TARGET,<degrees>` to set heading target

## Compatibility

The Python test scripts are compatible with both controllers, allowing for progressive testing and development:

| Arduino File | Compatible Python Files |
|--------------|-------------------------|
| mecanum-basic-controller.ino | controller-test-basic.py, controller-test-advanced.py |
| mecanum-advanced-controller.ino | controller-test-basic.py, controller-test-advanced.py | 