#include <ArduinoJson.h>

#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

#define DHTPIN 2 // Digital pin connected to the DHT sensor 
#define DHTTYPE    DHT11

// See guide for details on sensor wiring and usage:
//   https://learn.adafruit.com/dht/overview

DHT_Unified dht(DHTPIN, DHTTYPE);

uint32_t delayMS;

void setup() {
  pinMode(3, OUTPUT);
  digitalWrite(3, HIGH);
  Serial.begin(9600); 
  while(!Serial) {
  }
  dht.begin();
  // Set delay between sensor readings based on sensor details.
  delayMS = 1000;
}

void loop() {
  int     size_ = 0;
  String  payload;
  float temperature = 0;
  float humidity = 0;
  String temperature_error;
  String humidity_error;
  char buffer[500];
  while ( !Serial.available()  ){
    temperature_error = "";
    humidity_error = "";
    sensors_event_t event;
    dht.temperature().getEvent(&event);
    if (isnan(event.temperature)) {
      temperature_error = "Error reading temperature! ";
      temperature = 0;
    }
    else {
      temperature = event.temperature;
    }

    dht.humidity().getEvent(&event);
    if (isnan(event.relative_humidity)) {
      humidity_error = "Error reading humidity! ";
      humidity = 0;
    }
    else {
      humidity = event.relative_humidity;
    }
    
    if ( !Serial.available()  ) {
      // Delay between measurements.
      delay(delayMS);
      }
    }
    
  if ( Serial.available() )
    payload = Serial.readStringUntil( '\n' );
  StaticJsonDocument<512> doc;

  DeserializationError   error = deserializeJson(doc, payload);
  if (error) {
//    Serial.println("{\"Success\":\"False\"; \"Error:\" : \"Neco se pokazilo\"}");
    Serial.println(error.f_str()); 
    return;
  }
  if (doc["operation"] == "REQUEST_DATA") {
    String data = "{\"success\":\"true\","
        "\"name\":\"DHT11_MODULE\","
        "\"display_name\":\"DHT11 - teplota a vlhkost vzduchu\", "
        "\"descripion\":\"Senzor DHT11 pro měření teploty a vlhkosti vzduchu\", "
        "\"error\" : \"" + temperature_error + humidity_error + "\","
        "\"variables\": [{\"name\" : \"teplota\", \"type\" : \"float\", \"value\" : " + temperature + ", \"unit\" : \"°C\"},"
        "{\"name\" : \"vlhkost vzduchu\", \"type\" : \"float\", \"value\" : " + humidity + ", \"unit\" : \"%\"}]}";

        
//     sprintf(buffer, "{\"success\":\"true\","
//        "\"name\":\"DHT11_MODULE\","
//        "\"display_name\":\"DHT11 - teplota a vlhkost vzduchu\", "
//
//        "\"values\": [{\"name\" : \"teplota\", \"type\" : \"float\", \"value\" : %d},"
//        "{\"name\" : \"vlhkost vzduchu\", \"type\" : \"float\", \"value\" : %d}]}",  temperature, humidity);
      Serial.println(data);
  }
  else {
      Serial.println("{\"success\":\"false\"; \"error:\" : \"Decoded message doesn't match\"}");
   }
  delay(20);
}
