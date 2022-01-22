#! /usr/bin/python

#needed for MQTT communication
import paho.mqtt.client as mqtt
import subprocess
import time
import os


#MQTT functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    if (rc==0):
        print("Connected successfully!")

#checks for MQTT messages
def on_message(client, userdata, msg): #function is automatically activated when message is received
    if (msg.topic == "puzzle4"):
        msg.payload = msg.payload.decode("utf-8")
        if(str(msg.payload) == "start"):
            #start the Picture Puzzle 
            print("Received start message for the picture puzzle")
            #p = subprocess.call(["python3", "puzzle4_raspberry_gui.py"])
            subprocess.call(["terminator", "--command=python3 puzzle4_raspberry_gui.py"], cwd="/home/pi/escape_room", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


#Connect to MQTT-Server
def init_mqtt(): 

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("192.168.178.30", 1883, 60) #10.8.166.20
    client.subscribe("puzzle4/#") 
       
    client.loop_start()



if __name__ == "__main__":
    #######Initalization########
    #starts the MQTT connection
    client = mqtt.Client()
    init_mqtt()


    while(True):
        time.sleep(0.1)

