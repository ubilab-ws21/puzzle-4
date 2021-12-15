#!/usr/bin/python3

import paho.mqtt.client as mqtt #pip install paho-mqtt
import time


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    if (rc==0):
        print("Connected successfully!")

def on_message(client, userdata, msg): #function is automatically activated when message is received
    if (msg.topic == "puzzle4/raspberry"):
        print("Received start message")

def init_mqtt(): #Connect to MQTT-Server

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("192.168.0.101", 1883, 60) #192.168.92.128
    client.subscribe("puzzle4/#") 
    client.publish("puzzle4/esp/state", "start") #tell ESPs to start showing numbers
    

    client.loop_start()


if __name__ == "__main__":
    i = 0
    client = mqtt.Client()
    init_mqtt()
    while(1):
        time.sleep(1)
        client.publish("puzzle4/esp/1/left/sequence", i)
        print(i)
        i = i + 1
        if (i==10):
            i=0