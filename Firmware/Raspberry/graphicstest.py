import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

window = Gtk.Window(title="Hello World")
window.show()
window.fullscreen()
#window.connect("destroy", Gtk.main_quit)

image = Gtk.Image()
image.set_from_file("pictures/Schneeflocke.png")
#image.set_size_request(60,60)
image.show()

window.add(image)
Gtk.main()