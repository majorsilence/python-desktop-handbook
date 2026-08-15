---
layout: chapter
title: "Audio and Video Playback - GStreamer"
number: 6
---

> Please send any fixes or suggestions to peter@majorsilence.com or leave a comment at http://www.majorsilence.com/pygtk\_book.

## Introduction

GStreamer is a multimedia framework that can be used from the simple to the more advanced. The possibilities range from playing a simple audio file or video file to creating an advanced audio/video editor.

When you are finished reading this chapter you will be able to use a high level playbin factory element to play audio and video, detect missing codecs and automatically install them, discover the file information about your audio or video files and apply all these to your very own PyGTK program.

This chapter does not cover any advanced topics but it does show you how to very quickly add the ability to play audio or video to your own program.

Enjoy the journey.

## The Beginnings

### Playbin

The playbin element is a very high level, automatic video/audio player. It will automatically detect your multimedia file type and take the correct actions for it to be played. All that needs to be done to use it is to supply the playbin with a location of a multimedia file and set the state of it to play.

**playbin Features:**

- Audio and video output ("audio-sink" and "video-sink")
- Error Handling
- EOS handling(end of stream)
- State handling
- Seeking
- Buffers network sources
- Visualization for audio supported
- Subtitle support ("suburi")

**Playbin element:**

What is needed in every GStreamer application is an element to play your media with. In the case of this chapter all that we are going to use is the "playbin" factory. You create this using the gst.element\_make\_factory(factory, element\_name) method like so:

```python
player_name = gst.element_make_factory("playbin", "YourElementName")
```

**Set location of the multimedia file:**

Setting the location of the file is done with the player\_name.set\_property("uri", "location") like so:

```python
player_name.set_property("uri", "file:///home/peter/myvideo.avi")
```

**Set state of the multimedia file:**

Some states that the multimedia file may be set to include:

- gst.STATE\_PLAYING -- Used to start playing
- gst.STATE\_PAUSED -- Used to pause file
- gst.STATE\_NULL -- Used to stop file

To set the state of the "player\_name" just created above to play the file you would set\_state(state) method like so:

```python
player_name.set_state(gst.STATE_PLAYING)
```

To set the file to be paused you would:

```python
player_name.set_state(gst.STATE_PAUSED)
```

To altogether stop the file that is playing you would set the state like so:

```python
player_name.set_state(gst.STATE_NULL)
```

### Bus - watching for GStreamer signals

The GStreamer bus is what allows for receiving signals from GStreamer. It is important because it will allow your program to detect things such as errors or the end of the audio or video stream.

When the end of stream is detected it is the programs responsibility to set the state back to gst.STATE\_NULL. Otherwise if you try to load in another file or play the same file again it will not play because the state is already set to gst.STATE\_PLAYING.

The bus is not difficult to use and it will only add a few more lines to the program and one extra function to handle the messages.

So if we have created a player bin using the gst.element\_make\_factory method and have called it `player_name` then we can create a bus and watch it like so:

```python
bus = player_name.get_bus()
bus.add_signal_watch()
bus.connect("message", on_message)
```

This creates a bus from the player\_name playbin, adds a signal watcher, and connects the bus to send signals to the function on\_message when messages are detected.

The function message can detect whatever type of message that GStreamer has but in the examples in this chapter it will focus on errors and detecting when the end of stream has occurred so that the program will reset the state to gst.STATE\_NULL.

An example message function looks like this:

```python
def on_message(self, bus, message):
    # Detect end of stream and set state to to NULL
    if message.type == gst.MESSAGE_EOS:
        self.player_name.set_state(gst.STATE_NULL)
    elif message.type == gst.MESSAGE_ERROR:
        self.player_name.set_state(gst.STATE_NULL)
        (err, debug) = message.parse_error()
        print "Error: %s" % err, debug
```

## Playing Audio

Playing audio with PyGST is a very simple matter that only requires a few lines of code to get the audio playing.

As the was just covered we will use the gst.element\_make\_factory function and set it up with a PyGTK GUI. But besides that we will create a false video sink using the gst.element\_make\_factory function so that if the multimedia file is a video, only the audio portion is played. This is because we are using the high level "playbin" element which will automatically play everything. So if all you want played is the audio, the video must be redirected.

Create a multimedia playbin to play the audio and redirect all video to a fake video sink that is added to the multimedia pipeline:

```python
# Create the player_name sink
player_name = gst.element_make_factory("playbin", "Multimedia Player")
# Create the fake video sink
fake_video_sink = gst.element_make_factory("fakesink", "Fake sink for Videos")
#Add the fake video sink to the player
player_name.set_property("videosink", fake_video_sink)
```

If a fake video sink is not created and a video file is played ,it will pop up a window with the video playing in it. This will really subtract from the professional feel of your application.

Now what is needed is to add the audio source using the player\_name.set\_property method and set the state to playing. This is just like what is discussed earlier and is now shown below:

```python
player_name.set_property("uri", "file:///home/peter/mymusic.mp3")
player_name.set_state(gst.PLAYING)
```

It really is that simple.

For a full example of how to hook up audio and video to a PyGTK application please review the example at the end of the chapter.

## Playing Video

Playing audio is very simple and is much like playing audio except that with playing video there is no fake video sink created to hide the video.

To play video a playbin must be created using the gst.element\_make\_factory function. Then set the location of the video file with the newly created playbin and then set the playbin state to gst.PLAYING.

```python
# Create the player_name sink
player_name = gst.element_make_factory("playbin", "Multimedia Player")
# Set the location of the video file
player_name.set_property("uri", "file:///home/peter/myvideo.avi")
# Start playing the video.
player_name.set_state(gst.PLAYING)
```

It really is much shorter to play a video then it is an audio file. But remember that you should also hook up a bus, as shown in the section "bus -- watching for GStreamer signals", to your video to catch messages. However there is a problem with this code.

If you play a video with this code the video will open up in its own window. If the video opening in its own window is good enough for your program so be it; however I believe that for most programs the video will be better suited in a widget inside of the application.

### **Play the Video in you Application**

To play a video file in your own application you use a gtk.DrawingArea widget to play the video. You create a gtk.DrawingArea and sync it with the video using the bus that has been created to watch for GStreamer messages.

Create your gtk.DrawingArea like so:

```python
self.videowidget = gtk.DrawingArea()
self.videowidget.set_size_request(400, 250)
```

Then add this widget to your PyGTK window.

Now you sync the video to your videowidget using the bus. If your bus name is *bus* you would enable sync messages and connect it to a function with the following code:

```python
bus.enable_sync_message_emission()
bus.connect("sync-message::element", self.on_sync_message)
```

This code enables the sync message and then connects any signals to be forwarded to the `self.on_sync_message` function. The on\_sync\_message function will hook the video up to the gtk.DrawingArea widget that has been created to show the video.

Here is an example function showing how to play a video.

```python
def on_sync_message(self, bus, message):
    if message.structure is None:
        return False
    if message.structure.get_name() == "prepare-xwindow-id":
        if sys.platform == "win32":
            win_id = self.videowidget.window.handle
        else:
            win_id = self.videowidget.window.xid

        assert win_id
        imagesink = message.src
        imagesink.set_property("force-aspect-ratio", True)
        imagesink.set_xwindow_id(win_id)
```

Now when the state of your playbin element is set to play using gst.PLAYING, the video will be played inside of your application instead of opening up in its own window.

For a full example of how to hook up audio and video to a PyGTK application please review the example at the end of the chapter.

### Play Video Example

This example will be referred to in following sections and when adding things such as seeking and will be expanded upon in the file example at the end of the chapter.

<a id="simple-video-player-example"></a>

```python
#!/usr/bin/env python
import pygst
pygst.require("0.10")
import gst, pygtk, gtk
import sys

class Main(object):
    def __init__(self):
        self.multimedia_file=""
        # Create the GUI
        self.win = gtk.Window()
        self.win.set_title("Play Video Example")
        self.win.connect("delete_event",
            lambda w,e: gtk.main_quit())

        vbox = gtk.VBox(False, 0)
        hbox = gtk.HBox(False, 0)
        self.load_file =
            gtk.FileChooserButton("Choose Audio File")
        self.play_button =
            gtk.Button("Play", gtk.STOCK_MEDIA_PLAY)
        self.pause_button =
            gtk.Button("Pause", gtk.STOCK_MEDIA_PAUSE)
        self.stop_button =
            gtk.Button("Stop", gtk.STOCK_MEDIA_STOP)
        self.videowidget = gtk.DrawingArea()
        # You want to expand the video widget or
        # else you cannot see it
        self.videowidget.set_size_request(400, 250)

        self.load_file.connect("selection-changed",
            self.on_file_selected)
        self.play_button.connect("clicked", self.on_play_clicked)
        self.pause_button.connect("clicked", self.on_pause_clicked)
        self.stop_button.connect("clicked", self.on_stop_clicked)

        hbox.pack_start(self.play_button, False, True, 0)
        hbox.pack_start(self.pause_button, False, True, 0)
        hbox.pack_start(self.stop_button, False, True, 0)
        vbox.pack_start(self.load_file, False, True, 0)
        vbox.pack_start(self.videowidget, True, True, 0)

        vbox.pack_start(hbox, False, True, 0)
        self.win.add(vbox)
        self.win.show_all()

        # Setup GStreamer
        self.player = gst.element_factory_make(
            "playbin", "MultimediaPlayer")
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        #used to get messages that GStreamer emits
        bus.connect("message", self.on_message)
        #used for connecting video to your application
        bus.connect("sync-message::element",
            self.on_sync_message)

    def on_file_selected(self, widget):
        self.multimedia_file = self.load_file.get_filename()

    def on_play_clicked(self, widget):
        self.player.set_property('uri',
            "file://" + self.multimedia_file)
        self.player.set_state(gst.STATE_PLAYING)

    def on_pause_clicked(self, widget):
        self.player.set_state(gst.STATE_PAUSED)

    def on_stop_clicked(self, widget):
        self.player.set_state(gst.STATE_NULL)

    def on_message(self, bus, message):
        if message.type == gst.MESSAGE_EOS:
            # End of Stream
            self.player.set_state(gst.STATE_NULL)
        elif message.type == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            (err, debug) = message.parse_error()
            print "Error: %s" % err, debug

    def on_sync_message(self, bus, message):
        if message.structure is None:
            return False
        if message.structure.get_name() == "prepare-xwindow-id":
            if sys.platform == "win32":
                win_id = self.videowidget.window.handle
            else:
                win_id = self.videowidget.window.xid
            assert win_id
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_xwindow_id(win_id)

if __name__ == "__main__":
    Main()
    gtk.main()
```

## Multimedia Info

Now what I should mention here is that this code is more or less the unmodified example that comes with the PyGST source code. Copyright (C) 2006 Andy Wingo, LGPL Version 2.

Lets say that you are going to play a video and you want to know some information about it. Maybe you want to know what the video width and height is to set a proper size on your video widget. Or maybe you want to know the length of the video. Well this information is very easy to find out using GStreamer.

First you will have to import the GStreamer discoverer like so:

```python
from gst.extend import discoverer
```

Now that you have the discoverer imported you can access information about the video file with only a few lines of code.

We create a discover function that will be the main work area that hooks everything together.

The discover functions includes an in-line function that is connected to using a gobject main loop since this is a command line example. If this code is used in a PyGTK GUI it will will run fine without the gobject main loop because it is already running in the applications GTK main loop.

If the the file is discovered to be a multimedia file it is then sent to the succeed function where it prints out information about the file.

If it fails and is not recognized as a multimedia file then it prints out an error message and exits the gobject main loop.

```python
def discover(path):
    def discovered(d, is_media):
        if is_media:
            succeed(d)
        else:
            print "error: %r does not appear to be a media file" % path
            # Exit the gobject main loop
            # Remove this in a pygtk program.
            sys.exit(1)

    d = discoverer.Discoverer(path)
    # Connect discovered to the inline function discovered.
    d.connect("discovered", discovered)
    d.discover()
    # comment out the gobject.MainLoop.run() in a pygtk program.
    gobject.MainLoop().run()
```

The succeed method is called from the discover function when the file is detected as a multimedia file. It can be used to print out or save information about the video or audio file.

Data available for video files include:

- is\_video
- video\_length
- fps - videorate.num / videorate.denom
- videocaps
- videowidth
- videoheight

Data available for audio files include:

- is\_audio
- audiocaps
- audiofloat
- audiorate
- audiowidth
- audiodepth
- audiolength
- audiochannels

```python
def succeed(d):
    print("media type", d.mimetype)

    print("has video", d.is_video)
    if d.is_video:
        print("video length (ms)", d.videolength / gst.MSECOND)
        print("framerate (fps)", "%s/%s" % (d.videorate.num, d.videorate.denom))

    print("has audio", d.is_audio)
    if d.is_audio:
        print("audio caps", d.audiocaps)
        print("audio format", d.audiofloat and "floating-point" or "integer")
        print("audio length (ms)", d.audiolength / gst.MSECOND)
    # Exit gobject main loop.
    sys.exit(0)
```

All that is left is to run the discover file with a path to a multimedia file specified. To read in the file location and do the proper handling of it you could use the following code:

```python
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print >> sys.stderr, "usage: script_name.py PATH-TO-MEDIA-FILE"
        sys.exit(1)
    path = sys.argv.pop()
    if not os.path.isfile(path):
        print >> sys.stderr, "error: file %r does not exist" % path
        print >> sys.stderr, "usage: gst-discover PATH-TO-MEDIA-FILE"
        sys.exit(1)

    discover(path)
```

For a full example of how to retrieve information from an audio or video file from a PyGTK application, please review MediaInfo class in the example at the end of the chapter. Also you can check out the PyGST examples on this books website.

## Codec Buddy - Auto install multimedia Codecs {#sec-gst-codec-buddy}

Tested with Ubuntu 8.10

Taking advantage of the gst.pbutils allows a program to automatically install available codecs or provide the user of the program a choice of actions to take.

```python
#!/usr/bin/python
import pygst, gst, pygtk, gtk
pygst.require("0.10")

class InstallMissingCodecExample(object):
  def __init__(self):
    # Gtk Gui
    self.win = gtk.Window()
    self.win.set_title("Install Missing Codec Example")
    self.win.connect("delete_event", lambda w,e: gtk.main_quit())
    self.load_file = gtk.FileChooserButton("Choose Audio File")
    self.load_file.connect("selection-changed", self.on_file_selected)
    self.win.add(self.load_file)
    self.win.show_all()

    # Setup GStreamer
    self.player = gst.element_factory_make("playbin",
      "MultimediaPlayer")
    bus = self.player.get_bus()
    bus.add_signal_watch()
    bus.connect("message", self.on_message)

  def on_file_selected(self, widget):
    print "Selected: ", self.load_file.get_filename()
    multimedia_file = self.load_file.get_filename()
    self.player.set_property('uri', "file://" + multimedia_file)
    self.play()

  def play(self):
    self.player.set_state(gst.STATE_PLAYING)
    # Codec Buddy Methods

  def on_message(self, bus, message):
    import gst
    if message.type == gst.MESSAGE_ERROR:
      self.player.set_state(gst.STATE_NULL)
      (err, debug) = message.parse_error()
      print "Error: %s" % err, debug
    elif message.type == gst.MESSAGE_EOS:
      # End of Stream
      self.player.set_state(gst.STATE_NULL)
    elif message.type == gst.MESSAGE_ELEMENT:
      """  CodicBuddy Stuff  """
      st = message.structure
      if st and st.get_name().startswith('missing-'):
        self.player.set_state(gst.STATE_NULL)
        if gst.pygst_version >= (0, 10, 10):
          import gst.pbutils
          detail = gst.pbutils.missing_plugin_message_get_installer_detail(message)                 context = gst.pbutils.InstallPluginsContext()
          gst.pbutils.install_plugins_async([detail],
            context, self.install_plugin)

  def install_plugin(self, result):
    if result == gst.pbutils.INSTALL_PLUGINS_SUCCESS:
      gst.update_registry()
      self.play()
      return
    if result == gst.pbutils.INSTALL_PLUGINS_USER_ABORT:
      dialog = gtk.MessageDialog(parent=None,
          flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_INFO,
          buttons=gtk.BUTTONS_OK, message_format=
          "Plugin installation aborted.")
      dialog.run()
      dialog.hide()
      return
    error.show("Error", "failed to install plugins: %s" %
      str(result))

if __name__ == "__main__":
  InstallMissingCodecExample()
  gtk.main()
```

## Seeking - Basic Position Seeking

Seeking allows multimedia software to display the position in the audio or video stream and also may allow the user to skip to a different section of the media file they are watching or listening to.

### Displaying the Current Position

When playing a media file it may be a good idea to display the current position relative to the duration of the file as a courtesy to the user.

Displaying the duration of the file and current time position will require adding two methods to the play video ([Play Video Example](06-audio-and-video-playback-gstreamer.html#simple-video-player-example)) example found earlier in the chapter.

In the \_\_init\_\_ method of the Main class the variables time\_format, duration and is\_playing are added.

```python
self.time_format = gst.Format(gst.FORMAT_TIME)
self.duration = None
self.is_playing = False
```

The time\_format will be used when seeking the the duration of the media file and seeking the current position of the file. The duration will be a string to display the length of the media file. the is\_playing variable will be used to let the methods that are going to soon be added know if the player is playing or not.

The is\_playing variable must be set to False anytime the file is not playing. This includes the end of stream message in the on\_message method and when the pause and stop buttons are clicked.

Further down in the \_\_init\_\_ method a label called time\_label is added and that is it for the GUI changes to display the time.

```python
self.time_label = gtk.Label("00:00 / 00:00")
```

Going through the different methods, besides setting is\_playing to False in the on\_stop\_clicked and on\_pause\_clicked methods, in the on\_play\_clicked it must be set to True. But after setting it to playing by clicking the play button the application must be able to update the GUI with the new current position every second.

To update the GUI every second the on\_play\_clicked button adds the following:

```python
timer = gobject.timeout_add(1000, self.update_time_label)
```

This will create a timer that is executed every one second calling the method update\_time\_label. It will execute every one second as long a update\_time\_label returns true.

Skipping down to below the on\_sync\_message method there is the new function update\_time\_label.

```python
def update_time_label(self):
  """
  Update the time_label to display the current location
  in the media file as well as update the seek bar
  """
  if self.is_playing == False:
    print "return false"
    return False
  print "update_time_label"
  if self.duration == None:
    try:
      self.length = self.player.query_duration(self.time_format, None)[0]
      self.duration = self.convert_time(self.length)
    except:
      self.duration = None

  if self.duration != None:
    self.current_position = self.player.query_position(self.time_format, None)[0]
    current_position_formated = self.convert_time(self.current_position)
    self.time_label.set_text(current_position_formated + "/" + self.duration)

    # Update the seek bar
    # gtk.Adjustment(value=0, lower=0, upper=0, step_incr=0, page_incr=0, page_size=0)
    percent = (float(self.current_position)/float(self.length))*100.0
    adjustment = gtk.Adjustment(percent, 0.00, 100.0, 0.1, 1.0, 1.0)       self.seeker.set_adjustment(adjustment)

  return True
```

If the `is_playing` variable is set to False the `update_time_label` method will return False. This method starts to be called when the play button is called and is called every one second until it returns False.

If the duration of the file has not yet been set it will be set here. The duration is found in nanoseconds and is converted to a string by passing it into the convert\_time method. The duration variable will be reset to None each time a new media file is added to be played. If the duration is not None then it never set again unless a new file is loaded.

After duration of the file is found the `current_position` variable is calculated every time the `update_time_label` is called. The current position is found the same was as the duration except that the `query_position` function is used. Then the time in nanoseconds is converted to a person understandable string.

Once the duration and the current position is found it is displayed to the user by setting the text of the time\_label like so:

```python
self.time_label.set_text(current_position_formated + "/" + self.duration)
```

As was just discussed above, the convert\_time function is used to convert the time of the media file from nanoseconds to human readable string. This code is adapted from a tutorial[^1] found on the PyGST documentation site. It takes the time in nanoseconds and converts it to human readable string in the format of HH::MM::SS and then returns it.

```python
def convert_time(self, time=None):
  # convert_ns function from:
  # http://pygstdocs.berlios.de/pygst-tutorial/seeking.html
  # LGPL Version 3 - Copyright: Jens Persson
  if time==None:
    return None

  hours = 0
  minutes = 0
  seconds = 0
  time_string = ""

  time = time / 1000000000 # gst.NSECOND

  if time >= 3600:
    hours = time / 3600
    time = time - (hours * 3600)
  if time >= 60:
    minutes = time / 60
    time = time - (minutes * 60)
  #remaining time is seconds
  seconds = time

  time_string = time_string + str(hours).zfill(2) + ":" +
      str(minutes).zfill(2) + ":" + str(seconds).zfill(2)

  #return time in Hours:Minutes:Seconds format
  return time_string
```

If the time passed in is None it immediately returns None. The method divides the passed in time by 1 000 000 000 and then proceeds to calculate the hours, minutes, and seconds; creating a nice string HH:MM:SS to view by a human.

When the time\_string has been completed it is returned to be used by the user interface.

### Seeking a New Position

Like displaying the position and duration, seeking a new position in a media file will use the methods convert\_time as well as update\_time\_label, but it will also use a horizontal scaler to that it will let the user slide to a new position.

To allow a user to update the position of the media file a horizontal scaler needs to be added. To use a scaler you must create an adjustment first.

```python
self.adjustment = gtk.Adjustment(0.0, 0.00, 100.0, 0.1, 1.0, 1.0)
```

This creates a new adjustment with a starting value of 0, lower limit of 0.00, upper limit of 100.0, and step increment of 0.1, page increment of 1.0, and page size of 1.0. The adjustment is used with the the horizontal scaler that is to be created to control the place in the media file.

```python
self.seeker = gtk.HScale(self.adjustment)
self.seeker.set_draw_value(False)
self.seeker.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
```

The first line creates the seeker and the set\_draw\_value(False) line keeps the format-value signal from being admitted and the value of the current position is not displayed.

On the third line the seeker is set to update in a discontinuous way. What this means is that it will only be updated when a button-release-event signal is emitted.

The new method being added for seeking is seeker\_button\_release\_event and the signals is connected like this:

```python
self.seeker.connect("button-release-event", self.seeker_button_release_event)
```

When the scaler button is released this method is called and the media file is set to a new position.

```python
def seeker_button_release_event(self, widget, event):
    print "seeker_button_release_event"
    value = widget.get_value()
    if self.is_playing == True:
        duration = self.player.query_duration(self.time_format, None)[0]
        time = value * (duration / 100)
        print self.convert_time(time)
        self.player.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, time)
```

When the self.seeker is released, its current position is retrieved and the position to reposition the media file is calculated.

```python
time = value * (duration / 100)
```

After the new position is determined, the media file is set to it using the seek\_simple function. The seek\_simple function takes a GStreamer time format, a seek flag, and the new time[^2], returning True if it succeeds.

## Volume Control

Adding the option to control the volume of audio or video from individual programs is accomplished using the gtk.VolumeButton.

A volume button is created like any other widget in PyGTK.

```python
volume_button = gtk.VolumeButton()
```

Then hook the volume button up to the value-changed signal with a method to control the volume.

```python
volume_button.connect("value-changed", self.on_volume_changed)
```

The last piece to complete is to create the method that is being used to increase and decrease the volume.

```python
def on_file_selected(self, widget, value=0.5)
    self.player.set_property("volume", float(value))
    return True
```

What this method does is to control the volume and increase by the percent raised on the volume slider. The default value is 0.5 if it is not specified.

### Volume Control Example

```python
class Main(object):
    def __init__(self):
        self.win = gtk.Window()
        self.win.set_title("Volume Control Example")
        self.win.set_default_size(200, -1)
        self.win.connect("delete_event", lambda w,e: gtk.main_quit())

        hbox = gtk.HBox(False, 0)
        self.load_file = gtk.FileChooserButton("Choose Audio File")\
        self.load_file.connect("selection-changed", self.on_file_selected)
        volume_button = gtk.VolumeButton()
        volume_button.connect("value-changed", self.on_volume_changed)

        hbox.pack_start(self.load_file, True, True, 0)
        hbox.pack_start(volume_button, False, True, 0)
        self.win.add(hbox)
        self.win.show_all()

        self.player = gst.element_factory_make("playbin", "MultimediaPlayer")
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)

    def on_file_selected(self, widget):
        self.player.set_property("uri", "file://" + self.load_file.get_filename())
        self.player.set_state(gst.STATE_PLAYING)

    def on_volume_changed(self, widget, value=10):
        self.player.set_property("volume", float(value))
        return True

    def on_message(self, bus, message):
        if message.type == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
        elif message.type == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            (err, debug) = message.parse_error()
            print "Error: %s" % err, debug

if __name__ == "__main__":
    Main()
    gtk.main()
```

## Example

The purpose of this section is to provide a full media example that includes a user interface written with PyGTK. The application will be able to play, pause, or stop audio and video. Also the program will be able to discover information about the media file such as its length, width and height, and audio format using the MediaInfo class.

Using the information found with the MediaInfo class the user interface will be able to resize its video display to match the width and height of the video.

The GstPlayer class will wrap the GStreamer functions to make it easy to separate the multimedia and user interface functionality. The user interface will use a separate class called VideoWidget to display the video in also to make it easier to reuse.

### MediaInfo Class

The MediaInfo class is very similar to the media info section covered earlier in the chapter. What the MediaInfo class does here is to create an easy to use wrapper around the GStreamer discoverer functions, providing accessor methods to the data.

Though there are many different pieces of information that can be discovered about a media file, for this example it will be kept short. For more information on the different variables that can be used to access the information please refer to the *multimedia info* section earlier in this chapter.

The only information that is of interest at the moment is if the media file is audio or video. If it is a video file, the width and the video height is of interest. If seeking is involved then the length of the file is also of interest, but this is not covered in this example.

```python
class MediaInfo:
    def __init__(self, path):
        def discovered(d, is_media):
            if is_media:
                self.succeed(d)
            else:
                self.fail(path)
        self.__finished = False
        self.__is_media=False
        self.__video_width = 0
        self.__video_height = 0
        self.__is_video = False
        self.__is_audio = False
        self.__video_length = 0.0
        self.__frame_rate = ""

        self.__is_fullscreen = False
        print "path: ", path

        d = discoverer.Discoverer(path)
        #print help(d.discover)
        d.connect("discovered", discovered)
        d.discover()

    def fail(self, path):
        print "error: %r does not appear to be a media file" % path
        self.__is_media = False

    def succeed(self, d):
        print "File discover success"
        self.__is_media = True
        self.__mimetype = d.mimetype
        self.__is_video = d.is_video
        if self.__is_video:
            self.__video_width = d.videowidth
            self.__video_height = d.videoheight
            # Retrieve the video length in minute
            self.__video_length = ((d.videolength / gst.MSECOND) / 1000) / 60
            self.__frame_rate = "%s/%s" % (d.videorate.num, d.videorate.denom)

        self.__finished = True

    def poll(self):
        return self.__finished

    def is_media(self):
        return self.__is_media

    def is_video(self):
        return self.__is_video

    def is_audio(self):
        return self.__is_audio

    def get_width(self):
        return self.__video_width

    def get_height(self):
        return self.__video_height
```

The MediaInfo class starts off by creating an inline function called discovered which is called by connecting the *discovered* signal, near the end of the init function, to the *discovered* function. The init function also creates sever class instance variables that is used to store information about the media file.

If the file loaded is detected as being a media file it is sent to the method *succeed*. If the file is not a media file the fail method is called, an error message is printed to the console, and the class variable self.\_\_is\_media is set to false indicating the file is not a media file.

If the succeed method is called it will set the class variable self.\_\_is\_media to true. It will then set the mime type using the variable self.\_\_mimetype. It will check to see if the media file is an audio file or a video file. It will set self.\_\_is\_video to true if it is a video file.

The height and width of a video file is stored respectively in the variables self.\_\_video\_height and self.\_\_video\_width.

Then there are a few methods to retrieve these variables that are of interest to the programmer. The methods return the variables that are obviously in their names. get\_height() returns self.\_\_video\_height and so on with the other methods.

The only other method that is included is the *poll* method. Since the discovery of media information is not instantaneous, if you attempt to use any of the get methods to retrieve information such as the height or width of a video, it may return the initialization values of the variables which is zero.

The *poll* method will return True when the *succeed* method has finished, indicating that all the variables have been assigned.

If the poll method returns False you must wait to use the information provided by the MediaInfo class.

### GstPlayer Class

The GstPlayer class is used to control the GStreamer instance, watch the bus, handle GStreamer errors and messages, and sync the GStreamer video to video widget created with the VideoWidget class below.

```python
class GstPlayer(object):
    def __init__(self, videowidget):
        # Setup GStreamer
        self.videowidget = videowidget
        self.player = gst.element_factory_make("playbin", "MultimediaPlayer")

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        #used to get messages that gstreamer emits
        bus.connect("message", self.on_message)
        #used for connecting video to your application
        bus.connect("sync-message::element", self.on_sync_message)

    def set_location(self, location):
        self.player.set_property("uri", "file://" + location)

    def play(self):
        print "playing"
        self.player.set_state(gst.STATE_PLAYING)

    def pause(self):
        print "paused"
        self.player.set_state(gst.STATE_PAUSED)

    def stop(self):
        print "stoped"
        self.player.set_state(gst.STATE_NULL)

    def on_message(self, bus, message):
        if message.type == gst.MESSAGE_EOS: # End of Stream
            self.player.set_state(gst.STATE_NULL)
        elif message.type == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            (err, debug) = message.parse_error()
            print "Error: %s" % err, debug

    def on_sync_message(self, bus, message):
        if message.structure is None:
            return False
        if message.structure.get_name() == "prepare-xwindow-id":
        self.videowidget.set_sink(message.src)
        message.src.set_property("force-aspect-ratio", True)
```

The GstPlayer class starts off with a video widget being passed in. This video widget is used to sync the GStreamer video with. After this the GStreamer pipeline is created using gst.element\_factory\_make using the *playbin* element and with the identifier MultimediaPlayer.

```python
self.player = gst.element_factory_make("playbin", "MultimediaPlayer")
```

Next a bus is created to be used with the pipeline and signal watching is added. Signals are connected to the self.\_on\_message method.

```python
bus = self.player.get_bus()
bus.add_signal_watch()
bus.connect("message", self.on_message)
```

After this is used the enable\_sync\_message\_emission() method on the bus to enable the player to sync the GStreamer video with the video widget that is being used. If this is not done, a separate window will be opened that is outside of the running application to play the video in. The sync emissions signals are directed to the self.on\_sync\_message method.

```python
bus.enable_sync_message_emission()
bus.connect("sync-message::element", self.on_sync_message)
```

The on\_sync\_message method uses the video widget that has been passed in during the initialization of GstPlayer to attach the video to the application. This is a little hocus pocus that I am not really sure of what is happening. It seems to be communicating somewhat with the underlying X Windows about the window id.

Then the set\_sink method that is in video widget class is set to the message src. The set\_sink method is used for convenience. The VideoWidget class that is discussed in the next section.

The very last part is to set force the aspect ratio of the video.

```python
def on_sync_message(self, bus, message):
    if message.structure is None:
        return False
    if message.structure.get_name() == "prepare-xwindow-id":
        self.videowidget.set_sink(message.src)
        message.src.set_property("force-aspect-ratio", True)
```

The rest of what is covered by the GstPlayer class is very self explanatory. A *play*, *stop*, and *pause* method to play, pause, or stop the media file. And there is also a method call `set_location` that sets the location of the media file that is to be played.

### VideoWidget

The VideoWidget class is a subclass of gtk.DrawingArea. It is created to ease the use of displaying videos inside of applications and is used in conjunction with the user interface and GstPlayer class.

```python
class VideoWidget(gtk.DrawingArea):
"""
    Extend gtk.DrawingArea to create our own video widget.
"""
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.imagesink = None
        self.unset_flags(gtk.DOUBLE_BUFFERED)

    def do_expose_event(self, event):
        if self.imagesink:
            self.imagesink.expose()
            return False
        else:
            return True

    def set_sink(self, sink):
        if sys.platform == "win32":
            win_id = self.window.handle
        else:
            win_id = self.window.xid

        assert win_id
        self.imagesink = sink
        self.imagesink.set_xwindow_id(win_id)
```

VideoWidget starts off with the initialization of the DrawingArea parent class. It then proceeds to set the imagesink to none. Last in the initialization is to unset the double buffering.

The set\_sink method asserts that the window xid is available and then proceeds to set the imagesink to the sink that is passed in. The sink is passed in from the GstPlayer class. Then while still in the set\_sink method the imagesink sets the id of the xwindow to self.window.xid.

With the VideoWidget class now completed it is simple to use to display videos. To use it with a PyGTK application you would just initialize in your PyGTK GUI code like so:

```python
videowidget = VideoWidget()
```

### User Interface

A good user interface is required to make the ability to play media files useful. The user interface will allow the user to interact with the program, open audio or video files, and if the file is a video then resize it to fullscreen.

```python
class Main(object):
    """
    The Main class is the Gui. It creates an instance of the
    GstPlayer class and the FileInfo class. It is what the user
    interacts with and controls what happens.
    """
    def __init__(self):
        #Store the location of the multimedia file
        self.multimedia_file = None
        # To be used with the FileInfo Class
        self.file_info = None

        # Create the GUI
        self.win = gtk.Window()
        self.win.set_title("Play Video Example 2")
        self.win.connect("delete_event", lambda w,e:
             gtk.main_quit())
        vbox = gtk.VBox(False, 0)
        self.control_box = gtk.HBox(False, 0)

        # Control Buttons
        self.load_file_button = gtk.FileChooserButton(
            "Choose Audio File")
        self.play_button = gtk.Button("Play",
            gtk.STOCK_MEDIA_PLAY)
        self.pause_button = gtk.Button("Pause",
            gtk.STOCK_MEDIA_PAUSE)
        self.stop_button = gtk.Button("Stop", gtk.STOCK_MEDIA_STOP)

        # Video Widget Stuff
        self.videowidget = VideoWidget()
        self.videowidget.set_size_request(400, 250)

        # Signals and Callbacks
        self.load_file_button.connect("selection-changed",
            self.on_file_selected)
        self.play_button.connect("clicked", self.on_play_clicked)
        self.pause_button.connect("clicked", self.on_pause_clicked)
        self.stop_button.connect("clicked", self.on_stop_clicked)

        # Fullscreen stuff
        self.win.connect("key-press-event",
            self.on_win_key_press_event)
        self.win.connect("window-state-event",
            self.on_window_state_event)

        self.control_box.pack_start(self.play_button,
            False, True, 0)
        self.control_box.pack_start(self.pause_button,
            False, True, 0)
        self.control_box.pack_start(self.stop_button,
            False, True, 0)
        vbox.pack_start(self.load_file_button, False, True, 0)
        vbox.pack_start(self.videowidget, True, True, 0)

        # You want to expand the video widget or else you
        #cannot see it
        vbox.pack_start(self.control_box, False, True, 0)
        self.win.add(vbox)
        self.win.show_all()
        self.gst_player = GstPlayer(self.videowidget)

    def fullscreen_mode(self):
        """
        Called from the on_win_key_press_event method. If the
        program is in fullscreen this method will unfullscreen
        it. If the program is not in fullscreen it will set it
        to fullscreen. This method will also hide the controls
        while in fullscreen mode.
        """
        if self.__is_fullscreen:
            self.win.unfullscreen()
            self.control_box.show()
            self.load_file_button.show()
        else:
            self.control_box.hide()
            self.load_file_button.hide()
            self.win.fullscreen()

   def on_win_key_press_event(self, widget, event):
        """
        Handle any key press event on the main window.
        This method is being used to detect when the ESC key
        is being pressed in fullscreen to take the
        window out of fullscreen
        """
        key = gtk.gdk.keyval_name(event.keyval)
        if key == "Escape" or key == "f":
            self.fullscreen_mode()

   def on_window_state_event(self, widget, event):
        """
        Detect window state events to determine whether in
        fullscreen or not in fullscreen
        """
        self.__is_fullscreen = bool(event.new_window_state &                                       gtk.gdk.WINDOW_STATE_FULLSCREEN)
        print "Is fullscreen: ", self.__is_fullscreen

    def on_file_selected(self, widget):
        print "Selected: ", self.load_file_button.get_filename()
        self.multimedia_file = self.load_file_button.get_filename()

        # Do not call method from here immediately.
        # FileInfo.poll() will return false when it is ready.
        # Usually a second or two.
        self.file_info = MediaInfo(self.multimedia_file)
        self.gst_player.set_location(
             self.multimedia_file )

    def on_play_clicked(self, widget):
        print "play clicked"
        print "Video (width, height): ",
            self.file_info.get_width(),
            self.file_info.get_height()

        self.videowidget.set_size_request(
            self.file_info.get_width(),
            self.file_info.get_height() )

        self.gst_player.play()

    def on_pause_clicked(self, widget):
        print "pause clicked"
        self.gst_player.pause()

    def on_stop_clicked(self, widget):
        print "stop clicked"
        self.gst_player.stop()

if __name__ == "__main__":
    Main()
    gtk.main()
```

The Main class starts off by initializing a few variables and creating the required user interface code.

The multimedia\_file is set to None and will store the location of the media file that is to be played.

The file\_info variable is set to None and will be later used to initialize the MediaInfo class.

After declaring the first class instance variables the Main class creates the user interface, sets the title to "Play Video Example 2", and adds a few buttons to play, pause, and stop the video. It also adds a gtk.FileChooserButton video to select the media files that will be played.

Next it creates a video widget using the VideoWidget class that was described above.

At the very bottom of the of the \_\_init\_\_ method the class variable self.gst\_player is initialized as an instance of the GstPlayer class using the self.videowidget instance that was created.

```python
self.gst_player = GstPlayer(self.videowidget)
```

On the clicked signal is emitted from the play, pause, or stop button; then the methods on\_play\_clicked, on\_pause\_clicked, and on\_stop\_clicked are called respective to their buttons.

When a file is selected with the load\_file\_button the on\_file\_selected method is called.

In the section of the code commented as full screen stuff it will connect key-press-event signals and window-state-event signals to the on\_win\_key\_press\_event and on\_window\_state\_event methods. The on\_win\_key\_press\_event method will detect if the key pressed is the "F" or "Esc" key and if so call the fullscreen\_mode() method. If it is fullscreen it will unfullscreen the video. If it is not in full screen it will set it to fullscreen.

The on\_window\_state\_event detects changes in the window state. All that it is used for is to set the variable self.\_\_is\_fullscreen to True or false. This variable is used in the method fullscreen\_mode() to either hide the control buttons (play, pause, stop, load\_file) or show them. If the variable is set to False it will set these widgets to be displayed and unfullscreen the video widget. If the self.\_\_full\_screen is True it will hide all the control widgets and set the video widget to fullscreen with self.win.fullscreen().

Next is the on\_file\_selected method. This method is called when the a file selected from the gtk.FileChooserButton load\_file\_button. It stores the location of the file in the variable self.multimedia\_file. After the file location has been stored it is used to create an instance of the MediaInfo class.

```python
self.file_info = MediaInfo(self.multimedia_file)
```

And finally in the on\_file\_selected method the location of the media file is loaded into the the GstPlayer instance self.gst\_player.

```python
self.gst_player.set_location(self.multimedia_file)
```

The on\_play\_clicked method will use the MediaInfo instance self.file\_info to get the width and height of the video and set the size of the self.videowdiget to the correct dimensions to display the video.

After this it will set the video playing by calling the play method in the GstPlayer class:

```python
self.gst_player.play()
```

As with the on\_play\_clicked method the on\_pause\_clicked and on\_stop\_clicked methods will use call the pause and stop methods from the GstPlayer class.

```python
self.gst_player.pause()
self.gst_player.stop()
```

The only thing that is left to do is to make sure the Main class is called and this is accomplished at the bottom of the source code, which detects if this is file is the main file being run and enters the GTK mainloop.

```python
if __name__ == "__main":
    Main()
    gtk.main()
```

## Summary

Basically GStreamer is a very powerful framework with many options available. Even though this chapter only covered a small portion of what is available, as a programmer you should now be able to add audio and video play back to your application.

As well as seek the position of the media file and display the current location and length of the file to the user.

For more information using GStreamer visit the following sites:

1. <http://pygstdocs.berlios.de/> Contains tutorials and documentation on python GStreamer
1. The main C documentation. If you do not know C this may not be of use, but it may, anyway <http://gstreamer.freedesktop.org/data/doc/gstreamer/head/manual/html/index.html>
1. Check out all the examples that come with the PyGST source at <http://webcvs.freedesktop.org/gstreamer/gst-python/examples/>
1. And of course check out the examples that come with this books website <http://www.majorsilence.com/rubbish/pygtk-book/>

[^1]: This is licensed under the LGPL Version 3 and can be found at: <http://pygstdocs.berlios.de/pygst-tutorial/seeking.html>
[^2]: <http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer/html/GstElement.html>
