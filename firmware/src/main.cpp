#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <TinyGPSPlus.h>

// --- HARDWARE PINS ---
#define ONE_WIRE_BUS 4

// Motor Driver Pins (Example pins - adjust to your actual wiring!)
#define ENA 25
#define IN1 26
#define IN2 27
#define IN3 14
#define IN4 12
#define ENB 13

// Sensor Pins
#define PIN_PH 36
#define PIN_TDS 35
#define PIN_TURBIDITY 34 // Digital Input mode (GPIO 34)
#define PIN_VISIBILITY 39

// GPS UART Pins (HardwareSerial2)
#define GPS_RX_PIN 16 // ESP32 RX2 (Connect to GPS TXD)
#define GPS_TX_PIN 17 // ESP32 TX2 (Connect to GPS RXD)

// Sensors & GPS
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
TinyGPSPlus gps;

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
  
  // Initialize GPS on Serial2
  Serial2.begin(9600, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);
  
  sensors.begin();
  setupMotors();
  
  // Set Turbidity Pin as Digital Input
  pinMode(PIN_TURBIDITY, INPUT);
  
  // Set ADC attenuation for analog sensors
  analogSetPinAttenuation(PIN_PH, ADC_11db);
  analogSetPinAttenuation(PIN_TDS, ADC_11db);
  analogSetPinAttenuation(PIN_VISIBILITY, ADC_11db);
  
  Serial.println("ESP32 ROS Hardware Node Initialized with Sensors & GPS");
}

void loop() {
  // 0. CONTINUOUSLY READ GPS SENTENCES
  while (Serial2.available() > 0) {
    gps.encode(Serial2.read());
  }

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

  // 2. UPSTREAM: Send sensor & GPS telemetry to Orange Pi periodically
  if (millis() - lastTelemetryTime >= TELEMETRY_INTERVAL) {
    lastTelemetryTime = millis();
    
    // -- READ TEMPERATURE --
    sensors.requestTemperatures(); 
    float tempC = sensors.getTempCByIndex(0);
    if (tempC == DEVICE_DISCONNECTED_C) tempC = 25.0; // Fallback to 25C for TDS compensation if disconnected

    // -- READ pH (DFRobot Analog pH V2) --
    float phVoltage = readVoltage(PIN_PH);
    float current_ph = 7.0 - ((phVoltage - PH_NEUTRAL_VOLTAGE) * 3.1);

    // -- READ TDS (DFRobot TDS V1.0) --
    float tdsVoltage = readVoltage(PIN_TDS);
    float compensationCoefficient = 1.0 + 0.02 * (tempC - 25.0);
    float compensationVoltage = tdsVoltage / compensationCoefficient;
    float current_salinity = (133.42 * pow(compensationVoltage, 3) - 255.86 * pow(compensationVoltage, 2) + 857.39 * compensationVoltage) * 0.5;
    if (current_salinity < 0) current_salinity = 0;

    // -- READ TURBIDITY (Digital Mode) --
    int turbDigital = digitalRead(PIN_TURBIDITY);
    // DFRobot Digital Mode: HIGH = Clear Water (0 NTU), LOW = Turbid Water (3000 NTU)
    float current_turbidity = (turbDigital == HIGH) ? 0.0 : 3000.0;

    // -- READ VISIBILITY (Generic Analog Placeholder) --
    float visVoltage = readVoltage(PIN_VISIBILITY);
    float current_visibility = (visVoltage / 3.3) * 100.0;

    // -- READ GPS LOCATION --
    double current_lat = gps.location.isValid() ? gps.location.lat() : 0.0;
    double current_lng = gps.location.isValid() ? gps.location.lng() : 0.0;
    int satellites = gps.satellites.isValid() ? gps.satellites.value() : 0;

    // Send formatted telemetry string: S:temp,pH,salinity,turbidity,visibility,lat,lng
    Serial.printf("S:%.2f,%.2f,%.2f,%.2f,%.2f,%.6f,%.6f\n", 
                  tempC, current_ph, current_salinity, current_turbidity, current_visibility, current_lat, current_lng);
                  
    // Send raw debug status
    Serial.printf("DEBUG_VOLTAGE: pH=%.2fV, TDS=%.2fV, TurbDig=%d, GPS_Sats=%d\n", 
                  phVoltage, tdsVoltage, turbDigital, satellites);
  }
}
