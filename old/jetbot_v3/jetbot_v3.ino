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

// ======= Function Implementations ======= //

void initializeMotors() {
  for (uint8_t i = 0; i < NUM_MOTORS; i++) {
    pinMode(MOTOR_DIR[i], OUTPUT);
    pinMode(MOTOR_PWM[i], OUTPUT);
    digitalWrite(MOTOR_DIR[i], LOW);
    analogWrite(MOTOR_PWM[i], 0);
  }
}

void setMotor(uint8_t index, int16_t speed) {
  if (index >= NUM_MOTORS) return;
  speed = constrain(speed, -PWM_MAX, PWM_MAX);
  digitalWrite(MOTOR_DIR[index], (speed >= 0) ? HIGH : LOW);
  analogWrite(MOTOR_PWM[index], abs(speed));
}

void setAllMotors(int16_t speeds[NUM_MOTORS]) {
  for (uint8_t i = 0; i < NUM_MOTORS; i++) {
    setMotor(i, speeds[i]);
  }
}

void stopMotors() {
  int16_t zeros[NUM_MOTORS] = {0, 0, 0, 0};
  setAllMotors(zeros);
}

void updateIMU() {
  // Get raw sensor data from MPU6050
  int16_t ax, ay, az, gx, gy, gz;
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
  
  // Compute accelerometer-based pitch (in degrees)
  pitch_acc = atan2(ax, sqrt(ay * ay + az * az)) * 180.0 / PI;
  
  // Gyro integration: assume gx is pitch rate in deg/s (scale: 131 LSB/deg/s)
  float gyroRate = gx / 131.0;
  // Integrate gyro data over dt (using a rough dt from loop delay)
  float dt_imu = 0.01; // approximate, refined by complementary filter
  pitch_gyro = pitch + gyroRate * dt_imu;
  
  // Complementary filter
  pitch = ALPHA * pitch_gyro + (1 - ALPHA) * pitch_acc;
  
  // Integrate yaw (using gz for yaw rate)
  float yawRate = gz / 131.0;
  yaw += yawRate * dt_imu;
  if (yaw > 180) yaw -= 360;
  if (yaw < -180) yaw += 360;
}

void computeBalancingPID(float dt) {
  balance_error = 0.0 - pitch;  // desired pitch is 0°
  balance_integral += balance_error * dt;
  balance_derivative = (balance_error - lastPitchError) / dt;
  balance_correction = Kp_balance * balance_error +
                       Ki_balance * balance_integral +
                       Kd_balance * balance_derivative;
  lastPitchError = balance_error;
}

void computeHeadingPID(float dt) {
  heading_error = target_heading - yaw;
  heading_integral += heading_error * dt;
  heading_derivative = (heading_error) / dt;  // simple derivative
  heading_correction = Kp_heading * heading_error +
                       Ki_heading * heading_integral +
                       Kd_heading * heading_derivative;
}

void updateOdometry(float dt) {
  // Very simple inertial odometry using accelerometer readings (prone to drift)
  float ax_ms = mpu.getAccelerationX() / 16384.0 * 9.81;
  float ay_ms = mpu.getAccelerationY() / 16384.0 * 9.81;
  static float vel_x = 0.0, vel_y = 0.0;
  vel_x += ax_ms * dt;
  vel_y += ay_ms * dt;
  odom_x += vel_x * dt;
  odom_y += vel_y * dt;
}

void processSerialCommands() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (cmdIndex > 0) {
        cmdBuffer[cmdIndex] = '\0';
        if (!parseCommand(cmdBuffer)) {
          sendStatus("Error: Invalid command format");
        }
        cmdIndex = 0;
      }
    } else if (cmdIndex < CMD_BUFFER_SIZE - 1) {
      cmdBuffer[cmdIndex++] = c;
    } else {
      sendStatus("Error: Command buffer overflow");
      cmdIndex = 0;
    }
  }
}

bool parseCommand(const char* cmd) {
  // Expected command formats:
  // "MOVE,FL,FR,RL,RR"  -> Set base motor speeds
  // "BALANCE,ON" or "BALANCE,OFF" -> Toggle balancing mode
  // "HEADING,<angle>" -> Set target heading and enable heading control
  // "STOP" -> Stop all motors and disable control modes
  char buf[CMD_BUFFER_SIZE];
  strncpy(buf, cmd, CMD_BUFFER_SIZE);
  buf[CMD_BUFFER_SIZE - 1] = '\0';
  
  char* token = strtok(buf, ",");
  if (!token) return false;
  
  if (strcasecmp(token, "MOVE") == 0) {
    for (int i = 0; i < NUM_MOTORS; i++) {
      token = strtok(NULL, ",");
      if (!token) return false;
      baseSpeeds[i] = atoi(token);
    }
    char out[64];
    snprintf(out, sizeof(out), "MOVE: %d, %d, %d, %d", baseSpeeds[0], baseSpeeds[1], baseSpeeds[2], baseSpeeds[3]);
    sendStatus(out);
    return true;
  } else if (strcasecmp(token, "BALANCE") == 0) {
    token = strtok(NULL, ",");
    if (!token) return false;
    if (strcasecmp(token, "ON") == 0) {
      balancingEnabled = true;
      sendStatus("Balancing enabled");
    } else if (strcasecmp(token, "OFF") == 0) {
      balancingEnabled = false;
      sendStatus("Balancing disabled");
    } else {
      return false;
    }
    return true;
  } else if (strcasecmp(token, "HEADING") == 0) {
    token = strtok(NULL, ",");
    if (!token) return false;
    target_heading = atof(token);
    headingControlEnabled = true;
    char out[32];
    snprintf(out, sizeof(out), "Heading set to %.2f", target_heading);
    sendStatus(out);
    return true;
  } else if (strcasecmp(token, "STOP") == 0) {
    stopMotors();
    balancingEnabled = false;
    headingControlEnabled = false;
    sendStatus("Motors stopped; controls disabled");
    return true;
  }
  return false;
}

void sendStatus(const char* msg) {
  Serial.println(msg);
}
