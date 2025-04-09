# Mecanum Robot Line Following System

This directory contains the firmware and control scripts for a line-following Mecanum-wheeled robot. It enables a robot to autonomously follow a line on the ground using three infrared (IR) sensors and PID control.

## Components

- **Arduino Firmware:**
  - `mecanum-line-follower-basic.ino` - Basic line follower with automatic line detection
  - `mecanum-line-follower-advanced.ino` - Enhanced line follower with sensor filtering and bi-directional control

- **Python Control Scripts:**
  - `line-follower-controller.py` - Simple control interface
  - `mecanum-line-controller.py` - Advanced control interface with error handling and response reading

## Features

### Basic Line Follower
- Automatic line type detection (dark line on light background or light line on dark background)
- PID-based line tracking
- Differential steering for turns
- Automatic stopping on uniform surfaces
- Real-time sensor value display

### Advanced Line Follower
- All features of the basic system
- Moving average filter for sensor smoothing
- Serial command interface for direction control
- Bi-directional line following (forward or backward)
- Structured code with improved documentation
- Enhanced error handling

## Hardware Requirements

- Arduino (UNO, Mega, etc.)
- 4 DC motors with Mecanum wheels
- Two dual motor drivers (e.g., RMCS-2305)
- 3 IR reflective sensors
- Power supply for motors and Arduino

## Connection Diagram

```
Arduino Pins Configuration:
- Motor Driver 1 (Front):
    • Front Left: DIR pin 2, PWM pin 3
    • Front Right: DIR pin 4, PWM pin 5
- Motor Driver 2 (Rear):
    • Rear Left: DIR pin 8, PWM pin 9
    • Rear Right: DIR pin 10, PWM pin 11
- IR Sensors:
    • Left: A0
    • Center: A1
    • Right: A2
```

## Usage

### Basic Line Following

1. Upload `mecanum-line-follower-basic.ino` to your Arduino
2. Place the robot on a line
3. Power on the robot
4. The robot will automatically follow the line

### Controlled Line Following

1. Upload `mecanum-line-follower-advanced.ino` to your Arduino
2. Run the Python controller script:
   ```bash
   python mecanum-line-controller.py
   ```
3. Use the following commands:
   - `forward` or `f` - Start forward line following
   - `backward` or `b` - Start backward line following
   - `stop` or `s` - Stop the robot
   - `exit` - Exit the control program

## PID Tuning

For optimal performance, you may need to adjust the PID parameters in the Arduino firmware:

- **Kp** (Proportional Gain):
  - Increase to make the robot respond more aggressively to deviations from the line
  - Decrease if the robot oscillates or overshoots the line

- **Ki** (Integral Gain):
  - Increase to help eliminate steady-state error if the robot doesn't center perfectly on the line
  - Keep at 0.0 initially to avoid integration wind-up issues

- **Kd** (Derivative Gain):
  - Increase to reduce oscillations and overshooting
  - Decrease if the robot becomes jittery or unresponsive

## Line Detection

The system automatically detects whether the line is darker or lighter than the background:

1. It computes the average value of all three sensors
2. If the average value is below 512 (midpoint of 0-1023 range), the line is considered darker
3. Sensor values are inverted as needed so that higher values always indicate the presence of the line

## Compatibility

| Arduino File | Compatible Python Files |
|--------------|-------------------------|
| mecanum-line-follower-basic.ino | line-follower-controller.py, mecanum-line-controller.py |
| mecanum-line-follower-advanced.ino | line-follower-controller.py, mecanum-line-controller.py | 