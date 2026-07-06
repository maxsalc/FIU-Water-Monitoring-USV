#include <Arduino.h>

// --- Motor A Pins (Left Motor) ---
const int ENA = 14;
const int IN1 = 27;
const int IN2 = 26;

// --- Motor B Pins (Right Motor) ---
const int ENB = 32;
const int IN3 = 33;
const int IN4 = 25;

const int freq = 2000;
const int resolution = 8;
const int pwmChannelA = 0;
const int pwmChannelB = 1;

void setMotors(int speedA, int speedB) {
  speedA = constrain(speedA, -255, 255);
  speedB = constrain(speedB, -255, 255);

  // Motor A (Left)
  if (speedA > 0) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
  } else if (speedA < 0) {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
  } else {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
  }
  
  // Motor B (Right)
  if (speedB > 0) {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
  } else if (speedB < 0) {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
  } else {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
  }

  ledcWrite(pwmChannelA, abs(speedA));
  ledcWrite(pwmChannelB, abs(speedB));
}

void setup() {
  Serial.begin(115200);
  
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  ledcSetup(pwmChannelA, freq, resolution);
  ledcSetup(pwmChannelB, freq, resolution);
  
  ledcAttachPin(ENA, pwmChannelA);
  ledcAttachPin(ENB, pwmChannelB);

  setMotors(0, 0);
  Serial.println("ESP32 Motor Controller Ready.");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove whitespace

    if (command == "FWD") {
      setMotors(200, 200);
      Serial.println("ACK: FWD");
    } 
    else if (command == "REV") {
      setMotors(-200, -200);
      Serial.println("ACK: REV");
    } 
    else if (command == "LEFT") {
      setMotors(-200, 200);
      Serial.println("ACK: LEFT");
    } 
    else if (command == "RIGHT") {
      setMotors(200, -200);
      Serial.println("ACK: RIGHT");
    } 
    else if (command == "STOP") {
      setMotors(0, 0);
      Serial.println("ACK: STOP");
    }
  }
}
