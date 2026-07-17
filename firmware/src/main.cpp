#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// Temperature sensor data wire is connected to GPIO 4
#define ONE_WIRE_BUS 4

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setup() {
  // Start serial communication at 115200 baud
  Serial.begin(115200);
  Serial.println("ESP32 Temperature Sensor Test Starting...");
  
  // Initialize the sensor
  sensors.begin();
}

void loop() {
  // Request temperature readings
  sensors.requestTemperatures(); 
  
  // Read the temperature in Celsius
  float tempC = sensors.getTempCByIndex(0);
  
  // Check if reading was successful
  if (tempC != DEVICE_DISCONNECTED_C) {
    Serial.print("Temperature: ");
    Serial.print(tempC);
    Serial.println(" C");
  } else {
    Serial.println("Error: Could not read temperature data (Sensor disconnected?)");
  }
  
  // Wait 1 second before reading again
  delay(1000);
}
