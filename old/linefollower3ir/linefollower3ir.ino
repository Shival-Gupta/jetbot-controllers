/*
  Project: 4-Wheel Mecanum Drive Line Follower with PID Control
  Platform: Arduino Uno with RMCS-2305 motor drivers
  Sensors: 3 Analog IR sensors 
    - Left: A0
    - Center: A1
    - Right: A2
  Motors: 4 Mecanum wheels controlled via DIR and PWM pins
    - Front Left: DIR 2, PWM 3
    - Front Right: DIR 4, PWM 5
    - Rear Left: DIR 8, PWM 9
    - Rear Right: DIR 10, PWM 11

  Description:
    This sketch enables a 4-wheel Mecanum robot to follow a line using PID control.
    Three IR sensors detect the line position, and PID adjusts motor speeds to keep
    the robot centered on the line. Differential steering (left vs. right motor speeds)
    allows sharp turns up to 100 degrees.

    Special Behavior:
    - Stops when all three sensors detect a uniform surface (all on or all off the line).
    - Moves forward when the center sensor detects the line (odd reading).
    - Handles sharp turns using PID and omnidirectional capabilities.
    - Automatically detects if the line is darker or lighter than the background.

  PID Tuning:
    Adjust Kp, Ki, Kd for optimal performance:
    - Kp: Proportional gain (corrects based on current error)
    - Ki: Integral gain (corrects persistent offset over time)
    - Kd: Derivative gain (reduces overshooting and oscillations)

  Motor Control:
    Motors support forward and reverse motion for sharper corrections.
    Speeds range from -255 to 255 (PWM range).

  Calibration:
    Use the Serial Monitor to read sensor values and adjust uniformThreshold.
*/

// --- Configuration ---
const int uniformThreshold = 100;  // Max difference in sensor values for uniform surface detection

// --- Pin Configuration ---
// Sensor pins (analog inputs)
const int leftSensorPin   = A0;  // Left IR sensor
const int centerSensorPin = A1;  // Center IR sensor
const int rightSensorPin  = A2;  // Right IR sensor

// Motor control pins (direction and PWM)
const int frontLeftDir  = 2;   // Front Left Direction
const int frontLeftPWM  = 3;   // Front Left Speed
const int frontRightDir = 4;   // Front Right Direction
const int frontRightPWM = 5;   // Front Right Speed
const int rearLeftDir   = 8;   // Rear Left Direction
const int rearLeftPWM   = 9;   // Rear Left Speed
const int rearRightDir  = 10;  // Rear Right Direction
const int rearRightPWM  = 11;  // Rear Right Speed

// --- PID Control Variables ---
float Kp = 0.5;     // Proportional constant (tune for responsiveness)
float Ki = 0.0;     // Integral constant (tune for steady-state error)
float Kd = 0.1;     // Derivative constant (tune to reduce oscillation)
float previousError = 0.0; // Previous error for derivative calculation
float integral      = 0.0; // Accumulated error for integral term
const float setPoint = 500.0;  // Desired line position (center, range 0-1000)

// --- Base Motor Speed ---
const int baseSpeed = 100;     // Base PWM speed (0-255), adjust for your robot
const int loopDelay = 10;      // Delay in ms for loop stability, adjust as needed

// --- Setup Function ---
void setup() {
  // Initialize motor pins as outputs
  pinMode(frontLeftDir, OUTPUT);
  pinMode(frontLeftPWM, OUTPUT);
  pinMode(frontRightDir, OUTPUT);
  pinMode(frontRightPWM, OUTPUT);
  pinMode(rearLeftDir, OUTPUT);
  pinMode(rearLeftPWM, OUTPUT);
  pinMode(rearRightDir, OUTPUT);
  pinMode(rearRightPWM, OUTPUT);

  // Start Serial communication for debugging
  Serial.begin(9600);
  Serial.println("Mecanum Line Follower Initialized");
}

// --- Main Loop ---
void loop() {
  // Read IR sensor values (0-1023)
  int leftValue   = analogRead(leftSensorPin);
  int centerValue = analogRead(centerSensorPin);
  int rightValue  = analogRead(rightSensorPin);

  // Calculate the average sensor value to detect line type
  int avgValue = (leftValue + centerValue + rightValue) / 3;

  // Determine if the line is darker or lighter than the background
  bool lineIsDarker = (avgValue < 512);  // Midpoint assumption, adjust if needed

  // Adjust sensor values based on line type (higher value = line detected)
  int adjLeft   = lineIsDarker ? (1023 - leftValue) : leftValue;
  int adjCenter = lineIsDarker ? (1023 - centerValue) : centerValue;
  int adjRight  = lineIsDarker ? (1023 - rightValue) : rightValue;

  // Check for uniform surface (all sensors on or off the line)
  int minVal = min(adjLeft, min(adjCenter, adjRight));
  int maxVal = max(adjLeft, max(adjCenter, adjRight));
  bool isUniform = (maxVal - minVal) < uniformThreshold;

  // Declare motor speed variables
  int leftSpeed = 0;
  int rightSpeed = 0;

  if (isUniform) {
    // Stop the robot if all sensors detect a uniform surface
    leftSpeed = 0;
    rightSpeed = 0;
    Serial.println("Uniform surface detected - Robot stopped");
  } else {
    // Compute weighted position of the line (0 to 1000)
    long weightedSum = (long)adjLeft * 0 + (long)adjCenter * 500 + (long)adjRight * 1000;
    int sumValues = adjLeft + adjCenter + adjRight;
    float position = (sumValues != 0) ? (float)weightedSum / sumValues : setPoint;

    // Calculate PID terms
    float error = setPoint - position;      // Error from desired position
    integral += error;                      // Accumulate error for integral
    float derivative = error - previousError; // Rate of change for derivative
    float correction = Kp * error + Ki * integral + Kd * derivative; // PID output
    previousError = error;                  // Update previous error

    // Compute motor speeds with correction
    leftSpeed  = baseSpeed + (int)correction;  // Left motors adjust
    rightSpeed = baseSpeed - (int)correction;  // Right motors adjust oppositely

    // Constrain speeds to PWM range (-255 to 255) for reverse capability
    leftSpeed  = constrain(leftSpeed, -255, 255);
    rightSpeed = constrain(rightSpeed, -255, 255);
  }

  // Apply speeds to all motors (Mecanum wheels use differential steering)
  setMotorSpeed(frontLeftDir, frontLeftPWM, leftSpeed);
  setMotorSpeed(rearLeftDir, rearLeftPWM, leftSpeed);
  setMotorSpeed(frontRightDir, frontRightPWM, rightSpeed);
  setMotorSpeed(rearRightDir, rearRightPWM, rightSpeed);

  // Debug output to Serial Monitor
  Serial.print("LeftVal: ");
  Serial.print(leftValue);
  Serial.print(" CenterVal: ");
  Serial.print(centerValue);
  Serial.print(" RightVal: ");
  Serial.print(rightValue);
  Serial.print(" LeftSpeed: ");
  Serial.print(leftSpeed);
  Serial.print(" RightSpeed: ");
  Serial.println(rightSpeed);

  delay(loopDelay); // Small delay for loop stability
}

// --- Function: Set Motor Speed ---
/*
  Sets the speed and direction for a motor.
  Parameters:
    - dirPin: Direction control pin (HIGH = forward, LOW = reverse)
    - pwmPin: PWM speed control pin (0-255)
    - speed: Desired speed (-255 to 255); positive = forward, negative = reverse
*/
void setMotorSpeed(int dirPin, int pwmPin, int speed) {
  if (speed > 0) {
    digitalWrite(dirPin, HIGH); // Set forward direction
    analogWrite(pwmPin, speed); // Apply speed
  } else if (speed < 0) {
    digitalWrite(dirPin, LOW);  // Set reverse direction
    analogWrite(pwmPin, -speed); // Apply speed (absolute value)
  } else {
    digitalWrite(dirPin, HIGH); // Arbitrary direction when stopped
    analogWrite(pwmPin, 0);     // No speed (idle)
  }
}