/*
 * mecanum-basic-controller.ino
 * Version: 1.0
 * 
 * Description: Basic controller for 4-wheel Mecanum drive using RMCS-2305 motor drivers.
 * Provides core functionality for controlling a Mecanum robot via serial commands.
 * 
 * Compatible with:
 *   - controller-test.py
 *   - controller-test-advanced.py
 *
 * Original description follows:
 */

/*
 * 4-Wheel Mecanum Drive Motor Controller for RMCS-2305 Drivers
 *

 * Hardware Setup:
 * ---------------
 * - Two RMCS-2305 Dual Motor Drivers are used.
 * - Motor Driver 1 (Front):
 *     • Channel 1 (Front Left): DIR pin to Arduino pin 2, PWM pin to pin 3.
 *     • Channel 2 (Front Right): DIR pin to Arduino pin 4, PWM pin to pin 5.
 * - Motor Driver 2 (Rear):
 *     • Channel 1 (Rear Left): DIR pin to Arduino pin 8, PWM pin to pin 9.
 *     • Channel 2 (Rear Right): DIR pin to Arduino pin 10, PWM pin to pin 11.
 *
 * - The drivers' SLEEP pins should be tied HIGH to enable them.
 * - Optionally, a potentiometer can be connected to analog pin A0.
 *
 * Command Protocol:
 * -----------------
 * Commands are single lines of text terminated by newline.
 * Format: "num,num,num,num" where each number represents the PWM speed
 * (range -255 to 255) for one motor:
 *   • Motor 0: Front Left
 *   • Motor 1: Front Right
 *   • Motor 2: Rear Left
 *   • Motor 3: Rear Right
 * A positive value runs the motor forward (DIR HIGH) and negative reverses it.
 */

#include <Arduino.h>

// Enable debug printing by setting DEBUG to 1; set to 0 to disable.
#define DEBUG 1

// --- Motor Configuration ---

// Structure to hold motor pin assignments.
struct Motor {
  uint8_t dirPin; // Direction control pin
  uint8_t pwmPin; // PWM (speed) control pin
};

// Using an enum for clarity on motor indices.
enum MotorIndex {
  FRONT_LEFT = 0,
  FRONT_RIGHT,
  REAR_LEFT,
  REAR_RIGHT
};

// Define our four motors (order: Front Left, Front Right, Rear Left, Rear Right).
Motor motors[4] = {
  {2, 3},   // Front Left (Driver 1, channel 1)
  {4, 5},   // Front Right (Driver 1, channel 2)
  {8, 9},  // Rear Left (Driver 2, channel 1)
  {10, 11}   // Rear Right (Driver 2, channel 2)
};

const unsigned long BAUD_RATE = 9600;
const int NUM_MOTORS = 4;
const int PWM_MAX = 255;

// --- Serial Command Buffer Settings ---

#define CMD_BUFFER_SIZE 64   // Maximum command length
char cmdBuffer[CMD_BUFFER_SIZE];  // Buffer to store incoming command
int cmdIndex = 0;                 // Current position in the buffer

// --- Function Prototypes ---
void setupMotorPins();
void processSerialInput();
void handleCommand(const char* command);
bool parseCommand(const char* command, int speeds[NUM_MOTORS]);
void setMotorSpeed(int index, int speed);
void debugPrint(const char* msg);

void setup() {
  // Initialize motor control pins.
  setupMotorPins();

  // (Optional: initialize analog input for a potentiometer.)
  pinMode(A0, INPUT);

  Serial.begin(BAUD_RATE);
  while (!Serial) {
    ; // Wait for the serial port to connect (needed for native USB)
  }
  Serial.println("Mecanum 4-Wheel Motor Controller Initialized");
}

void loop() {
  // Process incoming serial data without blocking the main loop.
  processSerialInput();

  // Additional periodic tasks (e.g., sensor readings) can be added here.
}

/*
 * setupMotorPins()
 * Initializes all motor pins as OUTPUT.
 */
void setupMotorPins() {
  for (int i = 0; i < NUM_MOTORS; i++) {
    pinMode(motors[i].dirPin, OUTPUT);
    pinMode(motors[i].pwmPin, OUTPUT);
  }
}

/*
 * processSerialInput()
 * Reads serial data one character at a time into a fixed buffer.
 * When a newline (or carriage return) is encountered, the complete command
 * is processed and the buffer is reset.
 */
void processSerialInput() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    // End of command detected.
    if (c == '\n' || c == '\r') {
      if (cmdIndex > 0) {
        cmdBuffer[cmdIndex] = '\0';  // Null-terminate the string.
        handleCommand(cmdBuffer);
        cmdIndex = 0;  // Reset buffer for the next command.
      }
    } else {
      if (cmdIndex < CMD_BUFFER_SIZE - 1) {
        cmdBuffer[cmdIndex++] = c;
      } else {
        Serial.println("Error: Command buffer overflow.");
        cmdIndex = 0;  // Reset on overflow to avoid corrupt commands.
      }
    }
  }
}

/*
 * handleCommand()
 * Processes a complete command string by parsing it and applying motor speeds.
 *
 * Parameters:
 *   command - A null-terminated C-string containing the command.
 */
void handleCommand(const char* command) {
  int speeds[NUM_MOTORS] = {0};
  if (parseCommand(command, speeds)) {
    // Update each motor with the parsed speed.
    for (int i = 0; i < NUM_MOTORS; i++) {
      setMotorSpeed(i, speeds[i]);
    }
    // Debug: Print the received speeds.
    #if DEBUG
    Serial.print("Set speeds: ");
    for (int i = 0; i < NUM_MOTORS; i++) {
      Serial.print(speeds[i]);
      if (i < NUM_MOTORS - 1) Serial.print(", ");
    }
    Serial.println();
    #endif
  } else {
    Serial.println("Error: Command parsing failed.");
  }
}

/*
 * parseCommand()
 * Parses a command string formatted as "num,num,num,num" into an array of integers.
 *
 * Parameters:
 *   command - The input command string.
 *   speeds  - An array to be filled with the parsed speed values.
 *
 * Returns:
 *   true if exactly 4 integers are successfully parsed, false otherwise.
 */
bool parseCommand(const char* command, int speeds[NUM_MOTORS]) {
  int numParsed = sscanf(command, "%d,%d,%d,%d",
                         &speeds[0], &speeds[1], &speeds[2], &speeds[3]);
  return (numParsed == NUM_MOTORS);
}

/*
 * setMotorSpeed()
 * Sets the speed and direction for the specified motor.
 *
 * Parameters:
 *   index - The index of the motor (0 to 3).
 *   speed - A signed integer (-PWM_MAX to PWM_MAX). Positive for forward, negative for reverse.
 */
void setMotorSpeed(int index, int speed) {
  if (index < 0 || index >= NUM_MOTORS) return;
  int absSpeed = abs(speed);
  absSpeed = constrain(absSpeed, 0, PWM_MAX);
  // Set direction: HIGH for forward, LOW for reverse.
  digitalWrite(motors[index].dirPin, (speed >= 0) ? HIGH : LOW);
  analogWrite(motors[index].pwmPin, absSpeed);
}

/*
 * debugPrint()
 * Utility function for printing debug messages if debugging is enabled.
 *
 * Parameters:
 *   msg - The message to print.
 */
void debugPrint(const char* msg) {
  #if DEBUG
  Serial.println(msg);
  #endif
} 