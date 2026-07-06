#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// --- Motor Pins ---
const int ENA = 14;
const int IN1 = 27;
const int IN2 = 26;
const int ENB = 32;
const int IN3 = 33;
const int IN4 = 25;

const int freq = 2000;
const int resolution = 8;
const int pwmChannelA = 0;
const int pwmChannelB = 1;

// --- Temperature Sensor ---
const int ONE_WIRE_BUS = 4; // GPIO 4 on ESP32
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setMotors(int speedA, int speedB) {
  speedA = constrain(speedA, -255, 255);
  speedB = constrain(speedB, -255, 255);

  if (speedA > 0) {
    digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  } else if (speedA < 0) {
    digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
  } else {
    digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  }
  
  if (speedB > 0) {
    digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  } else if (speedB < 0) {
    digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
  } else {
    digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  }

  ledcWrite(pwmChannelA, abs(speedA));
  ledcWrite(pwmChannelB, abs(speedB));
}

void setup() {
  Serial.begin(115200);
  
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);

  ledcSetup(pwmChannelA, freq, resolution);
  ledcSetup(pwmChannelB, freq, resolution);
  ledcAttachPin(ENA, pwmChannelA);
  ledcAttachPin(ENB, pwmChannelB);

  setMotors(0, 0);
  sensors.begin();
  
  Serial.println("ESP32 Ready (Motors + Temp)");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "FWD") {
      setMotors(200, 200);
      Serial.println("ACK: FWD");
    } 
    else if (command == "STOP") {
      setMotors(0, 0);
      Serial.println("ACK: STOP");
    }
    else if (command == "TEMP") {
      sensors.requestTemperatures();
      float tempC = sensors.getTempCByIndex(0);
      Serial.println(String(tempC));
    }
  }
}
