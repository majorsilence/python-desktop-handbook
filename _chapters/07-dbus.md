---
layout: chapter
title: "D-Bus"
number: 7
part: 1
---

> **Not yet rewritten.** This chapter still describes GTK 2 and PyGTK,
> carried over from the previous edition. It is queued for the GTK 4 and
> PyGObject rewrite; the code in it will not run against GTK 4.

## Introduction

DBus is used for interprocess communication between applications. Simply put this means that applications can retrieve information from one another by accessing special methods that are provided by DBus.

ObjectPath
: An application may export an object to represent itself or different parts of itself. For example Rhythmbox exports an object representing the Play List and an object representing the current playing song. Eg. /org/gnome/Rhythmbox/Player

<a id="des-objectpath-an-application"></a>

BusName
: The name of the application as exposed through DBus. Eg. org.gnome.Rhythmbox

<a id="des-busname-the-name"></a>

Interface
: Is used to access methods through DBus. Eg. org.gnome.Rhythmbox

<a id="des-interface-is-used"></a>

This chapters purpose is to show how to control other applications with DBus and how to add DBus to your PyGTK applications so that you can expose functionality of your applications to others.

## Controlling Applications {#sec-dbus-controlling-applications}

First off is going to be an example of how to use dbus to communicate with another application. This example will communicate with the rhythmbox music player. The reason for using rhythmbox is because it is it is rather ubiquitous in the gnome distro world.

```python
#!/usr/bin/env python
import os, gobject, dbus
from dbus.mainloop.glib import DBusGMainLoop
import gtk
```

The above code imports the needed code to work with this example. What is needed to work with DBus is the *dbus* module and *DBusGMainLoop*. The dbus module is used for the common dbus interactions while DBusGMainLoop is used to work with gobject main loops, which PyGTK uses.

Here the class DBusExample is created with the \_\_init\_\_ method setting up the dbus.

```python
class DBusExample(object):
  def __init__(self):
    # Do before session or system bus is created.
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    self.bus = dbus.SessionBus()

    self.proxy_object = self.bus.get_object('org.gnome.Rhythmbox',
        '/org/gnome/Rhythmbox/Player')
    self.player = dbus.Interface(self.proxy_object,
        'org.gnome.Rhythmbox.Player')

    self.bus.add_signal_receiver(self.on_song_changed,
        dbus_interface="org.gnome.Rhythmbox.Player",
        signal_name="playingUriChanged")

    self.init_gui()
    self.list_available_commands()
```

To begin with a DBus SessionBus is created. This allows connecting to other applications. If this example were connecting to a system process it would use a SystemBus. Once the bus is created, a proxy object is assigned to self.proxy\_object using the self.bus.get\_object method. The get\_object method takes as arguments the applications Bus Name([Introduction](07-dbus.html#des-busname-the-name)) and Object Path([Introduction](07-dbus.html#des-objectpath-an-application)).

After the proxy\_object has been created it is used to create an interface to the available methods. The interface self.player is created using the dbus.Interface class. It is initlized with the self.proxy\_object and using the org.gnome.Rhythmbox.Player interface. This interface provides for methods to control and retrieve information on the currently playing song.

Below this a signal handler is created on the bus to catch the playingUriChanged Signal from the interface org.gnome.Rhythmbox.Player and call the on\_song\_changed method.

Lastly in the \_\_init\_\_ method the init\_gui method is called. The init\_gui method is rather insignificant as it creates a small gui with a few buttons. However the callback methods for those buttons use the self.player interface to control rhythmbox.

```python
  def init_gui(self):
    win = gtk.Window()
    win.connect("delete_event", lambda w,e:gtk.main_quit())
    vbox = gtk.VBox()
    hbox = gtk.HBox()

    self.output = gtk.Label("")
    vbox.pack_start(self.output, False, True, 0)
    mute=gtk.Button("Mute")
    play_pause=gtk.Button("Play/Pause")
    previous=gtk.Button("Previous")
    next=gtk.Button("Next")

    mute.connect("clicked", self.on_mute_clicked)
    play_pause.connect("clicked", self.on_play_pause_clicked)
    previous.connect("clicked", self.on_previous_clicked)
    next.connect("clicked", self.on_next_clicked)

    hbox.pack_start(mute, False, True, 0)
    hbox.pack_start(play_pause, False, True, 0)
    hbox.pack_start(previous, False, True, 0)
    hbox.pack_start(next, False, True, 0)
    vbox.pack_start(hbox, False, True, 0)
    win.add(vbox)
    win.show_all()
```

The init\_gui method above creates a small user interface with a play/pause, mute, previous and next button to control rhythmbox. It also as a label that is used by the on\_song\_changed callback method, that was specified in the \_\_init\_\_ method, to display the path and name of the current playing song.

```python
  def on_mute_clicked(self, widget):
    if self.player.getMute():
      self.player.setMute(False)
    else:
      self.player.setMute(True)
```

The on\_mute\_clicked method checks to see if rhythmbox is muted, if it is it will unmute it. If it is not muted it will set it to mute. This is accomplished using the self.player interface with the setMute method, which takes a boolean argument.

```python
  def on_play_pause_clicked(self, widget):
    if self.player.getPlaying():
      self.player.playPause(False)
    else:
      self.player.playPause(True)
```

The on\_play\_pause\_clicked method will set rhythmbox to play if it is paused and pause it if it is playing. This is accomplished using the self.player interface with the playPause method, which takes a boolean argument.

```python
  def on_previous_clicked(self, widget):
    self.player.previous()
```

The on\_previous\_clicked method will set rhythmbox to play the previous played song. This is accomplished using the self.player interface with the previous method.

```python
  def on_next_clicked(self, widget):
    self.player.next()
```

The on\_next\_clicked method will set rhythmbox to play the next song. This is accomplished using the self.player interface with the next method.

```python
  def on_song_changed(self, data):
    path, filename = os.path.split(self.player.getPlayingUri())
    self.output.set_text("Path: " + path + "\nFilename: " + filename)
```

The on\_song\_changed method is called when the playingUriChanged signal is emitted. It retrieves the current songs current uri, splitting it into a path and file name, and displays it using a gtk label. It should also be pointed out that instead of using the getPlayUri() method, the data argument could be used as it is the uri of the current song as well.

And last lets not forget the small amount of code to run this example

```python
if __name__ == "__main__":
  app = DBusExample()
  gtk.main()
```

## Adding DBus to your Applications

Controlling other applications using DBus is one thing but it is not enough if you application needs to allow others to control it. To let other applications have access to your program requires explosing methods of sub class of dbus.service.Object.

### Creating a DBus Service {#sub-dbus-creating-a-dbus-service}

To start off a few modlues need to be imported. The import ones are the DBus ones.

```python
#!/usr/bin/env python
import os, gobject, dbus, dbus.service
from dbus.mainloop.glibimport DBusGMainLoop
import gtk

output_label = None
```

So of the above modules dbus, dbus.service and DBusGMainLoop are what are important for allowing other applications to connect to his one. After the imports there is the output\_label which will be used as a global to create a gtk.Label to display messages that are received through DBus.

After this DBusObject class is created; it can be named whatever you want as long as it subclasses dbus.service.Object. As you will see it is not necessary to create \_\_init\_\_ method with this class as the parent classes can be used.

```python
class DBusObject(dbus.service.Object):
  # Display and message to gtk label and return message to caller
  @dbus.service.method('com.majorsilence.MessageInterface',
      in_signature='', out_signature='s')
  def display_welcome_message(self):
    global output_label
    output_label.set_text("Welcome to dbus.")
    return "Welcome to dbus."
```

To expose methods for the @dbus.service.method decorator is used, specifying the DBus Interface that the method will available on and the methods in (arguments) and out (return value) signatures. Here the interface is specified as com.majorsilence.MessageInterface, so any application calling this method would have to use com.majorsilence.MessageInterface. After the decorator declare the method as normal. The method name is the same name that will be exposed.

So what we end up with here is a method called display\_welcome\_message that returns a string, s meaning it is a dbus.String type (see [Types](07-dbus.html#sec-dbus-types)). As can be seen it sets the label to "Welcome to dbus" and returns the same message to the calling program.

Moving on to the next method, it takes a string as an argument emits a signal and completion and returns nothing.

```python
# Set gtk label to the message that is passed
  @dbus.service.method(dbus_interface='com.majorsilence.MessageInterface', in_signature='s', out_signature='')
  def set_message(self, s):
    global output_label
    if not isinstance(s, dbus.String):
      print "not string"
      return
    output_label.set_text(s)
    #emit signal
    self.message_signal()
```

As before and like all exposed DBus methods the @dbus.service.method decorator is used. This method has the same DBus Interface as the first method, com.majorsilence.MessageInterface, and an in\_signature of s meaning a dbus.String (see [Types](07-dbus.html#sec-dbus-types)).

The method is set\_message, it takes as an argument a string. It checks to make sure it was passed a string, if it was it will set the label to the string that was passed in. The interesting thing about this method compared to the first one is that it emits a signal on completion. It does this by calling the self.message\_signal() method as its last act.

The self.message\_signal is the method that is described next. It to uses a dbus decorator, but instead of using the @dbus.service.method decorator, it uses the @dbus.service.signal decorator. What this means is that when this method is called it will emit a signal that can be caught using the add\_signal\_receiver method that was described in [Controlling Applications](07-dbus.html#sec-dbus-controlling-applications).

```python
  @dbus.service.signal('com.majorsilence.MessageInterface')
  def message_signal(self):
    return
```

As can be seen the message\_signal method uses the @dbus.service.signal decorator and specifies the com.majorsilence.MessageInterface. If it is to include data with its signal it should also have a out\_signature specifying the correct type.

All that is left is the the main() function that is used to setup a very small PyGTK GUI and create the neccesary DBus initiation.

```python
def main():
  # Create GTK Gui
  global output_label
  win = gtk.Window()
  win.connect("delete_event", lambda w,e:gtk.main_quit())
  output_label = gtk.Label("This message will change through using dbus.")
  win.add(output_label)
  win.show_all()

  # Start DBus Service
  dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
  session_bus = dbus.SessionBus()
  name = dbus.service.BusName("com.majorsilence.MessageService", session_bus)
  object = DBusObject(session_bus, "/TestObject")

  gtk.main()
```

The important part of the code starts after the # Start DBus Service comment. These four lines of code are what makes available dbus and makes it possible to expose method of the application to any other DBus capable program. First DBus must be set to use the glib gobject main loop (the same that PyGTK uses), without this it will not work. Next it creates a session bus that allows applications to connect to a bus. After this it uses the session bus to create a bus name using the dbus.service.BusName class. It takes as arguements the session bus that was created and the interface com.majorsilence.MessageService.

Finally the object is create calling the DBusObject class that we have created, using the session bus that we have created and using the /TestObject object path.

```python
if __name__ == "__main__":
  main()
```

Of course do not forget to call the main function that runs the the example PyGTK DBus service application.

### Connecting to your DBus Service {#sub-dbus-connecting-to-your-dbus-service}

Controlling your own application through DBus is very similiar to how the first example controlled Rhythmbox. This is a small application that will call the two exposed methods from [Creating a DBus Service](07-dbus.html#sub-dbus-creating-a-dbus-service) and handle the signal that is emitted.

```python
#!/usr/bin/env python
import os, gobject,dbus
from dbus.mainloop.glib import DBusGMainLoop
import gtk

class DBusClient(object):
  def __init__(self):
    # Do before session or system bus is created.
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    self.bus = dbus.SessionBus()
    self.proxy = self.bus.get_object('com.majorsilence.MessageService',
        '/TestObject')
    self.control_interface = dbus.Interface(self.proxy,
        'com.majorsilence.MessageInterface')
    self.bus.add_signal_receiver(self.on_message_recieved,
        dbus_interface="com.majorsilence.MessageInterface",
        signal_name="message_signal")
```

As can be seen, connect to the bus name com.majorsilence.MessageSerive using the objec path /TestObject. Next the interface is created using self.proxy and the interface com.majorsilence.MessageInterface. Finally the signal message\_signal is handled by connecting it to the self.on\_message\_recieved method when it is emitted from the com.majorsilence.MessageInterface interface.

```python
    win = gtk.Window()
    win.connect("delete_event", lambda w,e:gtk.main_quit())
    vbox = gtk.VBox()
    hbox = gtk.HBox()

    self.text_message=gtk.Entry()
    set_message=gtk.Button("Set Message")
    display_message=gtk.Button("Display Welcome Message")
    set_message.connect("clicked", self.on_set_message_clicked)

    display_message.connect("clicked",
        self.on_display_message_clicked)

    hbox.pack_start(set_message, False, True, 0)
    hbox.pack_start(display_message, False, True, 0)
    vbox.pack_start(self.text_message, False, True, 0)
    vbox.pack_start(hbox, False, True, 0)
    win.add(vbox)
    win.show_all()

  def on_message_recieved(self):
    print "message_signal caught"
```

When the signal is emitted it does nothing prints a message to the console.

```python
  def on_set_message_clicked(self, widget):
    message = self.text_message.get_text()
    self.control_interface.set_message(message)
```

When the set message button is clicked it grabs the text from the text entry and uses the self.control\_interface to set the label in the serve appliction to whatever text was typed in.

```python
  def on_display_message_clicked(self, widget):
    print self.control_interface.display_welcome_message()
```

When the display message button is clicked it calls the exposed method display\_welcome\_message() which is a method with a predfined message that is displayed to the DBus service applications label.

```python
if __name__ == "__main__":
  app = DBusClient()
  gtk.main()
```

The code to to actually run the example.

## Finding Exposed Methods {#sec-dbus-finding-exposed-methods}

Now you are asking yourself "it is all good and well that I can access functionalty throught DBus, but how do I find what is available?". Well this is actionally fairly simple and is accomplished using introspection. Basically form is

```python
your_interface.Introspect(dbus_interface='org.freedesktop.DBus.Introspectable')
  def list_available_commands(self):
```

Here is an example using rhythmbox. It lists all the available methods, signals and properties of the interface that is used. It is printed as xml as that is the form that DBus uses.

```python
import gobject, dbus
from dbus.mainloop.glib import DBusGMainLoop

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
proxy_object = bus.get_object('org.gnome.Rhythmbox',
    '/org/gnome/Rhythmbox/Player')
player = dbus.Interface(proxy_object,
    'org.gnome.Rhythmbox.Player')
print player.Introspect(dbus_interface=
        'org.freedesktop.DBus.Introspectable')
```

That is all that is to it, very simple, very easy.

## Types {#sec-dbus-types}

When using introspection a print out of the xml will be displayed, for instance a piece of it may look like this.

```xml
<method name="playPause">
  <arg name="arg0" type="b" direction="in"/>
</method>
```

What this small piece means is that there is a method that is available called *playPause*. It takes one argument. Its type is b meaning it is a boolean. The direction is in, meaning it recieves input, if the direction is out is returns a value.

It is important to know what the different types are so here is a list.

b
: dbus.Boolean, bool

d
: dbus.Double, float

g
: dbus.Signature

i
: dbus.Int32, int

n
: dbus.Int16

o
: dbus.ObjectPath

q
: dbus.UInt16

s
: dbus.String, dbus.UTF8String, str, unicode

t
: dbus.UInt64

u
: dbus.UInt32

x
: dbus.Int64, long

y
: dbus.Byte

DBus also supports for container types.

ax dbus.Array, list
: a is an array and the x is the type that is used. X here means it is an array of dbus.UInt64/long

ay dbus.ByteArray, str
: Is a more effienct array

(types) dbus.Struct, tuple
: The signature of is either None or a string representing the contents of the struct. The signature '(iis)' would be used for two integers and a string.

a{xy} dbus.Dictionary, dict
: a is the key and y is the value. So a{si} would be a dictionary with strings for keys and integers for values.

v
: variants

## Summary

Although you are probably not a DBus expert from this chapter, it should have given you a good enough understanding to start accessing other applications and add some basic support to your own application. What you need to do is experiment a little and make sure that you fully understand DBus and maybe read up on it a little more.

Some other resources that you may want to check out are:

- <http://dbus.freedesktop.org/doc/dbus-python/doc/tutorial.html>
- <http://dbus.freedesktop.org/doc/dbus-python/>
- <http://dbus.freedesktop.org/doc/dbus-python/api/index.html>
- <http://www-128.ibm.com/developerworks/linux/library/l-dbus.html>
- <http://www.madsoft.org/2008/06/10/interfacing-banshee-10-with-dbus-and-python/>
- <http://mumble.sourceforge.net/DBus>
