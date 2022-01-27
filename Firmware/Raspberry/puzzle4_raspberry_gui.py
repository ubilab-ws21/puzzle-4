#!/usr/bin/python3

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
startup = True
timeOver = False
finished = False

#MQTT functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    if (rc==0):
        print("Connected successfully!")

#checks for MQTT messages
def on_message(client, userdata, msg): #function is automatically activated when message is received
    global codes
    global stopTimer
    global timeOver
    global updatePictures
    if (msg.topic == "puzzle4"):
        msg.payload = msg.payload.decode("utf-8")
        if(str(msg.payload) == "stop"):
            print("Time is over")
            stopTimer = True
            timeOver = True
            updatePictures = True
            client.publish("puzzle4/esp/timer", "error")
            #tell the buttons to stop everything
            client.publish("puzzle4/esp", "stop")
            time.sleep(10)
            #subprocess.run("vcgencmd display_power 0", shell=True)
            os.kill(os.getppid(), signal.SIGHUP)
            sys.exit()


#Connect to MQTT-Server
def init_mqtt(): 

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("192.168.178.30", 1883, 60) #10.8.166.20
    client.subscribe("puzzle4/#") 
       

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
        self.image.set_from_file("sequences/startup.jpg")
        #self.image.set_size_request(60,60)
        vbox.pack_start(self.image, True, True, 0)

        hbox = Gtk.Box(spacing=5)
        vbox.pack_start(hbox, True, True, 0)

        #code entry
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter Code")
        self.entry.set_max_length(4)
        self.entry.set_alignment(0.5)
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
        insertedCode = int(self.entry.get_text())

        if (insertedCode == codes[sequence]):
            print("Correct")
            stopTimer = True
            codeCorrect = True
            updatePictures = True           

        else:
            #reset the entry field
            self.entry.set_text("")

            print("False")
            stopTimer = True
            codeWrong = True
            updatePictures = True


    #changes picture
    def change_picture(self): 
        global picture
        global sequence
        global codeWrong
        global codeCorrect
        global stopTimer
        global updatePictures
        global finished
        if (codeCorrect == True or codeWrong == True):
            if codeCorrect == True:
                if finished == False:
                    self.image.set_from_file("sequences/Correct.jpg")
                    self.button.set_sensitive(False)
                else:
                    print("Test")
                    self.image.set_from_file("sequences/startup2.jpg")
                finished = True
            elif codeWrong == True:
                self.image.set_from_file("sequences/Wrong.jpg")
        elif (timeOver == True):
            self.image.set_from_file("sequences/over.jpg")
            self.button.set_sensitive(False)
        else:
            if picture == 0 or picture == 5 or picture == 10:
                self.image.set_from_file("sequences/{}_0.JPG".format(sequence))
                self.button.set_sensitive(True)
            elif picture == 1 or picture == 6 or picture == 11: 
                self.image.set_from_file("sequences/{}_1.JPG".format(sequence))
            elif picture == 2 or picture == 7 or picture == 12:
                self.image.set_from_file("sequences/{}_2.JPG".format(sequence))
            elif picture == 3 or picture == 8 or picture == 13:
                self.image.set_from_file("sequences/{}_3.JPG".format(sequence))
            elif picture == 4 or picture == 9:
                self.image.set_from_file("sequences/Restart.jpg")
            elif picture == 14:
                self.image.set_from_file("sequences/Reset.jpg")
                #reset the entry field
                self.entry.set_text("")

                print("Reset")
                stopTimer = True
                codeWrong = True
            
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
    #timerLength = 0
    if players == 2:
        timerLength = 120
    elif players == 3:
        timerLength = 105
    elif players == 4:
        timerLength = 85
    
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
                    client.publish("2/textToSpeech", "Code is incorrect. Please try again.")
                    time.sleep(3)    
                    client.publish("puzzle4/esp", "stop") 
                    #restart with new sequence
                    startUp()
                elif codeCorrect == True:
                    #notify the timer that the puzzle is solved
                    client.publish("puzzle4/esp/timer", "solved")
                    time.sleep(5)
                    client.publish("puzzle4/esp", "stop")
                    client.publish("2/textToSpeech", "Code is correct. Server is starting up.")
                    updatePictures = True
                    #tell the operator that puzzle 4 is solved
                    client.publish("operator/puzzle4", "solved")
                    time.sleep(20)
                    #subprocess.run("vcgencmd display_power 0", shell=True)
                    os.kill(os.getppid(), signal.SIGHUP)
                    sys.exit()
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

    #reset stopTimer variable 
    stopTimer = False
    if startup==True:
        client.publish("2/textToSpeech", "Server is starting up. Please enter code on the next screen to unlock the server")
        time.sleep(10)
        startup = False
    picture = 0
    codeWrong = False
    codeCorrect = False

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

    #subprocess.run("vcgencmd display_power 1", shell=True)

    startUp()
