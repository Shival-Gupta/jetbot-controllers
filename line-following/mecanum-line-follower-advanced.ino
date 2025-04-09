/*
 * mecanum-line-follower-advanced.ino
 * Version: 2.0
 * 
 * Description: Advanced line follower for 4-wheel Mecanum robot using 3 IR sensors.
 * Features sensor filtering, command processing, and bi-directional control for
 * following lines in both forward and backward directions.
 * 
 * Compatible with:
 *   - line-follower-controller.py
 *   - mecanum-line-controller.py
 *
 * Original description follows:
 */

/**
 * @file MecanumLineFollower.ino
 * @brief Arduino sketch for a Mecanum wheel robot to follow a line using PID control.
 * @details Controls four motors based on three analog sensors to follow a line forward or backward.
 *          Handles straight lines, curves, and sharp turns (e.g., 90 degrees).
 * @author Shival Gupta
 * @date 26-03-2025
 */

#include <Arduino.h>

// --- Constants ---
#define NUM_MOTORS 4          ///< Number of motors (4 for Mecanum setup)
#define PWM_MAX 255           ///< Maximum PWM value for motor speed
#define FILTER_SIZE 5         ///< Size of sensor smoothing filter
#define CMD_BUFFER_SIZE 64    ///< Serial command buffer size
#define LOOP_DELAY_MS 5       ///< Main loop delay in milliseconds
#define INTEGRAL_LIMIT 100    ///< Limit for PID integral term
#define UNIFORM_THRESHOLD 100 ///< Threshold for detecting uniform surface

// --- Motor Configuration ---
struct Motor {
  uint8_t dirPin; ///< Direction pin (HIGH = forward, LOW = reverse)
  uint8_t pwmPin; ///< PWM pin for speed control
};

/** Motor indices for easy reference */
enum MotorIndex {
  FRONT_LEFT = 0,
  FRONT_RIGHT,
  REAR_LEFT,
  REAR_RIGHT
};

/** Motor pin assignments */
Motor motors[NUM_MOTORS] = {
  {2, 3},  // Front Left
  {4, 5},  // Front Right
  {8, 9},  // Rear Left
  {10, 11} // Rear Right
};

// --- Sensor Pins ---
const int leftSensorPin = A0;   ///< Left sensor analog pin
const int centerSensorPin = A1; ///< Center sensor analog pin
const int rightSensorPin = A2;  ///< Right sensor analog pin

// --- PID Configuration ---
const float Kp = 1.0;         ///< Proportional gain
const float Ki = 0.0;         ///< Integral gain (disabled to prevent wind-up)
const float Kd = 0.5;         ///< Derivative gain for damping
const float SET_POINT = 500.0; ///< Desired line position (center, range 0-1000)
float previousError = 0.0;     ///< Previous error for derivative calculation
float integral = 0.0;          ///< Integral term for PID

// --- Speed and Direction ---
const int BASE_SPEED = 100; ///< Base speed for motors (adjustable, 0-255)
int direction = 0;          ///< Direction: 1 (forward), -1 (backward), 0 (stop)

// --- Sensor Smoothing ---
int leftValues[FILTER_SIZE] = {0};   ///< Buffer for left sensor readings
int centerValues[FILTER_SIZE] = {0}; ///< Buffer for center sensor readings
int rightValues[FILTER_SIZE] = {0};  ///< Buffer for right sensor readings
int filterIndex = 0;                 ///< Current index in filter buffer

// --- Serial Command Buffer ---
char cmdBuffer[CMD_BUFFER_SIZE]; ///< Buffer for incoming serial commands
int cmdIndex = 0;                ///< Current index in command buffer

// --- Function Prototypes ---
void setupMotors();
void readSensors(int& left, int& center, int& right);
float calculatePosition(int left, int center, int right);
void computePID(float position, float& correction);
void setMotorSpeeds(int leftSpeed, int rightSpeed);
void processSerialInput();
void handleCommand(const char* command);

/**
 * @brief Initializes the Arduino and motor pins.
 */
void setup() {
  setupMotors();
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for serial connection
  }
  Serial.println("Mecanum Line Follower Ready");
}

/**
 * @brief Main control loop for line following.
 */
void loop() {
  processSerialInput();

  if (direction == 0) {
    setMotorSpeeds(0, 0); // Stop all motors
  } else {
    // Read sensor values
    int left, center, right;
    readSensors(left, center, right);

    // Calculate line position
    float position = calculatePosition(left, center, right);

    // Compute PID correction
    float correction;
    computePID(position, correction);

    // Calculate motor speeds
    int leftSpeed = direction * BASE_SPEED + (int)correction;
    int rightSpeed = direction * BASE_SPEED - (int)correction;

    // Constrain speeds to PWM range
    leftSpeed = constrain(leftSpeed, -PWM_MAX, PWM_MAX);
    rightSpeed = constrain(rightSpeed, -PWM_MAX, PWM_MAX);

    // Apply speeds to motors
    setMotorSpeeds(leftSpeed, rightSpeed);
  }

  delay(LOOP_DELAY_MS);
}

/**
 * @brief Configures motor pins as outputs.
 */
void setupMotors() {
  for (int i = 0; i < NUM_MOTORS; i++) {
    pinMode(motors[i].dirPin, OUTPUT);
    pinMode(motors[i].pwmPin, OUTPUT);
    digitalWrite(motors[i].dirPin, HIGH); // Default to forward
    analogWrite(motors[i].pwmPin, 0);     // Start stopped
  }
}

/**
 * @brief Reads and smooths sensor values using a moving average filter.
 * @param[out] left Filtered left sensor value
 * @param[out] center Filtered center sensor value
 * @param[out] right Filtered right sensor value
 */
void readSensors(int& left, int& center, int& right) {
  int leftRaw = analogRead(leftSensorPin);
  int centerRaw = analogRead(centerSensorPin);
  int rightRaw = analogRead(rightSensorPin);

  leftValues[filterIndex] = leftRaw;
  centerValues[filterIndex] = centerRaw;
  rightValues[filterIndex] = rightRaw;
  filterIndex = (filterIndex + 1) % FILTER_SIZE;

  left = center = right = 0;
  for (int i = 0; i < FILTER_SIZE; i++) {
    left += leftValues[i];
    center += centerValues[i];
    right += rightValues[i];
  }
  left /= FILTER_SIZE;
  center /= FILTER_SIZE;
  right /= FILTER_SIZE;
}

/**
 * @brief Calculates the line position based on sensor readings.
 * @param left Left sensor value
 * @param center Center sensor value
 * @param right Right sensor value
 * @return float Line position (0-1000, 500 is center)
 */
float calculatePosition(int left, int center, int right) {
  int avgValue = (left + center + right) / 3;
  bool lineIsDarker = (avgValue < 512);

  int adjLeft = lineIsDarker ? (1023 - left) : left;
  int adjCenter = lineIsDarker ? (1023 - center) : center;
  int adjRight = lineIsDarker ? (1023 - right) : right;

  int minVal = min(adjLeft, min(adjCenter, adjRight));
  int maxVal = max(adjLeft, max(adjCenter, adjRight));
  if ((maxVal - minVal) < UNIFORM_THRESHOLD) {
    return SET_POINT; // Assume centered on uniform surface
  }

  long weightedSum = (long)adjLeft * 0 + (long)adjCenter * 500 + (long)adjRight * 1000;
  int sumValues = adjLeft + adjCenter + adjRight;
  return (sumValues != 0) ? (float)weightedSum / sumValues : SET_POINT;
}

/**
 * @brief Computes PID correction based on line position.
 * @param position Current line position
 * @param[out] correction Computed speed correction
 */
void computePID(float position, float& correction) {
  float error = SET_POINT - position;
  integral += error;
  integral = constrain(integral, -INTEGRAL_LIMIT, INTEGRAL_LIMIT);
  float derivative = error - previousError;
  
  correction = Kp * error + Ki * integral + Kd * derivative;
  previousError = error;
}

/**
 * @brief Sets motor speeds for all four motors.
 * @param leftSpeed Speed for left motors
 * @param rightSpeed Speed for right motors
 */
void setMotorSpeeds(int leftSpeed, int rightSpeed) {
  // Set direction pins based on speed direction
  digitalWrite(motors[FRONT_LEFT].dirPin, leftSpeed >= 0 ? HIGH : LOW);
  digitalWrite(motors[REAR_LEFT].dirPin, leftSpeed >= 0 ? HIGH : LOW);
  digitalWrite(motors[FRONT_RIGHT].dirPin, rightSpeed >= 0 ? HIGH : LOW);
  digitalWrite(motors[REAR_RIGHT].dirPin, rightSpeed >= 0 ? HIGH : LOW);
  
  // Set PWM values (always positive)
  analogWrite(motors[FRONT_LEFT].pwmPin, abs(leftSpeed));
  analogWrite(motors[REAR_LEFT].pwmPin, abs(leftSpeed));
  analogWrite(motors[FRONT_RIGHT].pwmPin, abs(rightSpeed));
  analogWrite(motors[REAR_RIGHT].pwmPin, abs(rightSpeed));
}

/**
 * @brief Processes incoming serial data for commands.
 */
void processSerialInput() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (cmdIndex > 0) {
        cmdBuffer[cmdIndex] = '\0';
        handleCommand(cmdBuffer);
        cmdIndex = 0;
      }
    } else if (cmdIndex < CMD_BUFFER_SIZE - 1) {
      cmdBuffer[cmdIndex++] = c;
    }
  }
}

/**
 * @brief Handles parsed commands.
 * @param command The command string to handle
 */
void handleCommand(const char* command) {
  if (strcmp(command, "forward") == 0) {
    direction = 1;
    Serial.println("Moving forward");
  } else if (strcmp(command, "backward") == 0) {
    direction = -1;
    Serial.println("Moving backward");
  } else if (strcmp(command, "stop") == 0) {
    direction = 0;
    Serial.println("Stopped");
  } else {
    Serial.print("Unknown command: ");
    Serial.println(command);
  }
} 