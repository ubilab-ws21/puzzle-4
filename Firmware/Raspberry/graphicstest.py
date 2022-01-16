#needed for GUI
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

#needed to run the GUI and the program logic (MQTT, changing pictures) simultaneously
import threading
import time

updatePictures = False
insertedCode = 0
picture = 0
sequence = 0

def runGUI():
    gui_ready.set()
    win = MyWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    win.set_default_size(800, 480)
    Gtk.main()



class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Sequence")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        #show sequence
        self.image = Gtk.Image()
        self.image.set_from_file("sequences/1_1.jpg")
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
        updatePictures_thread.daemon = True
        updatePictures_thread.start()

    #read inserted code on button press
    def on_button_clicked(self, widget):
        insertedCode = self.entry.get_text()
        print(insertedCode)

    def change_picture(self): 
        global picture
        if picture%4 == 0:
            self.image.set_from_file("sequences/1_2.jpg")
        elif picture%4 == 1:
            self.image.set_from_file("sequences/1_3.jpg")
        elif picture%4 == 2:
            self.image.set_from_file("sequences/1_4.jpg")
        elif picture%4 == 3:
            self.image.set_from_file("sequences/Reset.jpg")
        picture = picture + 1


    
    def check_change_picture(self):
        global updatePictures
        while(True):
            if(updatePictures == True):
                GLib.idle_add(self.change_picture)
                updatePictures = False
                


#initalization
gui_ready = threading.Event()
gui_thread = threading.Thread(target=runGUI)
gui_thread.start()
gui_ready.wait()

while(True):
    time.sleep(2)
    updatePictures = True












