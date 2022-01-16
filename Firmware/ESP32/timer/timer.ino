/*
 * This is the Firmware for a ESP32 to control a TM1637 7-segment-display which is used as a timer.
 * It shows how much time is still left to solve the current attempt of the puzzle. 
 * If the puzzle is not solved the timer will reset and starts the countdown again.
 */

 /*
 * MQTT topics:
 * puzzle4/esp/state [start, stop] - control the state of all ESPs
 * puzzle4/esp/5 [reset, solved] - control reset and solved
 * puzzle4/esp/5/time [3 digit int] - control the time (for ex. 230 - > 2:30)
 */
 
#include <WiFi.h>
#include <ESPmDNS.h>
#include <ArduinoOTA.h>
#include <PubSubClient.h>
#include "TM1637.h"

#define SERIALSPEED 115200

// use WiFi and MQTT
#define networkCapabilities

// Wifi Credentials
#define SSID "no"
#define PWD "no"

//MQTT Credentials
#define MQTT_SERVER_IP "192.168.0.101" //192.168.178.30
#define MQTT_PORT 1883
#define MAX_MSG 50
char msg[MAX_MSG] = {'\0'};

#define NAME "Puzzle4-ESP5"     //Name of ESP
#define OTA_PWD "pictures"      // OTA Password

//pin definition for TM1637
#define CLK 22  // clock
#define DIO 23  // data
TM1637 tm1637(CLK,DIO);

// timer variables
int timer = 13;
int position_minute = (timer/100U) % 10;
int high_position_second = (timer/10U) % 10;
int low_position_second = (timer/1U) % 10;

// timestep variables
int myTime = 0;
int timestep = 1000; 

// reset variable
bool reset = false;
bool mqttStart = false;
bool puzzle_solved = false;

WiFiClient mqttClient;
PubSubClient mqtt(mqttClient);

void setup() {
  Serial.begin(SERIALSPEED);

  Serial.println(position_minute);
  Serial.println(high_position_second);
  Serial.println(low_position_second);

  #ifdef networkCapabilities
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

    mqtt.subscribe("puzzle4/esp/state");
    mqtt.subscribe("puzzle4/esp/5");
    mqtt.subscribe("puzzle4/esp/5/time");

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
  #endif

  // 7-segment display setup
  tm1637.init();
  tm1637.set(4);  // Bright-level from 0 to 7

  tm1637.clearDisplay();
  
}

void loop() {
  #ifdef networkCapabilities
    ArduinoOTA.handle();
  
    mqtt.loop();
    
    while(!mqttStart){
      Serial.println("Waiting for start signal over MQTT");
      mqtt.loop();
      delay(1000);
    }
  #endif

  if(millis() >= myTime + timestep) {
    myTime = millis();

    if (high_position_second == 0 and low_position_second == 0 and position_minute == 0) {
      reset = true;
    }
    // change to lower minute f.ex. 2:00 -> 1:59
    else if (high_position_second == 0 and low_position_second == 0 and position_minute !=0) {
      position_minute--;
      high_position_second = 5;
      low_position_second = 9;      
    }

    //change to lower deci-second  f.ex. 2:30 -> 2:29
    else if (high_position_second != 0 and low_position_second == 0) {
      high_position_second--;
      low_position_second = 9;
    }

    //normal case, count a seond down  f.ex. 2:35 -> 2:34
    else {
      low_position_second--;
    }
  }

  if (reset) {
    // set timer back
    Serial.println("reset is triggerd!!");
    position_minute = (timer/100U) % 10;
    high_position_second = (timer/10U) % 10;
    low_position_second = (timer/1U) % 10;
    reset = false;
  }

  tm1637.display(1, position_minute);
  tm1637.display(2, high_position_second);
  tm1637.display(3, low_position_second);
  tm1637.point(true);
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
    mqttStart = true;
  }

  // check for end-message
  if(strcmp(topic, "puzzle4/esp/state") == 0 and strcmp(msg, "stop") == 0) {
    tm1637.point(false);
    tm1637.clearDisplay();
    mqttStart = false;
    position_minute = (timer/100U) % 10;
    high_position_second = (timer/10U) % 10;
    low_position_second = (timer/1U) % 10; 
  }

  // check for time
  if(strcmp(topic, "puzzle4/esp/5/time") == 0) {
    sscanf(msg, "%d", &timer);
    Serial.println(timer);
    position_minute = (timer/100U) % 10;
    high_position_second = (timer/10U) % 10;
    low_position_second = (timer/1U) % 10; 
  }

  // check for reset
  if(strcmp(topic, "puzzle4/esp/5") == 0 and strcmp(msg, "reset") == 0) {
    reset = true;
  }

  // check for solved
  if(strcmp(topic, "puzzle4/esp/5") == 0 and strcmp(msg, "solved") == 0) {
    puzzle_solved = true;
    Serial.println("Puzzle solved!!");
  }
}
