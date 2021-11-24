#include <WiFi.h>
#include <ESPmDNS.h>
#include <ArduinoOTA.h>
#include <PubSubClient.h>

#define SERIALSPEED 115200

// Wifi Credentials
#define SSID "MartinRouterKing"
#define PWD "hahahahaha"

//MQTT Credentials
#define MQTT_SERVER_IP "192.168.0.255"
#define MQTT_PORT 1883 

#define NAME "Puzzle4-ESP1"     //Name of ESP
#define OTA_PWD "pictures"      // OTA Password

WiFiClient mqttClient;
PubSubClient mqtt(mqttClient);


void setup() {
  Serial.begin(SERIALSPEED);
  WiFi.begin(SSID,PWD);

  Serial.print("Connecting to ");
  Serial.println(SSID);

  WiFi.setHostname(NAME);
  
  // wait for connecting
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  } 
  // Print IP
  Serial.println("\nWiFi connected.\nIP Adress: ");
  Serial.println(WiFi.localIP());

  // Setting up mDNS
  if (!MDNS.begin(NAME)) { 
    Serial.println("Error setting up MDNS responder!");
  }
  MDNS.addService("_escape", "_tcp", 2000);

  mqtt.setServer(MQTT_SERVER_IP, MQTT_PORT);
  // MQTT connect
  if (mqtt.connect(NAME)) {
    Serial.println("Connected to MQTT server");
  // Publish a message
  const char * topic = "zigbee2mqtt/Bulb/set";
  bool retained = false;
  mqtt.publish(topic, "{\"state\":\"ON\"}", retained);
  } else {
  Serial.println("Cannot connect to MQTT server");
  }

  // Arduino OTA
  ArduinoOTA.setHostname(NAME);
  ArduinoOTA.setPassword(OTA_PWD);
  ArduinoOTA.onStart([]() {
  Serial.println("Start updating");
  });
  ArduinoOTA.onEnd([]() {
  Serial.println("Finished updating");
  });
  ArduinoOTA.onError([](ota_error_t error) {
  Serial.println("Error updating");
  ESP.restart();
  });
  ArduinoOTA.begin();
}

void loop() {
  ArduinoOTA.handle();
  // mqtt.loop(); //Only

}
