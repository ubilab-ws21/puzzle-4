import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import time

insertedCode = 0

class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Sequence")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        #show sequence
        self.image = Gtk.Image()
        self.image.set_from_file("pictures/Schneeflocke.png")
        #self.image.set_size_request(60,60)
        vbox.pack_start(self.image, True, True, 0)

        hbox = Gtk.Box(spacing=6)
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

    #read inserted code on button press
    def on_button_clicked(self, widget):
        self.image.set_from_file("pictures/Blitz.png")
        insertedCode = self.entry.get_text()
        print(insertedCode)


win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
win.fullscreen()
Gtk.main()

time.sleep(5)

win.vbox.pack_start(win.image, True, True, 0)
win.show_all()
Gtk.main()