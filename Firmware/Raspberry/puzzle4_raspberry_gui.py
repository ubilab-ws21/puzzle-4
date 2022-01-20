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

#variables
startProcedure = False
codes = [1234, 2341, 3412, 4123]
players = 3
updatePictures = False
insertedCode = 0
picture = 0
sequence = 0
stopTimer = False
codeCorrect = False
codeWrong = False

#MQTT functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    if (rc==0):
        print("Connected successfully!")

#checks for MQTT messages
def on_message(client, userdata, msg): #function is automatically activated when message is received
    global startProcedure
    global players
    global codes
    #set variable to start the procedure
    if (msg.topic == "puzzle4"):
        msg.payload = msg.payload.decode("utf-8")
        if(str(msg.payload) == "start"):
            startProcedure = True
            print("Received start message")
    #set player count
    if (msg.topic == "puzzle4/players"):
        players = int(msg.payload)
        print("Set player count to {} players". format(players))

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
    win.set_default_size(800, 480)
    Gtk.main()

#specification of the GUI
class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Sequence")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        #show sequence
        self.image = Gtk.Image()
        self.image.set_from_file("sequences/blank.jpg")
        self.image.set_size_request(60,60)
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

            #notify the timer that the puzzle is solved
            client.publish("puzzle4/esp/timer", "solved")
            

        else:
            #reset the entry field
            self.entry.set_text("")

            print("False")
            stopTimer = True
            codeWrong = True
            updatePictures = True

            #notify the timer that the puzzle is solved
            client.publish("puzzle4/esp/timer", "error")


    #changes picture
    def change_picture(self): 
        global picture
        global sequence
        global codeWrong
        global codeCorrect
        global stopTimer
        global updatePictures
        
        if (codeCorrect == True or codeWrong == True):
            if codeCorrect == True:
                self.image.set_from_file("sequences/Correct.jpg")
            elif codeWrong == True:
                self.image.set_from_file("sequences/Wrong.jpg")
        else:
            if picture == 0 or picture == 5:
                self.image.set_from_file("sequences/{}_0.jpg".format(sequence))
            elif picture == 1 or picture == 6: 
                self.image.set_from_file("sequences/{}_1.jpg".format(sequence))
            elif picture == 2 or picture == 7:
                self.image.set_from_file("sequences/{}_2.jpg".format(sequence))
            elif picture == 3 or picture == 8:
                self.image.set_from_file("sequences/{}_3.jpg".format(sequence))
            elif picture == 4:
                self.image.set_from_file("sequences/Restart.jpg")
            elif picture == 9:
                self.image.set_from_file("sequences/Reset.jpg")
                #reset the entry field
                self.entry.set_text("")

                print("Reset")
                stopTimer = True
                codeWrong = True

                #notify the timer that the puzzle is not solved
                client.publish("puzzle4/esp/timer", "error")
            
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
    if players == 2:
        timerLength = 8
    elif players == 3:
        timerLength = 9
    elif players == 4:
        timerLength = 10
    
    while(True):
        updatePictures = True
        #loop as long as the timerLength was set
        for i in range(0, timerLength):
            time.sleep(1)
            #check if the timer should be stopped because the code is wrong or correct
            if (stopTimer == True):
                if codeWrong == True:
                    time.sleep(3)     
                    #tell the timer to restart
                    client.publish("puzzle4/esp/timer", "restart")
                    #restart with new sequence
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

    #generate random sequence number
    sequence = random.randint(0, 3)
    print("The current sequence is {}".format(sequence))
    print("The correct code is {}".format(codes[sequence]))

    #send out sequence number to ESPs
    client.publish("puzzle4/esp/sequence", sequence)

    #send timer length to timer
    client.publish("puzzle4/esp/timer/players", players)

    #tell ESPs to start showing numbers and start the timer
    client.publish("puzzle4/esp", "start")

    #reset stopTimer variable 
    stopTimer = False
    picture = 0
    codeWrong = False
    codeCorrect = False

    #starts Timer in a thread
    timer_ready = threading.Event()
    timer_thread = threading.Thread(target=timerThread)
    timer_thread.start()
    timer_ready.wait()

            

if __name__ == "__main__":
    #######Initalization########
    #starts the MQTT connection
    client = mqtt.Client()
    init_mqtt()

    while(startProcedure == False):
        time.sleep(0.1)

    #starts the GUI in a thread
    gui_ready = threading.Event()
    gui_thread = threading.Thread(target=runGUI)
    gui_thread.start()
    gui_ready.wait()

    startUp()