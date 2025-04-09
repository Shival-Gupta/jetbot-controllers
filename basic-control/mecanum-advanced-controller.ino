/*
 * mecanum-advanced-controller.ino
 * Version: 3.0
 * 
 * Description: Advanced controller for 4-wheel Mecanum drive with MPU6050 IMU integration.
 * Features self-balancing, platform stabilization, heading control, and inertial odometry.
 * 
 * Compatible with:
 *   - controller-test.py
 *   - controller-test-advanced.py
 *   - controller-imu.py
 *
 * Original description follows:
 */

/*
 * Ultimate Mecanum Robot Controller with MPU6050 IMU
 *
 * Features:
 * - Self-balancing & platform stabilization using complementary filtering and PID.
 * - Heading and drift correction using integrated gyro data.
 * - Tip-over detection with motor shutdown.
 * - Basic inertial odometry for short-term motion tracking.
 * - Serial command interface for controlling movement.
 *
 * Hardware:
 * - Arduino (UNO, Mega, etc.)
 * - 4 Mecanum wheels via motor drivers (PWM & DIR per motor)
 * - MPU6050 IMU sensor via I2C (SDA, SCL)
 *
 * Version: Ultimate 1.0
 */

#include <Arduino.h>
#include <Wire.h>
#include "MPU6050.h"  // Ensure the MPU6050 library is installed

// ======= Configuration Constants =======
#define DEBUG_LEVEL 2            // 0=Off, 1=Basic, 2=Verbose
#define SERIAL_BAUD 9600
#define STATUS_INTERVAL 500      // ms between status messages

const uint8_t CMD_BUFFER_SIZE = 64;
const int16_t PWM_MAX = 255;
const uint8_t NUM_MOTORS = 4;

// Motor pins: Front Left, Front Right, Rear Left, Rear Right
const uint8_t MOTOR_DIR[NUM_MOTORS] = {2, 4, 8, 10};
const uint8_t MOTOR_PWM[NUM_MOTORS] = {3, 5, 9, 11};

// Balancing & Heading Parameters
const float BALANCE_THRESHOLD = 10.0;    // Engage balancing if |pitch| > 10°
const float TIP_OVER_THRESHOLD = 30.0;     // Tip-over if |pitch| > 30°
const float ALPHA = 0.98;                  // Complementary filter coefficient

// PID Gains for balancing (tune as needed)
float Kp_balance = 20.0;
float Ki_balance = 0.5;
float Kd_balance = 0.1;

// PID Gains for heading control (tune as needed)
float Kp_heading = 2.0;
float Ki_heading = 0.1;
float Kd_heading = 0.05;

// ======= Global Variables =======
MPU6050 mpu;

// Variables for complementary filtering and balancing
float pitch_acc = 0.0;    // computed from accelerometer
float pitch_gyro = 0.0;   // integrated from gyro
float pitch = 0.0;        // filtered pitch angle (balance axis)
float lastPitchError = 0.0;
unsigned long lastTime = 0;

// PID variables for balancing
float balance_error = 0.0;
float balance_integral = 0.0;
float balance_derivative = 0.0;
float balance_correction = 0.0;

// Heading control variables
float yaw = 0.0;                // integrated yaw angle
float target_heading = 0.0;     // desired heading
float heading_error = 0.0;
float heading_integral = 0.0;
float heading_derivative = 0.0;
float heading_correction = 0.0;

// Inertial odometry (very basic, drift-prone)
float odom_x = 0.0, odom_y = 0.0;

// Serial command buffer
char cmdBuffer[CMD_BUFFER_SIZE];
uint8_t cmdIndex = 0;

// Control mode flags
bool balancingEnabled = false;
bool headingControlEnabled = false;

// Base motor speeds (set via serial MOVE command)
int16_t baseSpeeds[NUM_MOTORS] = {0, 0, 0, 0};

// ======= Function Prototypes =======
void initializeMotors();
void setMotor(uint8_t index, int16_t speed);
void setAllMotors(int16_t speeds[NUM_MOTORS]);
void stopMotors();

void updateIMU();
void computeBalancingPID(float dt);
void computeHeadingPID(float dt);
void updateOdometry(float dt);
void processSerialCommands();
bool parseCommand(const char* cmd);
void sendStatus(const char* msg);

// ======= Setup =======
void setup() {
  Serial.begin(SERIAL_BAUD);
  while (!Serial && millis() < 3000) {} // Wait for serial connection

  initializeMotors();
  Wire.begin();

  mpu.initialize();
  if (!mpu.testConnection()) {
    sendStatus("MPU6050 connection failed!");
    while(1);
  }
  sendStatus("MPU6050 initialized.");
  
  lastTime = millis();
}

// ======= Main Loop =======
void loop() {
  unsigned long currentTime = millis();
  float dt = (currentTime - lastTime) / 1000.0;
  lastTime = currentTime;
  
  // Update IMU (and compute complementary filter)
  updateIMU();
  
  // If balancing is enabled, compute PID for balancing
  if (balancingEnabled) {
    computeBalancingPID(dt);
    if (abs(pitch) > TIP_OVER_THRESHOLD) {
      sendStatus("TIP-OVER DETECTED! Stopping motors.");
      stopMotors();
      return;
    }
  } else {
    balance_correction = 0.0;
  }
  
  // If heading control is enabled, compute heading PID
  if (headingControlEnabled) {
    computeHeadingPID(dt);
  } else {
    heading_correction = 0.0;
  }
  
  // Update odometry (for short-term motion analysis)
  updateOdometry(dt);
  
  // Process any incoming serial commands
  processSerialCommands();
  
  // Mix base command speeds with corrections:
  // For balancing, adjust front vs rear; for heading, adjust left vs right.
  int16_t finalSpeeds[NUM_MOTORS];
  finalSpeeds[0] = baseSpeeds[0] - balance_correction + heading_correction; // Front Left
  finalSpeeds[1] = baseSpeeds[1] - balance_correction - heading_correction; // Front Right
  finalSpeeds[2] = baseSpeeds[2] + balance_correction + heading_correction; // Rear Left
  finalSpeeds[3] = baseSpeeds[3] + balance_correction - heading_correction; // Rear Right
  
  setAllMotors(finalSpeeds);
  
  if (DEBUG_LEVEL >= 2) {
    char buf[128];
    snprintf(buf, sizeof(buf), "Pitch: %.2f, Yaw: %.2f, BalCorr: %.2f, HeadCorr: %.2f, Odom:(%.2f,%.2f)",
             pitch, yaw, balance_correction, heading_correction, odom_x, odom_y);
    sendStatus(buf);
  }
  
  delay(10);
} 