#include <Arduino.h>

// --- Motor A Pins (Left Motor) ---
const int ENA = 14;  // PWM speed control
const int IN1 = 27;  // Direction 1
const int IN2 = 26;  // Direction 2

// --- Motor B Pins (Right Motor) ---
const int ENB = 32;  // PWM speed control
const int IN3 = 33;  // Direction 1
const int IN4 = 25;  // Direction 2

// PWM Configuration Properties
const int freq = 2000;      // 2 kHz frequency for motor
const int resolution = 8;   // 8-bit resolution (0-255)
// ESP32 requires assigning channels to PWM pins
const int pwmChannelA = 0;
const int pwmChannelB = 1;

void setMotors(int speedA, int speedB) {
  // Constrain speeds to -255 to 255
  speedA = constrain(speedA, -255, 255);
  speedB = constrain(speedB, -255, 255);

  // Motor A (Left)
  if (speedA > 0) {
    // Forward
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
  } else if (speedA < 0) {
    // Backward
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
  } else {
    // Stop
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
  }
  
  // Motor B (Right)
  if (speedB > 0) {
    // Forward
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
  } else if (speedB < 0) {
    // Backward
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
  } else {
    // Stop
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
  }

  // Set absolute speeds (0-255)
  ledcWrite(pwmChannelA, abs(speedA));
  ledcWrite(pwmChannelB, abs(speedB));
}

void setup() {
  Serial.begin(115200);
  Serial.println("Starting ESP32 Motor Dummy Test...");

  // Initialize motor control pins as outputs
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Setup PWM channels
  ledcSetup(pwmChannelA, freq, resolution);
  ledcSetup(pwmChannelB, freq, resolution);
  
  // Attach the PWM channels to the ENA and ENB pins
  ledcAttachPin(ENA, pwmChannelA);
  ledcAttachPin(ENB, pwmChannelB);

  // Ensure motors are stopped initially
  setMotors(0, 0);
  delay(2000);
}

void loop() {
  Serial.println("Moving FORWARD at 50% speed");
  setMotors(128, 128); // 128 is ~50% of 255
  delay(3000);

  Serial.println("Moving FORWARD at 100% speed");
  setMotors(255, 255); // Full speed
  delay(2000);

  Serial.println("STOPPING");
  setMotors(0, 0);
  delay(2000);

  Serial.println("Moving BACKWARD at 50% speed");
  setMotors(-128, -128);
  delay(3000);

  Serial.println("STOPPING");
  setMotors(0, 0);
  delay(2000);

  Serial.println("Turning LEFT in place (Full speed)");
  // Motor A backwards, Motor B forwards
  setMotors(-255, 255);
  delay(2000);

  Serial.println("STOPPING");
  setMotors(0, 0);
  delay(2000);

  Serial.println("Turning RIGHT in place (Full speed)");
  // Motor A forwards, Motor B backwards
  setMotors(255, -255);
  delay(2000);

  Serial.println("STOPPING for 5 seconds before repeating...");
  setMotors(0, 0);
  delay(5000);
}
