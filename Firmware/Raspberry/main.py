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
    client.publish("4/gamecontrol", "{\"method\": \"status\", \"state\": \"inactive\"}", retain=True)
    client.subscribe("puzzle4/#") 
    client.subscribe("4/gamecontrol")
    client.subscribe("op/gameOptions")

#checks for MQTT messages
def on_message(client, userdata, msg): #function is automatically activated when message is received
    global players
    #check if puzzle 4 should be activated
    if (msg.topic == "4/gamecontrol"):
        msg.payload = msg.payload.decode("utf-8")
        msg_json = json.loads(msg.payload)
        if(msg_json["method"] == "trigger"):
            if(msg_json["state"] == "on"):
                #start the Picture Puzzle 
                print("Received start message for the picture puzzle")
                #p = subprocess.call(["python3", "puzzle4_raspberry_gui.py"])
                players_copy = players
                players = 3
                subprocess.call(["terminator", "--command=python3 puzzle4_raspberry_gui.py {}".format(players_copy)], cwd="/home/pi/escape_room", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            elif(msg_json["state"] == "skip"):
                #start the Picture Puzzle 
                print("Received skip message for the picture puzzle")
                players_copy = 0
                subprocess.call(["terminator", "--command=python3 puzzle4_raspberry_gui.py {}".format(players_copy)], cwd="/home/pi/escape_room", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    #check if player count is being adjusted
    if (msg.topic == "op/gameOptions"):
        msg.payload = msg.payload.decode("utf-8")
        msg_json = json.loads(msg.payload)
        players = msg_json["participants"]
        if players > 4:
            players = 4
        print("Received player count {}".format(players))

#Connect to MQTT-Server
def init_mqtt(): 

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("10.8.166.20", 1883, 60) #10.8.166.20
    client.subscribe("puzzle4/#")
    client.subscribe("4/gamecontrol")
    client.subscribe("op/gameOptions") 

    client.publish("4/gamecontrol", "{\"method\": \"status\", \"state\": \"inactive\"}", retain=True)

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

