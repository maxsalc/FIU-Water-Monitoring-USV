#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <TinyGPSPlus.h>

// --- HARDWARE PINS ---
#define ONE_WIRE_BUS 4

// Motor Driver Pins
#define ENA 25
#define IN1 26
#define IN2 27
#define IN3 14
#define IN4 12
#define ENB 13

// Sensor Pins
#define PIN_PH 36
#define PIN_TDS 35
#define PIN_TURBIDITY 18 // Digital Input mode with internal pull-up (GPIO 18)
#define PIN_VISIBILITY 39

// GPS UART Pins (HardwareSerial2)
#define GPS_RX_PIN 16 // ESP32 RX2 (Connect to GPS TXD)
#define GPS_TX_PIN 17 // ESP32 TX2 (Connect to GPS RXD)

// Radio UART Pins (HardwareSerial1 - Emergency Direct LoRa)
#define RADIO_RX_PIN 32 // ESP32 RX1 (Connect to Radio TXD)
#define RADIO_TX_PIN 33 // ESP32 TX1 (Connect to Radio RXD)

// Sensors, GPS, and Radio
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
TinyGPSPlus gps;
HardwareSerial RadioSerial(1);

// Timing
unsigned long lastTelemetryTime = 0;
const unsigned long TELEMETRY_INTERVAL = 1000; // Send telemetry every 1 second for faster responsive data

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
  int raw = analogRead(pin);
  return (raw / 4095.0) * 3.3;
}

void setup() {
  Serial.begin(115200); // Debug USB Serial
  
  // Initialize GPS on Serial2
  Serial2.begin(9600, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);
  
  // Initialize LoRa Radio directly on Serial1
  RadioSerial.begin(9600, SERIAL_8N1, RADIO_RX_PIN, RADIO_TX_PIN);
  
  sensors.begin();
  sensors.setResolution(10); // 10-bit resolution (187.5ms conversion time vs 750ms 12-bit)
  setupMotors();
  
  pinMode(PIN_TURBIDITY, INPUT_PULLUP);
  
  analogSetPinAttenuation(PIN_PH, ADC_11db);
  analogSetPinAttenuation(PIN_TDS, ADC_11db);
  analogSetPinAttenuation(PIN_VISIBILITY, ADC_11db);
  
  Serial.println("ESP32 Direct Autonomous System Initialized (Standalone Node)");
}

void processCommand(String command) {
  command.trim();
  Serial.printf("[COMMAND RECV] %s\n", command.c_str());
  
  if (command == "FWD") {
    setMotors(200, 200);
  } else if (command == "BWD") {
    setMotors(-200, -200);
  } else if (command == "LEFT") {
    setMotors(-150, 150);
  } else if (command == "RIGHT") {
    setMotors(150, -150);
  } else if (command == "STOP") {
    setMotors(0, 0);
  } else if (command.startsWith("M:")) {
    command.remove(0, 2);
    int commaIndex = command.indexOf(',');
    if (commaIndex > 0) {
      int left_pwm = command.substring(0, commaIndex).toInt();
      int right_pwm = command.substring(commaIndex + 1).toInt();
      setMotors(left_pwm, right_pwm);
    }
  }
}

void loop() {
  // 0. CONTINUOUSLY READ GPS SENTENCES
  while (Serial2.available() > 0) {
    gps.encode(Serial2.read());
  }

  // 1. READ COMMANDS DIRECTLY FROM LORA RADIO
  if (RadioSerial.available() > 0) {
    String command = RadioSerial.readStringUntil('\n');
    processCommand(command);
  }
  
  // Also support local USB debugging commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }

  // 2. BROADCAST TELEMETRY OVER RADIO & USB
  if (millis() - lastTelemetryTime >= TELEMETRY_INTERVAL) {
    lastTelemetryTime = millis();
    
    // -- READ TEMPERATURE --
    sensors.requestTemperatures(); 
    float tempC = sensors.getTempCByIndex(0);
    if (tempC == DEVICE_DISCONNECTED_C) tempC = 25.0;

    // -- READ pH --
    float phVoltage = readVoltage(PIN_PH);
    float current_ph = 7.0 - ((phVoltage - PH_NEUTRAL_VOLTAGE) * 3.1);

    // -- READ TDS --
    float tdsVoltage = readVoltage(PIN_TDS);
    float compensationCoefficient = 1.0 + 0.02 * (tempC - 25.0);
    float compensationVoltage = tdsVoltage / compensationCoefficient;
    float current_salinity = (133.42 * pow(compensationVoltage, 3) - 255.86 * pow(compensationVoltage, 2) + 857.39 * compensationVoltage) * 0.5;
    if (current_salinity < 0) current_salinity = 0;

    // -- READ TURBIDITY --
    int turbDigital = digitalRead(PIN_TURBIDITY);
    float current_turbidity = (turbDigital == HIGH) ? 0.0 : 3000.0;

    // -- READ VISIBILITY --
    float visVoltage = readVoltage(PIN_VISIBILITY);
    float current_visibility = (visVoltage / 3.3) * 100.0;

    // -- READ GPS LOCATION --
    double current_lat = gps.location.isValid() ? gps.location.lat() : 0.0;
    double current_lng = gps.location.isValid() ? gps.location.lng() : 0.0;
    int satellites = gps.satellites.isValid() ? gps.satellites.value() : 0;

    // Format telemetry string
    char teleBuf[128];
    snprintf(teleBuf, sizeof(teleBuf), "S:%.2f,%.2f,%.2f,%.2f,%.2f,%.6f,%.6f\n", 
             tempC, current_ph, current_salinity, current_turbidity, current_visibility, current_lat, current_lng);

    // Broadcast directly over LoRa Radio to Laptop!
    RadioSerial.print(teleBuf);
    
    // Print to local USB Serial for debugging
    Serial.print(teleBuf);
    Serial.printf("DEBUG_VOLTAGE: pH=%.2fV, TDS=%.2fV, TurbDig=%d, GPS_Sats=%d\n", 
                  phVoltage, tdsVoltage, turbDigital, satellites);
  }
}
