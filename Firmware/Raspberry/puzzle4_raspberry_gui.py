#!/usr/bin/python3

#TODO: messages to the tts system

#needed for MQTT communication
import paho.mqtt.client as mqtt #pip install paho-mqtt

#needed for GUI
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

#needed to run the GUI and the program logic (MQTT, changing pictures) simultaneously
import threading
import time
import random
import sys
import os
import signal
import subprocess
import json

#variables
codes = [7548, 5849, 9834, 3170, 7413, 4469, 5716, 4827, 5392, 9263]
#codes = [1234, 1234, 1234, 1234, 1234, 1234, 1234, 1234, 1234, 1234]
players = 3
updatePictures = False
insertedCode = 0
picture = 0
sequence = 0
stopTimer = False
codeCorrect = False
codeWrong = False
reset = False
startup = True
timeOver = False
finished = False
bootup = 1
buttonPressed = False
busy = False
progress = 0

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
    global codes
    global stopTimer
    global timeOver
    global updatePictures
    global buttonPressed
    global startup
    global bootup
    global busy
    global finished
    if (msg.topic == "puzzle4"):
        #msg.payload = msg.payload.decode("utf-8")
        msg_json = json.load(msg.payload)
        if(msg_json["trigger"] == "off"):
            print("Time is over")
            stopTimer = True
            timeOver = True
            bootup = 0
            updatePictures = True
    if (msg.topic == "puzzle4/button"):
        msg.payload = msg.payload.decode("utf-8")
        if(str(msg.payload) == "true"):
            buttonPressed = True
        elif (str(msg.payload) == "false"):
            buttonPressed = False
            #wait till startup procedure or busy is finished
            if (timeOver != True): #codeCorrect != True or 
                while startup == True or busy == True:
                    time.sleep(0.1)
                startup = True
                stopTimer = True



#Connect to MQTT-Server
def init_mqtt(): 

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("192.168.178.30", 1883, 60) #10.8.166.20
    client.subscribe("puzzle4/#") 
    client.subscribe("4/gamecontrol")
    client.subscribe("op/gameOptions")

    client.publish("4/gamecontrol", "{\"status\": \"active\"}", retain=True)
       

    client.loop_start()


#starts the GUI window
def runGUI():
    gui_ready.set()
    win = MyWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    win.fullscreen()
    #win.set_default_size(800, 480)
    Gtk.main()

#specification of the GUI
class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Sequence")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        #show sequence
        self.image = Gtk.Image()
        self.image.set_from_file("sequences/boot.jpg")
        #self.image.set_size_request(60,60)
        vbox.pack_start(self.image, True, True, 0)

        hbox = Gtk.Box(spacing=5)
        vbox.pack_start(hbox, True, True, 0)

        #code entry
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter Code")
        self.entry.set_max_length(4)
        self.entry.set_alignment(0.5)
        self.entry.set_editable(False)
        self.entry.connect("activate", self.on_button_clicked)
        hbox.pack_start(self.entry, True, True, 0)

        self.button = Gtk.Button(label="Submit Code")
        self.button.connect("clicked", self.on_button_clicked)
        self.button.set_sensitive(False)
        hbox.pack_end(self.button, True, True, 0)

        updatePictures_thread = threading.Thread(target=self.check_change_picture)
        updatePictures_thread.start()

    #read inserted code on button press
    def on_button_clicked(self, widget):
        global sequence
        global codes
        global stopTimer
        global codeCorrect
        global codeWrong
        global updatePictures
        global busy
        insertedCode = int(self.entry.get_text())

        if (insertedCode == codes[sequence]):
            print("Correct")
            stopTimer = True
            codeCorrect = True
            updatePictures = True
            #busy = True           

        else:
            #reset the entry field
            self.entry.set_text("")

            print("False")
            stopTimer = True
            codeWrong = True
            updatePictures = True
            busy = True


    #changes picture
    def change_picture(self): 
        global picture
        global sequence
        global codeWrong
        global codeCorrect
        global stopTimer
        global updatePictures
        global finished
        global bootup
        global reset
        global busy
        global progress

        #boot sequence
        if bootup > 0:
            self.image.set_from_file("sequences/boot_{}.jpg".format(bootup))
            bootup = bootup + 1
        
        #code correct or incorrect
        elif (codeCorrect == True or codeWrong == True):
            if codeCorrect == True:
                if finished == False:
                    self.image.set_from_file("sequences/Correct.jpg")
                    self.button.set_sensitive(False)
                    self.entry.set_editable(False)
                    finished = True
                #progressbar
                else:
                    self.image.set_from_file("progressbar/progress_{}.JPG".format(progress))
                    progress = progress + 1
            elif codeWrong == True:
                self.image.set_from_file("sequences/Wrong.jpg")

        #time is over (of the whole escape room)
        elif (timeOver == True):
            self.image.set_from_file("sequences/over.jpg")
            self.button.set_sensitive(False)
            self.entry.set_editable(False)

        #the puzzle sequence itself
        else:
            if picture == 0 or picture == 5:
                self.image.set_from_file("sequences/{}_0.JPG".format(sequence))
                self.button.set_sensitive(True)
                self.entry.set_editable(True)
            elif picture == 1 or picture == 6: 
                self.image.set_from_file("sequences/{}_1.JPG".format(sequence))
            elif picture == 2 or picture == 7 or picture == 12:
                self.image.set_from_file("sequences/{}_2.JPG".format(sequence))
            elif picture == 3 or picture == 8:
                self.image.set_from_file("sequences/{}_3.JPG".format(sequence))
            elif picture == 4:
                self.image.set_from_file("sequences/Restart.jpg")
            elif picture == 9:
                self.image.set_from_file("sequences/Reset.jpg")
                #reset the entry field
                self.entry.set_text("")

                print("Reset")
                stopTimer = True
                reset = True
                busy = True
            
            picture = picture + 1


    #checks if the picture should be changed
    def check_change_picture(self):
        global updatePictures
        while(True):
            if(updatePictures == True):
                GLib.idle_add(self.change_picture)
                updatePictures = False


def timerThread():
    global players
    global updatePictures
    global stopTimer
    global codeCorrect
    global codeWrong
    global timeOver
    global startup
    global bootup
    global busy
    global reset

    if players == 2:
        timerLength = 70
    elif players == 3:
        timerLength = 60
    elif players == 4:
        timerLength = 50
    
    while(True):
        updatePictures = True
        #loop as long as the timerLength was set
        for i in range(0, timerLength):
            time.sleep(0.1)
            #check if the timer should be stopped because the code is wrong or correct
            if (stopTimer == True):
                if codeWrong == True:
                    #notify the timer to stop, because the code is wrong
                    client.publish("puzzle4/esp/timer", "error")
                    client.publish("2/textToSpeech", "{\"method\": \"message\", \"data\": \"Code is incorrect. Please try again.\"}")
                    time.sleep(5)    
                    client.publish("puzzle4/esp", "stop") 
                    time.sleep(5)
                    #restart with new sequence
                    startUp()
                elif codeCorrect == True:
                    #notify the timer that the puzzle is solved
                    client.publish("4/gamecontrol", "{\"status\": \"active\"}", retain=True)
                    client.publish("puzzle4/esp/timer", "solved")
                    client.publish("2/textToSpeech", "{\"method\": \"message\", \"data\": \"Code is correct\"}")
                    time.sleep(5)
                    client.publish("puzzle4/esp/timer/button", "off")
                    client.publish("puzzle4/esp", "stop")
                    client.publish("2/textToSpeech", "{\"method\": \"message\", \"data\": \"Server is starting up.\"}")
                    #display progressbar
                    for i in range(0, 16):
                        if (i == 5 or i == 6):
                            time.sleep(2)
                        elif (i == 5 or i == 6):
                            time.sleep(0.3)
                        if (i == 9 or i == 10):
                            time.sleep(1)
                        elif (i == 14):
                            time.sleep(3)
                        else:
                            time.sleep(0.5)
                        #TODO: message to texttospeach system
                        updatePictures = True                  
                    time.sleep(5)
                    subprocess.run("vcgencmd display_power 0", shell=True)
                    os.kill(os.getppid(), signal.SIGHUP)
                    sys.exit()
                elif reset == True:
                    #notify the timer to stop, because the code is wrong
                    client.publish("puzzle4/esp/timer", "error")
                    client.publish("2/textToSpeech", "{\"method\": \"message\", \"data\": \"No code entered in time. Please try again.\"}")
                    time.sleep(5)    
                    client.publish("puzzle4/esp", "stop") 
                    time.sleep(5)
                    #restart with new sequence
                    startUp()
                elif timeOver == True:
                    #send error message to timer
                    client.publish("puzzle4/esp/timer", "error")
                    time.sleep(5)
                    #tell the buttons to stop everything
                    client.publish("puzzle4/esp/timer/button", "off")
                    client.publish("puzzle4/esp", "stop")
                    client.publish("4/gamecontrol", "{\"status\": \"solved\"}", retain=True)
                    time.sleep(15)
                    subprocess.run("vcgencmd display_power 0", shell=True)
                    os.kill(os.getppid(), signal.SIGHUP)
                    sys.exit()
                elif startup == True:
                    #restart with new sequence when button was released
                    bootup = 1
                    #tell the buttons to stop everything
                    client.publish("puzzle4/esp/timer/button", "off")
                    client.publish("puzzle4/esp", "stop")
                    startUp()
                return
        


def startUp():
    #needed or else the GUI thread can't access any value changes
    global sequence
    global players
    global codes
    global stopTimer
    global picture
    global codeCorrect
    global codeWrong
    global startup
    global updatePictures
    global bootup
    global buttonPressed
    global startup
    global busy
    global reset
    global timeOver

    #reset stopTimer variable 
    stopTimer = False
    busy = False
    codeWrong = False
    codeCorrect = False
    reset = False

    if (startup == True and timeOver != True):
        updatePictures = True
        client.publish("puzzle4/esp/timer/button", "on")
        client.publish("2/textToSpeech", "{\"method\": \"message\", \"data\": \"Please press and hold the red button to start server bootup process.\"}")
        while(buttonPressed == False):
            time.sleep(0.1)
            #stop in case the time is over
            if (timeOver == True):
                #send error message to timer
                client.publish("puzzle4/esp/timer", "error")
                time.sleep(5)
                #tell the buttons to stop everything
                client.publish("puzzle4/esp/timer/button", "off")
                client.publish("puzzle4/esp", "stop")
                time.sleep(15)
                subprocess.run("vcgencmd display_power 0", shell=True)
                os.kill(os.getppid(), signal.SIGHUP)
                sys.exit()            

        updatePictures = True
        client.publish("2/textToSpeech", "{\"method\": \"message\", \"data\": \"Safety meassure: Keep pressing the button during bootup.\"}")
        time.sleep(5)
        
        updatePictures = True
        client.publish("2/textToSpeech", "{\"method\": \"message\", \"data\": \"Server is starting up. Please enter code on the next screen.\"}")
        time.sleep(5)
        startup = False
    
    bootup = 0
    picture = 0

    #generate random sequence number
    sequence = random.randint(0, 9)
    print("The current sequence is {}".format(sequence))
    print("The correct code is {}".format(codes[sequence]))

    #send out sequence number to ESPs
    client.publish("puzzle4/esp/sequence", sequence)

    #send timer length to timer
    client.publish("puzzle4/esp/timer/players", players)

    #tell ESPs to start showing numbers and start the timer
    client.publish("puzzle4/esp", "start")

    #starts Timer in a thread
    timer_ready = threading.Event()
    timer_thread = threading.Thread(target=timerThread)
    timer_thread.start()
    timer_ready.wait()

            

if __name__ == "__main__":
    #######Initalization########
    #checks the input arguments for player count
    if (len(sys.argv) == 0):
        players = 3
    else:
        players = int(sys.argv[1])
    print("Player count is set to {}".format(players))
    #starts the MQTT connection
    client = mqtt.Client("puzzle4")
    init_mqtt()

    print("Starting picture puzzle")

    #starts the GUI in a thread
    gui_ready = threading.Event()
    gui_thread = threading.Thread(target=runGUI)
    gui_thread.start()
    gui_ready.wait()

    subprocess.run("vcgencmd display_power 1", shell=True)

    startUp()
