#! /usr/bin/python

#needed for MQTT communication
import paho.mqtt.client as mqtt
import subprocess
import time
import atexit
import json

#variables 
players = 3

#MQTT functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    if (rc==0):
        print("Connected successfully!")
    client.subscribe("puzzle4/#") 
    client.subscribe("4/gamecontrol")
    client.subscribe("op/gameOptions")

#checks for MQTT messages
def on_message(client, userdata, msg): #function is automatically activated when message is received
    global players
    #check if puzzle 4 should be activated
    if (msg.topic == "4/gamecontrol"):
        #msg.payload = msg.payload.decode("utf-8")
        msg_json = json.load(msg.payload)
        if(msg_json["trigger"] == "on"):
            #start the Picture Puzzle 
            print("Received start message for the picture puzzle")
            #p = subprocess.call(["python3", "puzzle4_raspberry_gui.py"])
            players_copy = players
            players = 3
            subprocess.call(["terminator", "--command=python3 puzzle4_raspberry_gui.py {}".format(players_copy)], cwd="/home/pi/escape_room", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    #check if player count is being adjusted
    if (msg.topic == "op/gameOptions"):
        msg_json = json.load(msg.payload)
        players = msg_json["participants"]
        if players > 4:
            players = 4
        print("Received player count {}".format(players))

#Connect to MQTT-Server
def init_mqtt(): 

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("192.168.178.30", 1883, 60) #10.8.166.20
    client.subscribe("puzzle4/#")
    client.subscribe("4/gamecontrol")
    client.subscribe("op/gameOptions") 

    client.publish("4/gamecontrol", "{\"status\": \"inactive\"}", retain=True)

    client.loop_start()

def exit():
    subprocess.run("vcgencmd display_power 1", shell=True)



if __name__ == "__main__":
    #######Initalization########
    #turn on display on exit
    atexit.register(exit)
    #turn off display 
    subprocess.run("vcgencmd display_power 0", shell=True)
    #wait for Wifi connection
    #starts the MQTT connection
    client = mqtt.Client("puzzle4_main")
    init_mqtt()


    while(True):
        time.sleep(0.1)

