#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// --- HARDWARE PINS ---
#define ONE_WIRE_BUS 4

// Motor Driver Pins (Example pins - adjust to your actual wiring!)
#define ENA 25
#define IN1 26
#define IN2 27
#define IN3 14
#define IN4 12
#define ENB 13

// Sensors
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Timing
unsigned long lastTelemetryTime = 0;
const unsigned long TELEMETRY_INTERVAL = 1000; // Send data every 1 second

// Sensor Placeholder Variables (to be implemented later)
float current_ph = 7.1;
float current_salinity = 35.0;
float current_turbidity = 12.5;
float current_visibility = 98.2;

void setupMotors() {
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);
  
  // Stop motors initially
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}

void setMotors(int left_pwm, int right_pwm) {
  // Constrain PWM to 0-255
  left_pwm = constrain(left_pwm, -255, 255);
  right_pwm = constrain(right_pwm, -255, 255);

  // Left Motor Direction
  if (left_pwm >= 0) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
  } else {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
  }
  analogWrite(ENA, abs(left_pwm));

  // Right Motor Direction
  if (right_pwm >= 0) {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
  } else {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
  }
  analogWrite(ENB, abs(right_pwm));
}

void setup() {
  Serial.begin(115200);
  sensors.begin();
  setupMotors();
  Serial.println("ESP32 ROS Hardware Node Initialized");
}

void loop() {
  // 1. DOWNSTREAM: Read incoming commands from Orange Pi (ROS)
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    // Check if it's a Motor Command (e.g., "M:200,-200")
    if (command.startsWith("M:")) {
      command.remove(0, 2); // Remove "M:"
      
      int commaIndex = command.indexOf(',');
      if (commaIndex > 0) {
        String left_str = command.substring(0, commaIndex);
        String right_str = command.substring(commaIndex + 1);
        
        int left_pwm = left_str.toInt();
        int right_pwm = right_str.toInt();
        
        setMotors(left_pwm, right_pwm);
      }
    }
  }

  // 2. UPSTREAM: Send sensor telemetry to Orange Pi (ROS) periodically
  if (millis() - lastTelemetryTime >= TELEMETRY_INTERVAL) {
    lastTelemetryTime = millis();
    
    // Read real temperature
    sensors.requestTemperatures(); 
    float tempC = sensors.getTempCByIndex(0);
    if (tempC == DEVICE_DISCONNECTED_C) tempC = -999.0;

    // Send formatted telemetry string: S:temp,pH,salinity,turbidity,visibility
    Serial.printf("S:%.2f,%.2f,%.2f,%.2f,%.2f\n", 
                  tempC, current_ph, current_salinity, current_turbidity, current_visibility);
  }
}
