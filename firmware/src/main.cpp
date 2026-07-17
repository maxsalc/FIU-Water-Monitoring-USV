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

// Analog Sensor Pins
#define PIN_PH 36
#define PIN_TDS 35
#define PIN_TURBIDITY 34
#define PIN_VISIBILITY 39

// Sensors
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Timing
unsigned long lastTelemetryTime = 0;
const unsigned long TELEMETRY_INTERVAL = 1000; // Send data every 1 second

// Calibration Offsets
#define PH_NEUTRAL_VOLTAGE 1.50 

void setupMotors() {
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);
  
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}

void setMotors(int left_pwm, int right_pwm) {
  left_pwm = constrain(left_pwm, -255, 255);
  right_pwm = constrain(right_pwm, -255, 255);

  if (left_pwm >= 0) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
  } else {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
  }
  analogWrite(ENA, abs(left_pwm));

  if (right_pwm >= 0) {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
  } else {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
  }
  analogWrite(ENB, abs(right_pwm));
}

float readVoltage(int pin) {
  // ESP32 12-bit ADC (0-4095) mapped to 0-3.3V
  int raw = analogRead(pin);
  return (raw / 4095.0) * 3.3;
}

void setup() {
  Serial.begin(115200);
  sensors.begin();
  setupMotors();
  
  // Set ADC attenuation to allow measuring up to 3.3V
  analogSetPinAttenuation(PIN_PH, ADC_11db);
  analogSetPinAttenuation(PIN_TDS, ADC_11db);
  analogSetPinAttenuation(PIN_TURBIDITY, ADC_11db);
  analogSetPinAttenuation(PIN_VISIBILITY, ADC_11db);
  
  Serial.println("ESP32 ROS Hardware Node Initialized with Sensors");
}

void loop() {
  // 1. DOWNSTREAM: Read incoming commands from Orange Pi
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.startsWith("M:")) {
      command.remove(0, 2); 
      
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

  // 2. UPSTREAM: Send sensor telemetry to Orange Pi periodically
  if (millis() - lastTelemetryTime >= TELEMETRY_INTERVAL) {
    lastTelemetryTime = millis();
    
    // -- READ TEMPERATURE --
    sensors.requestTemperatures(); 
    float tempC = sensors.getTempCByIndex(0);
    if (tempC == DEVICE_DISCONNECTED_C) tempC = 25.0; // Fallback to 25C for TDS compensation if disconnected

    // -- READ pH (DFRobot Analog pH V2) --
    float phVoltage = readVoltage(PIN_PH);
    // Generic DFRobot pH formula (requires manual calibration offsets for true accuracy)
    float current_ph = 7.0 - ((phVoltage - PH_NEUTRAL_VOLTAGE) * 3.1);

    // -- READ TDS (DFRobot TDS V1.0) --
    float tdsVoltage = readVoltage(PIN_TDS);
    // Temperature compensation
    float compensationCoefficient = 1.0 + 0.02 * (tempC - 25.0);
    float compensationVoltage = tdsVoltage / compensationCoefficient;
    float current_salinity = (133.42 * pow(compensationVoltage, 3) - 255.86 * pow(compensationVoltage, 2) + 857.39 * compensationVoltage) * 0.5;
    if (current_salinity < 0) current_salinity = 0;

    // -- READ TURBIDITY (DFRobot Turbidity V1.0) --
    float turbVoltage = readVoltage(PIN_TURBIDITY);
    float current_turbidity = 0.0;
    
    // NOTE: If Turbidity sensor is powered by 5V, voltage can reach 4.5V! 
    // This math assumes a voltage divider is used to step 4.5V down to 3.3V max.
    // If powered directly by 3.3V, the sensor's internal math shifts.
    if (turbVoltage < 2.5) {
      current_turbidity = 3000; // Max turbidity
    } else if (turbVoltage > 4.2) {
      current_turbidity = 0;    // Perfectly clear
    } else {
      current_turbidity = -1120.4 * turbVoltage * turbVoltage + 5742.3 * turbVoltage - 4352.9;
    }
    if (current_turbidity < 0) current_turbidity = 0;

    // -- READ VISIBILITY (Generic Analog Placeholder) --
    float visVoltage = readVoltage(PIN_VISIBILITY);
    float current_visibility = (visVoltage / 3.3) * 100.0;

    // Send formatted telemetry string: S:temp,pH,salinity,turbidity,visibility
    Serial.printf("S:%.2f,%.2f,%.2f,%.2f,%.2f\n", 
                  tempC, current_ph, current_salinity, current_turbidity, current_visibility);
                  
    // Send raw voltages for debugging
    Serial.printf("DEBUG_VOLTAGE: pH=%.2fV, TDS=%.2fV, Turb=%.2fV\n", phVoltage, tdsVoltage, turbVoltage);
  }
}
