/*
 * This is the Firmware for a ESP32 to control a TM1637 7-segment-display which is used as a timer.
 * It shows how much time is still left to solve the current attempt of the puzzle. 
 * If the puzzle is not solved the timer will reset and starts the countdown again.
 */

 /*
 * MQTT topics:
 * puzzle4/esp [start, stop] - control the state of all ESPs
 * puzzle4/esp/timer [error, restart, solved] - error:   timer is either over or the entered passwort is wrong
 *                                            - restart: timer gets restarted again
 *                                            - solved:  puzzle is solved and the timer stops
 * puzzle4/esp/timer/players [int] - set the number of players to influence puzzle timer 2  -> 3:00
 *                                                                                       3  -> 2:30
 *                                                                                       4+ -> 2:00
 * puzzle4/esp/timer/button [on, off] - sets button state                                                                                    
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
#define SSID "ubilab_wifi" //ubilab_wifi
#define PWD "ohg4xah3oufohreiPe7e"  // ohg4xah3oufohreiPe7e

//MQTT Credentials
#define MQTT_SERVER_IP "10.8.166.20" //10.8.166.20
#define MQTT_PORT 1883
#define MAX_MSG 50
char msg[MAX_MSG] = {'\0'};

#define NAME "Puzzle4-Timer"     //Name of ESP
#define OTA_PWD "pictures"      // OTA Password

//pin definition for TM1637
#define CLK 22  // clock
#define DIO 23  // data
TM1637 tm1637(CLK,DIO);

//pins for arcade button
#define LED 13
#define BUTTON 19

// timer variables
int timer2 = 256;  // timer for 2 players
int timer3 = 234;  // timer for 3 players
int timer4 = 205;  // timer for 4+ players

int timer = 234;  // default to 2:30 min
int position_minute = (timer/100U) % 10;
int high_position_second = (timer/10U) % 10;
int low_position_second = (timer/1U) % 10;

// timestep variables
int myTime = 0;
int timestep = 1000; 

// variables
bool reset = false;
bool blinks = false;
bool mqttStart = false;
bool puzzle_solved = false;
bool button_light = false;
bool button_press = false;
int number_of_players = 0;

WiFiClient mqttClient;
PubSubClient mqtt(mqttClient);

void setup() {
  Serial.begin(SERIALSPEED);

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

    mqtt.subscribe("puzzle4/esp");
    mqtt.subscribe("puzzle4/esp/timer");
    mqtt.subscribe("puzzle4/esp/timer/players");
    mqtt.subscribe("puzzle4/esp/timer/button");

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

  //button and button light
  pinMode(LED, OUTPUT);
  pinMode(BUTTON, INPUT_PULLUP);
  
}

void loop() {
  #ifdef networkCapabilities
    ArduinoOTA.handle();
  
    mqtt.loop();

    while(!mqttStart){
      //allow changing button light before start mqtt message
      if (button_light == true) {
        digitalWrite(LED, HIGH);
      } else if (button_light == false) {
        digitalWrite(LED, LOW);
      }

      //check button state before start mqtt message
      if (digitalRead(BUTTON) == 0) {
        if (button_press == false) {
          button_press = true;
          mqtt.publish("puzzle4/button", "true");
        }
      } else {
        if (button_press == true) {
          button_press = false;
          mqtt.publish("puzzle4/button", "false");
        }
      }
      //Serial.println("Waiting for start signal over MQTT");
      mqtt.loop();
    }
  #endif

  //light up button when mqtt message arrives
  if (button_light == true) {
    digitalWrite(LED, HIGH);
  } else if (button_light == false) {
    digitalWrite(LED, LOW);
  }

  //check for button state
  if (digitalRead(BUTTON) == 0) {
    if (button_press == false) {
      button_press = true;
      mqtt.publish("puzzle4/button", "true");
    }
  } else {
    if (button_press == true) {
      button_press = false;
      mqtt.publish("puzzle4/button", "false");
    }
  }

  if (!reset and !puzzle_solved) {
    // enter every second if reset is false
    if(millis() >= myTime + timestep) {
      myTime = millis();

      // stop timer
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

      //normal case, count a second down  f.ex. 2:35 -> 2:34
      else {
        low_position_second--;
      }
    }    
  }

  if (reset or puzzle_solved) {
    blinks = true;
    if (millis() >= myTime + timestep/2) {
      myTime = millis();
      tm1637.point(true);
      tm1637.display(1, position_minute);
      tm1637.display(2, high_position_second);
      tm1637.display(3, low_position_second);
    } else if ((millis() >= myTime + timestep/4)) {
      tm1637.point(false);
      tm1637.clearDisplay();
    }
  }

  if (!blinks) {
    tm1637.display(1, position_minute);
    tm1637.display(2, high_position_second);
    tm1637.display(3, low_position_second);
    tm1637.point(true);
  }

  if (!mqtt.connected()){
    Serial.println("Client disconnected!");
    reconnect();
    mqtt.loop();
  }
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
  if(strcmp(topic, "puzzle4/esp") == 0 and strcmp(msg, "start") == 0) {
    mqttStart = true;
    blinks = false;
    puzzle_solved = false;
    reset = false;
    position_minute = (timer/100U) % 10;
    high_position_second = (timer/10U) % 10;
    low_position_second = (timer/1U) % 10;
  }

  // check for end-message
  if(strcmp(topic, "puzzle4/esp") == 0 and strcmp(msg, "stop") == 0) {
    tm1637.point(false);
    tm1637.clearDisplay();
    mqttStart = false;
    blinks = false;
    puzzle_solved = false;
    position_minute = (timer/100U) % 10;
    high_position_second = (timer/10U) % 10;
    low_position_second = (timer/1U) % 10;
  }

  // check for number of players to choose the time for the puzzle
  if(strcmp(topic, "puzzle4/esp/timer/players") == 0) {
    sscanf(msg, "%d", &number_of_players);
    // 1-2 players: puzzle time = 3:00
    if (number_of_players < 3) {
      timer = timer2;
      position_minute = (timer/100U) % 10;
      high_position_second = (timer/10U) % 10;
      low_position_second = (timer/1U) % 10;      
    }
    // 3 players: puzzle time = 2:30
    if (number_of_players == 3) {
      timer = timer3;
      position_minute = (timer/100U) % 10;
      high_position_second = (timer/10U) % 10;
      low_position_second = (timer/1U) % 10;      
    }
    // 4+ players: puzzle time = 2:00
    if (number_of_players > 3) {
      timer = timer4;
      position_minute = (timer/100U) % 10;
      high_position_second = (timer/10U) % 10;
      low_position_second = (timer/1U) % 10;      
    }
  }

  // check for reset
  if(strcmp(topic, "puzzle4/esp/timer") == 0 and strcmp(msg, "error") == 0) {
    reset = true;
  }

  // check for restart
  if(strcmp(topic, "puzzle4/esp/timer") == 0 and strcmp(msg, "restart") == 0) {
    reset = false;
    blinks = false;
    position_minute = (timer/100U) % 10;
    high_position_second = (timer/10U) % 10;
    low_position_second = (timer/1U) % 10; 
  }

  // check for solved
  if(strcmp(topic, "puzzle4/esp/timer") == 0 and strcmp(msg, "solved") == 0) {
    puzzle_solved = true;
    timer = 230;
    Serial.println("Puzzle solved!!");
  }

  //check if button should be turned on
  if(strcmp(topic, "puzzle4/esp/timer/button") == 0 and strcmp(msg, "on") == 0) {
    button_light = true;
    Serial.println("Button light turned on");
  }
  
  if(strcmp(topic, "puzzle4/esp/timer/button") == 0 and strcmp(msg, "off") == 0) {
    button_light = false;
    Serial.println("Button light turned off");
  }
}

void reconnect() { 
  while (!mqtt.connected()) {  
    if (mqtt.connect(NAME)) { 
      Serial.println("MQTT connected");        
      mqtt.setCallback(mqttCallback);
      mqtt.subscribe("puzzle4/esp");
      mqtt.subscribe("puzzle4/esp/sequence");  
    } 
  }    
}
