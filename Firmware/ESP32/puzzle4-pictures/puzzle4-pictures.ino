/*
 * Waits for start MQTT message and receives current number which should be displayed.
 * Shows the current number on TM1637 7-segment-display when arcade button gets pushed.
 */

/*
 * MQTT topics:
 * puzzle4/esp/state [start, stop] - control the state of all ESPs 
 * puzzle4/esp/1/left/sequence [1-9] - control the number of the left picture of the 1st ESP
 * puzzle4/esp/1/right/sequence [1-9] - control the number of the right picture of the 1st ESP
 */

#include <WiFi.h>
#include <ESPmDNS.h>
#include <ArduinoOTA.h>
#include <PubSubClient.h>
#include "TM1637.h"

#define SERIALSPEED 115200

// Wifi Credentials
#define SSID "FRITZ!Box 7490"
#define PWD "44934748849398685912"

//MQTT Credentials
#define MQTT_SERVER_IP "192.168.178.30" //192.168.0.101
#define MQTT_PORT 1883
#define MAX_MSG 50
char msg[MAX_MSG] = {'\0'};

#define NAME "Puzzle4-ESP1"     //Name of ESP
#define OTA_PWD "pictures"      // OTA Password

//pin definition for TM1637
#define CLK 22  // clock
#define DIO 23  // data
TM1637 tm1637(CLK,DIO);

//pins for the two arcade buttons
#define LED_1 21
#define LED_2 4
#define BUTTON_1 13
#define BUTTON_2 5

bool mqttStart = false;
int leftSequenceIndex = 0;
int rightSequenceIndex = 0;

int leftSequence[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
int rightSequence[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

WiFiClient mqttClient;
PubSubClient mqtt(mqttClient);

bool segmentState[] = {0, 0};


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
  } else {
    Serial.println("Cannot connect to MQTT server");
  }
  mqtt.setCallback(mqttCallback);

  mqtt.subscribe("puzzle4/esp/1/left/sequence");
  mqtt.subscribe("puzzle4/esp/1/right/sequence");
  mqtt.subscribe("puzzle4/esp/state");

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

  // 7-segment display setup
  tm1637.init();
  tm1637.set(4);  // Bright-level from 0 to 7

  pinMode(LED_1, OUTPUT);
  pinMode(LED_2, OUTPUT);

  pinMode(BUTTON_1, INPUT_PULLUP);
  pinMode(BUTTON_2, INPUT_PULLUP);

}

void loop() {
  ArduinoOTA.handle();

  mqtt.loop();
  
  while(!mqttStart){
    Serial.println("Waiting for start signal over MQTT");
    mqtt.loop();
    delay(1000);
  }

  //handle Button 1
  if(digitalRead(BUTTON_1) == 0) {
    tm1637.display(0, leftSequence[leftSequenceIndex]);
    segmentState[0] = 1;
  } else if (segmentState[0] == 1) {
    segmentState[0] = 0;
    tm1637.clearDisplay();
    if (segmentState[1] == 1) {
      tm1637.display(3, rightSequence[rightSequenceIndex]);
    }
  }

  //handle Button 2
  if(digitalRead(BUTTON_2) == 0) {
    tm1637.display(3, rightSequence[rightSequenceIndex]);
    segmentState[1] = 1;
  } else if (segmentState[1] == 1) {
    segmentState[1] = 0;
    tm1637.clearDisplay();
    if (segmentState[0] == 1) {
      tm1637.display(0, leftSequence[leftSequenceIndex]);
    }
  }

  delay(10);
  

}

// MQTT Callback function
void mqttCallback(char* topic, byte* message, unsigned int length) {
  // Convert to cstring
  int len = min((int)length, (int)(MAX_MSG-1));
  memcpy(&msg[0], message, len);
  msg[len] = '\0'; 

  Serial.printf("MQTT msg on topic: %s: %s\n", topic, &msg);

  analyzeMQTTMessage(topic, msg);
}

void analyzeMQTTMessage(char* topic, char* msg) {
  // check for start-message
  if(strcmp(topic, "puzzle4/esp/state") == 0 and strcmp(msg, "start") == 0) {
    setLED(true);
    mqttStart = true;
  }

  // check for end-message
  if(strcmp(topic, "puzzle4/esp/state") == 0 and strcmp(msg, "stop") == 0) {
    setLED(false);
    mqttStart = false;
  }

  //analyze mqtt with a message cointaining a number change
  if (strcmp(topic, "puzzle4/esp/1/left/sequence") == 0){
    sscanf(msg, "%d", &leftSequenceIndex);
  } else if (strcmp(topic, "puzzle4/esp/1/right/sequence") == 0) {
    sscanf(msg, "%d", &rightSequenceIndex);
  }
}

void setLED(bool state) {
  if (state) {
    digitalWrite(LED_1, HIGH);
    digitalWrite(LED_2, HIGH);
  } else {
    digitalWrite(LED_1, LOW);
    digitalWrite(LED_2, LOW);
  }
}
