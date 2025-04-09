/*
 * mecanum-imu-controller.ino
 * Version: 2.1
 * 
 * Description: Enhanced 4-wheel Mecanum drive controller with MPU6050-based drift correction.
 * Provides precise control and straight-line drift correction using IMU feedback.
 * 
 * Compatible with:
 *   - controller-imu.py
 *
 * Original description follows:
 */

/*
 * Enhanced 4-Wheel Mecanum Drive Controller with MPU6050 Drift Correction
 *
 * This firmware provides precise control of a mecanum-wheel robot with
 * closed-loop drift correction using an MPU6050 IMU sensor.
 *
 * Features:
 * - Robust serial command parsing
 * - MPU6050-based straight-line drift correction
 * - Comprehensive error handling and status reporting
 * - Configurable PID control for motion correction
 * - Modular, maintainable code architecture
 *
 * Hardware Configuration:
 * - Arduino connected to two RMCS-2305 dual motor drivers
 * - Motors connected as follows:
 *   - Front Left:  DIR pin 2, PWM pin 3
 *   - Front Right: DIR pin 4, PWM pin 5
 *   - Rear Left:   DIR pin 8, PWM pin 9
 *   - Rear Right:  DIR pin 10, PWM pin 11
 * - MPU6050 connected via I2C (SDA = A4, SCL = A5)
 *
 * Version: 2.1
 */

#include <Arduino.h>
#include <Wire.h>
#include "MPU6050.h"

// =================== Configuration Constants =================== //
#define DEBUG_LEVEL 1        // 0=Off, 1=Basic, 2=Verbose
#define STATUS_INTERVAL 500  // Status message interval in ms (when DEBUG_LEVEL >= 2)

const unsigned long BAUD_RATE = 9600;
const uint8_t CMD_BUFFER_SIZE = 64;
const int16_t PWM_MAX = 255;
const uint8_t NUM_MOTORS = 4;
const float YAW_RATE_THRESHOLD = 0.5;  // Degrees/sec threshold to ignore noise
const int16_t MAX_CORRECTION = 50;     // Maximum correction value

// =================== Type Definitions =================== //
struct Motor {
  uint8_t dirPin;  // Direction control pin
  uint8_t pwmPin;  // PWM speed control pin
  int16_t speed;   // Current speed (-255 to 255)
};

enum MotorPosition {
  FRONT_LEFT = 0,
  FRONT_RIGHT = 1,
  REAR_LEFT = 2,
  REAR_RIGHT = 3
};

struct SystemState {
  bool mpuInitialized;
  bool straightDriveActive;
  unsigned long lastStatusTime;
  unsigned long lastUpdateTime;
};

struct PIDController {
  float kp;           // Proportional gain
  float ki;           // Integral gain
  float kd;           // Derivative gain
  float setpoint;     // Target value (0 for straight line)
  float integral;     // Accumulated error
  float lastError;    // Previous error for derivative calculation
  float maxIntegral;  // Anti-windup limit
};

// =================== Global Variables =================== //
Motor motors[NUM_MOTORS] = {
  { 2, 3, 0 },   // Front Left
  { 4, 5, 0 },   // Front Right
  { 8, 9, 0 },   // Rear Left
  { 10, 11, 0 }  // Rear Right
};

MPU6050 mpu;
const int16_t GYRO_OFFSET[3] = { 21, 1, 1 };           // Calibration values
const int16_t ACCEL_OFFSET[3] = { -1459, 555, 5329 };

float yawAngle = 0.0;
int16_t baseMotorSpeeds[NUM_MOTORS] = { 0 };

PIDController pidController = {
  0.5,   // kp
  0.02,  // ki
  0.1,   // kd
  0.0,   // setpoint (0 deg for straight line)
  0.0,   // integral
  0.0,   // lastError
  20.0   // maxIntegral
};

SystemState state = {
  false,  // mpuInitialized
  false,  // straightDriveActive
  0,      // lastStatusTime
  0       // lastUpdateTime
};

char cmdBuffer[CMD_BUFFER_SIZE];
uint8_t cmdIndex = 0;

// =================== Helper Functions =================== //
bool checkSpeeds(const int16_t speeds[NUM_MOTORS], bool &allEqual, bool &allZero) {
  allEqual = true;
  allZero = true;
  for (uint8_t i = 0; i < NUM_MOTORS; i++) {
    if (speeds[i] != speeds[0]) allEqual = false;
    if (speeds[i] != 0) allZero = false;
  }
  return true;
}

unsigned long getDeltaTime(unsigned long &lastTime) {
  unsigned long currentTime = millis();
  unsigned long delta = currentTime - lastTime;
  lastTime = currentTime;
  // Return delta in milliseconds; caller can convert to seconds if needed.
  return delta;
}

// =================== Function Prototypes =================== //
void initializeMotors();
bool initializeMPU();
void processSerialCommands();
bool parseMotorCommand(const char* cmd, int16_t speeds[NUM_MOTORS]);
void sendStatusMessage(const __FlashStringHelper* message, uint8_t level = 1);
void sendStatusMessage(const char* message, uint8_t level = 1);
void setMotorSpeeds(const int16_t speeds[NUM_MOTORS]);
void setMotorSpeed(uint8_t index, int16_t speed);
void stopAllMotors();
void updateIMUData();
void applyStraightLineDriftCorrection();
float calculatePIDCorrection(float currentValue);

// =================== Setup & Main Loop =================== //
void setup() {
  Serial.begin(BAUD_RATE);
  while (!Serial && millis() < 3000) {} // Wait for serial connection

  initializeMotors();
  Wire.begin();
  if (initializeMPU()) {
    sendStatusMessage(F("MPU6050 initialized successfully"), 1);
    state.mpuInitialized = true;
  } else {
    sendStatusMessage(F("WARNING: MPU6050 initialization failed"), 1);
    state.mpuInitialized = false;
  }
  state.lastUpdateTime = millis();
  sendStatusMessage(F("Mecanum controller initialized"), 1);
}

void loop() {
  processSerialCommands();
  
  if (state.mpuInitialized) {
    updateIMUData();
    if (state.straightDriveActive) {
      applyStraightLineDriftCorrection();
    }
    if (DEBUG_LEVEL >= 2 && (millis() - state.lastStatusTime >= STATUS_INTERVAL)) {
      if (state.straightDriveActive) {
        char statusMsg[64];
        snprintf(statusMsg, sizeof(statusMsg), "Yaw: %.2f deg, Straight-drive active", yawAngle);
        sendStatusMessage(statusMsg, 2);
      }
      state.lastStatusTime = millis();
    }
  }
} 