#include <Arduino.h>

// --- Motor Configuration ---
struct Motor {
  uint8_t dirPin;
  uint8_t pwmPin;
};

enum MotorIndex {
  FRONT_LEFT = 0,
  FRONT_RIGHT,
  REAR_LEFT,
  REAR_RIGHT
};

Motor motors[4] = {
  {2, 3},   // Front Left
  {4, 5},   // Front Right
  {8, 9},   // Rear Left
  {10, 11}  // Rear Right
};

const int NUM_MOTORS = 4;
const int PWM_MAX = 255;

// --- Sensor Pins ---
const int leftSensorPin = A0;
const int centerSensorPin = A1;
const int rightSensorPin = A2;

// --- PID Variables ---
float Kp = 2.0;        // Increased for sharper turns
float Ki = 0.01;       // Small integral to correct persistent error
float Kd = 0.2;        // Increased to reduce oscillation
float previousError = 0.0;
float integral = 0.0;
const float setPoint = 500.0;  // Center position (0-1000)

// --- Speed and Timing ---
const int baseSpeed = 120;  // Increased for faster turns
const int loopDelay = 5;    // Reduced for responsiveness
const int uniformThreshold = 150;  // Adjusted to avoid false stops

// --- Direction Control ---
int direction = 0;  // 1: forward, -1: backward, 0: stop

// --- Sensor Smoothing ---
const int filterSize = 5;
int leftValues[filterSize] = {0};
int centerValues[filterSize] = {0};
int rightValues[filterSize] = {0};
int filterIndex = 0;

// --- Serial Command Buffer ---
#define CMD_BUFFER_SIZE 64
char cmdBuffer[CMD_BUFFER_SIZE];
int cmdIndex = 0;

void setup() {
  // Initialize motor pins
  for (int i = 0; i < NUM_MOTORS; i++) {
    pinMode(motors[i].dirPin, OUTPUT);
    pinMode(motors[i].pwmPin, OUTPUT);
  }

  // Start serial at a higher baud rate for efficiency
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for connection
  }
  Serial.println("Mecanum Line Follower Initialized");
}

void loop() {
  // Process serial commands
  processSerialInput();

  // Read raw sensor values
  int leftRaw = analogRead(leftSensorPin);
  int centerRaw = analogRead(centerSensorPin);
  int rightRaw = analogRead(rightSensorPin);

  // Update moving average filter
  leftValues[filterIndex] = leftRaw;
  centerValues[filterIndex] = centerRaw;
  rightValues[filterIndex] = rightRaw;
  filterIndex = (filterIndex + 1) % filterSize;

  // Compute smoothed sensor values
  int leftAvg = 0, centerAvg = 0, rightAvg = 0;
  for (int i = 0; i < filterSize; i++) {
    leftAvg += leftValues[i];
    centerAvg += centerValues[i];
    rightAvg += rightValues[i];
  }
  leftAvg /= filterSize;
  centerAvg /= filterSize;
  rightAvg /= filterSize;

  // Determine line type (darker or lighter)
  int avgValue = (leftAvg + centerAvg + rightAvg) / 3;
  bool lineIsDarker = (avgValue < 512);

  // Adjust sensor values
  int adjLeft = lineIsDarker ? (1023 - leftAvg) : leftAvg;
  int adjCenter = lineIsDarker ? (1023 - centerAvg) : centerAvg;
  int adjRight = lineIsDarker ? (1023 - rightAvg) : rightAvg;

  // Check for uniform surface
  int minVal = min(adjLeft, min(adjCenter, adjRight));
  int maxVal = max(adjLeft, max(adjCenter, adjRight));
  bool isUniform = (maxVal - minVal) < uniformThreshold;

  int leftSpeed = 0;
  int rightSpeed = 0;

  if (isUniform || direction == 0) {
    // Stop the robot
    leftSpeed = 0;
    rightSpeed = 0;
  } else {
    // Compute line position
    long weightedSum = (long)adjLeft * 0 + (long)adjCenter * 500 + (long)adjRight * 1000;
    int sumValues = adjLeft + adjCenter + adjRight;
    float position = (sumValues != 0) ? (float)weightedSum / sumValues : setPoint;

    // PID calculation
    float error = setPoint - position;
    integral += error;
    float derivative = error - previousError;
    float correction = Kp * error + Ki * integral + Kd * derivative;
    previousError = error;

    // Handle sharp turns with rotation
    if (abs(error) > 300) {  // Large deviation detected
      // Rotate in place: left motors reverse, right motors forward (or vice versa)
      int turnSpeed = direction * baseSpeed + (int)correction;
      leftSpeed = -turnSpeed;  // Opposite direction for rotation
      rightSpeed = turnSpeed;
    } else {
      // Normal differential steering
      leftSpeed = direction * baseSpeed + (int)correction;
      rightSpeed = direction * baseSpeed - (int)correction;
    }

    // Constrain speeds
    leftSpeed = constrain(leftSpeed, -PWM_MAX, PWM_MAX);
    rightSpeed = constrain(rightSpeed, -PWM_MAX, PWM_MAX);
  }

  // Apply speeds to motors
  setMotorSpeed(FRONT_LEFT, leftSpeed);
  setMotorSpeed(REAR_LEFT, leftSpeed);
  setMotorSpeed(FRONT_RIGHT, rightSpeed);
  setMotorSpeed(REAR_RIGHT, rightSpeed);

  // Minimal debugging (comment out for performance)
  // Serial.print("Pos: "); Serial.print(position);
  // Serial.print(" LS: "); Serial.print(leftSpeed);
  // Serial.print(" RS: "); Serial.println(rightSpeed);

  delay(loopDelay);
}

// --- Set Motor Speed ---
void setMotorSpeed(int index, int speed) {
  if (index < 0 || index >= NUM_MOTORS) return;
  int absSpeed = abs(speed);
  absSpeed = constrain(absSpeed, 0, PWM_MAX);
  digitalWrite(motors[index].dirPin, (speed >= 0) ? HIGH : LOW);
  analogWrite(motors[index].pwmPin, absSpeed);
}

// --- Process Serial Input ---
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
    } else {
      Serial.println("Error: Buffer overflow");
      cmdIndex = 0;
    }
  }
}

// --- Handle Serial Command ---
void handleCommand(const char* command) {
  if (strcmp(command, "forward") == 0) {
    direction = 1;
    integral = 0;  // Reset integral on direction change
  } else if (strcmp(command, "backward") == 0) {
    direction = -1;
    integral = 0;
  } else if (strcmp(command, "stop") == 0) {
    direction = 0;
  } else {
    Serial.println("Error: Unknown command");
  }
}
