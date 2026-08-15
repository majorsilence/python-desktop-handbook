---
layout: chapter
title: "Embedded Web Browsers"
number: 9
---

> Please send any fixes or suggestions to peter@majorsilence.com or leave a comment at http://www.majorsilence.com/pygtk\_book.

## Introduction

This chapter is going to explore how a PyGTK application can have the web embedded into them. It will cover using the firefox engine gecko, webkit, and Internet Explorer.

## gtkmozembed

Using gtkmozemebed to embed mozilla firefox inside a PyGTK application is the easiest of the options in this chapter. A browser is initialized and added to the PyGTK window.

What is needed to start off with is to import the needed python modules.

```python
import gtk
import gtkmozembed
```

Along with the browser the application will probably want some buttons to control how the web pages. Included will be a back, forward, refresh, stop, go, and home button. Also there will be a address bar. These will be connect to methods to control their actions.

Web Browser PyGTK Init Method

```python
class ExampleBrowser(object):
  def __init__(self):
    data =
    """
<html><head><title>Hello</title></head> <body> PyGTK using MozEmbed to embed a web browser. </body> </html>
    """
    win = gtk.Window()
    win.set_size_request(800, 600)
    win.connect("delete_event", lambda w,e: gtk.main_quit())

    vbox = gtk.VBox(False, 0)
    control_box = gtk.HBox(False, 0)

    back = gtk.Button("Back")
    forward = gtk.Button("Forward")
    refresh = gtk.Button("Refresh")
    stop = gtk.Button("Stop")
    home = gtk.Button("Home")
    # no limit on address length
    self.address = gtk.Entry(max=0)
    go = gtk.Button("Go")

    control_box.pack_start(back, True, True, 2)
    control_box.pack_start(forward, True, True, 2)
    control_box.pack_start(refresh, True, True, 2)
    control_box.pack_start(stop, True, True, 2)
    control_box.pack_start(home, True, True, 2)
    control_box.pack_start(self.address, True, True, 2)
    control_box.pack_start(go, True, True, 2)

    back.connect("clicked", self.on_back_clicked, None)
    forward.connect("clicked", self.on_forward_clicked, None)
    refresh.connect("clicked", self.on_refresh_clicked, None)
    stop.connect("clicked", self.on_stop_clicked, None)
    home.connect("clicked", self.on_home_clicked, data)
    self.address.connect("key_press_event", self.on_address_keypress)
    go.connect("clicked", self.on_go_clicked, None)

    vbox.pack_start(control_box, False, True, 2) self.browser = gtkmozembed.MozEmbed()
    #gtkmozembed.set_profile_path("/tmp", "foobar")
    vbox.add(self.browser)

    win.add(vbox)
    win.show_all()
    ## self.browser.load_url('http://www.pygtk.org')
    self.browser.render_data(data, long(len(data)), 'file:///', 'text/html')
    # Load file from file system
    #self.browser.load_url('file:///path/to/file/name.html')
```

This code creates a PyGTK window and creates a control box, adds some buttons to the control box and then adds it to the window.

The import part to see though is the gtkmozembed part.

```python
self.browser = gtkmozembed.MozEmbed()
self.browser.render_data(data, long(len(data)), 'file:///', 'text/html')
```

This small piece of code initializes the web browser and leaves the an instance with the name self.browser. It then displays the message, "PyGTK using MozEmbed to embed a web browser".

With newly created browser it is now possible to access all the methods that are available such as going forward, backward, and entering addresses.

Mozilla Callback Methods

```python
def on_back_clicked(self, widget=None, data=None):
  print "Back button clicked."
  if self.browser.can_go_back():
    self.browser.go_back()

def on_forward_clicked(self, widget=None, data=None):
  print "Forward button clicked."
  if self.browser.can_go_forward():
    self.browser.go_forward()

def on_refresh_clicked(self, widget=None, data=None):
  print "Refresh button clicked."
  self.browser.reload(gtkmozembed.FLAG_RELOADNORMAL)

def on_stop_clicked(self, widget=None, data=None):
  print "Stop Button Clicked."
  self.browser.stop_load()

def on_home_clicked(self, widget=None, data=None):
  print "Home Button clicked."
  print "Back button only works on actual pages and not render_data"
  self.browser.render_data(data, long(len(data)), 'file:///', 'text/html')

def on_go_clicked(self, widget=None, data=None):
  print "Go Button Clicked."
  self.browser.load_url(self.address.get_text())
```

These methods should be self explanatory. For example there is the on\_back\_clicked method which checks if the browser is able to go back to a previous page with:

```python
self.browser.can_go_back()
```

If it passes this check, meaning there is a page to go back to, it goes back to the previous page with the following code:

```python
self.browser.go_back()
```

As can be seen with each of the signaled methods, they are just like the on\_back\_clicked methods. They are very easy to use and not much else to that.

### Running a PyGTK Mozembed Application

This section is very important if the gtkmozembed application is *seg faulting*. Depending on which operating system mozembed is being used on it may very well give a *segmentation fault*. This can be very frustrating to deal with if the reason is not known. However since I have run into this problem several times myself on a couple of systems I can give a few hints.

Basically the problem is that some mozilla libraries that are needed cannot be found by the application, so to run the app it needs to be started with a shell script instead of just running the python script.

#### Ubuntu Gutsy

To use gtkmozembed on Ubuntu Gutsy, the path variables LD\_LIBRARY\_PATH and MOZILLA\_FIVE\_HOME must be set. So what should done is create a shell script. For example, create with a shell script with the name mozilla\_embed\_start.sh and put the following code inside:

gtkmozembed Run Script (Gutsy)

```bash
#!/bin/bash
export LD_LIBRARY_PATH=/usr/lib/firefox
export LD_MOZILLA_FIVE_HOME=/usr/lib/firefox
python your_gtkmozembed_application.py
```

Now run this code in the same directory as `your_gtkmozembed_application.py` file and it should run with no segmentation fault.

#### Ubuntu Feisty, Edgy, and Dapper

On Ubuntu Feisty, Edgy, and Dapper the path variable LD\_LIBRARY\_PATH must be set to the firefox library directory.

A shell script must also be created just like for Ubuntu Gutsy.

gtkmozembed Script (Feisty, Edgy, Dapper)

```bash
#!/bin/bash
export LD_LIBRARY_PATH=/usr/lib/firefox
python your_gtkmozembed_application.py
```

Now run this shell script in the same directory as your gtkmozembed application and it should now be running without any segmentation faults.

#### Other Distributions

If you are running a different distribution of Linux or maybe a BSD the variables that need to be set may be different or the path to the firefox libraries may be different.

From here you are on your own. I suggest you try one of the Ubuntu solutions as one of them will probably work as long as you put in the correct firefox library path.

## Internet Explorer

Using Internet Explorer with PyGTK is an interesting exercise that took me quite of bit of web searching before finding how to do this. Because this is not something that I need often I will be using a somewhat modified sample found on a mailing list[^1] .

Just to be clear this is for Microsoft Windows only. In fact the only reason I am writing this here is so I do not forget myself. I once spent several hours creating a custom application for a specific purpose that had the ability to preview output html internally for ease of use. Then only to find out that gtkmozembed is not for windows. But I needed it to run on windows and linux. So here is how I got Internet Explorer to work on windows with PyGTK.

To start, the comtypes package will need to be installed and can be found at: <http://sourceforge.net/projects/comtypes/>. Also pywin32 should be installed.

Once this has been installed Internet explorer can be taken advantage of. First start off by importing the required modules and creating the required ctypes variables.

```python
import win32con
from ctypes import *
from ctypes.wintypes import *
from comtypes import IUnknown
from comtypes.automation import IDispatch, VARIANT
from comtypes.client import wrap

kernel32 = windll.kernel32
user32 = windll.user32
atl = windll.atl
```

Of course PyGTK will need to be imported like any other GTK application.

```python
import pygtk
pygtk.require("2.0")
import gtk
```

Now a class will be created call GUI with an \_\_init\_\_ method with the following code to setup the window. This will basically just be like using the gtkmozembed window.

```python
self.home_url = "http://www.majorsilence.com/"

self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
self.win.set_title("Example Webbrowser that works on Linux and Windows") self.win.connect("destroy", gtk.main_quit)
self.win.set_size_request(750, 550)
self.win.realize()
# Create a VBox to house the address bar and the IE control.
self.main_vbox = gtk.VBox()

control_box = gtk.HBox(False, 0)

back = gtk.Button("Back")
forward = gtk.Button("Forward")
refresh = gtk.Button("Refresh")
stop = gtk.Button("Stop")
home = gtk.Button("Home")
self.address = gtk.Entry(max=0)
go = gtk.Button("Go")

control_box.pack_start(back, True, True, 2)
control_box.pack_start(forward, True, True, 2)
control_box.pack_start(refresh, True, True, 2)
control_box.pack_start(stop, True, True, 2)
control_box.pack_start(home, True, True, 2)
control_box.pack_start(self.address, True, True, 2)
control_box.pack_start(go, True, True, 2)

back.connect("clicked", self.on_backward_clicked, None)
forward.connect("clicked", self.on_forward_clicked, None)
refresh.connect("clicked", self.on_refresh_clicked, None)
stop.connect("clicked", self.on_stop_clicked, None)
home.connect("clicked", self.on_home_clicked, None)
self.address.connect("key_press_event", self.on_address_keypress)
go.connect("clicked", self.on_go_clicked, None)

self.main_vbox.pack_start(control_box, False, True, 2)

self.win.add(self.main_vbox)
self.win.show_all()

# Initialize all the Internet Explorer things
self.init_ie()
```

As can be seen with this example, the initialization function most creates a nice window to view web pages in. This is to be used with the rest of the code.

At the very end of the initialization is found the method call `self.init_ie()`, this is what sets up all the Internet Explorer stuff. I will be very honest here and say I am not sure how it all works since I do not really care to much about Windows programming, but I know that it does work.

So to take a look at the init\_ie method what is found is the following:

```python
def init_ie(self):
  # Create a DrawingArea to host IE and add it to the hbox.
  self.container = gtk.DrawingArea()
  self.main_vbox.add(self.container)
  self.container.show()
  # Make the container accept the focus and pass it to the control;
  # this makes the Tab key pass focus to IE correctly.
  self.container.set_property("can-focus", True)
  self.container.connect("focus", self.on_container_focus)
  # Resize the AtlAxWin window with its container.
  self.container.connect("size-allocate", self.on_container_size)
  # Create an instance of IE via AtlAxWin.
  atl.AtlAxWinInit()
  hInstance = kernel32.GetModuleHandleA(None)
  parentHwnd = self.container.window.handle
  self.atlAxWinHwnd = user32.CreateWindowExA(0, "AtlAxWin", self.home_url,
    win32con.WS_VISIBLE | win32con.WS_CHILD | win32con.WS_HSCROLL |
    win32con.WS_VSCROLL, 0, 0, 100, 100, parentHwnd, None, hInstance, 0)

  # Get the IWebBrowser2 interface for the IE control.
  pBrowserUnk = POINTER(IUnknown)()
  atl.AtlAxGetControl(self.atlAxWinHwnd, byref(pBrowserUnk))

  # the wrap call querys for the default interface
  self.browser = wrap(pBrowserUnk)
  # Create a Gtk window that refers to the native AtlAxWin window.
  self.gtkAtlAxWin = gtk.gdk.window_foreign_new(long(self.atlAxWinHwnd))
  # By default, clicking a GTK widget doesn't grab the focus away from
  # a native Win32 control.
  self.address.connect("button-press-event", self.on_widget_click)
```

All I can say about this is that it works. If you can figure it out good for you. Now lets focus on some of the methods that are needed to work with Internet Explorer that are connected to in the init\_ie method.

Here is the on\_widget\_clicked method:

```python
def on_widget_click(self, widget, data):
  control self.win.window.focus()
```

This method is used with Internet Explorer because on Windows, by default a GTK application does not grab control from native win32 api.

Next is the on\_container\_size method.

```python
def on_container_size(self, widget, sizeAlloc):
  self.gtkAtlAxWin.move_resize(0, 0, sizeAlloc.width, sizeAlloc.height)
```

This is used to make sure the gtk.Drawing container is properly sized[^2].

The last special method is on\_container\_focus.

```python
def on_container_focus(self, widget, data):
  rect = RECT()
  user32.GetWindowRect(self.atlAxWinHwnd, byref(rect))
  ieHwnd = user32.WindowFromPoint(POINT(rect.left, rect.top))
  user32.SetFocus(ieHwnd)
```

Apparently this method is used to pass the focus to Internet Explorer by passing the handle of the Internet Explorer control.

And now are the backward, forward, stop, refresh, and home buttons.

```python
def on_backward_clicked(self, widget=None, data=None):
  try:
    self.browser.GoBack()
  except:
    pass # No page to go back to

def on_forward_clicked(self, widget=None, data=None):
  try:
    self.browser.GoForward()
  except:
    pass

def on_refresh_clicked(self, widget=None, data=None):
  self.browser.Refresh()

def on_stop_clicked(self, widget=None, data=None):
  self.browser.Stop()

def on_home_clicked(self, widget=None, data=None):
  #self.browser.GoHome()
```

When using the GoBack and GoForward methods they must be used with error handling or they will will crash the program. The Refresh method is used to refresh, the Stop method is used to stop ad GoHome is used to go to the browsers home page.

The on\_go\_clicked method takes the address entered in the address bar and loads that page.

```python
def on_go_clicked(self, widget=None, data=None):
  v = byref(VARIANT())
  self.browser.Navigate(self.address.get_text(), v, v, v, v)
```

Loading the page that is in the address uses the Navigate method, pass in the address, then a variant to the rest[^3].

And finally the on\_address\_keypress method. This is the last method to be used with the Internet Explorer example. All this method does is watch for the Enter to be pressed and then calls the on\_go\_clicked method.

## Mozilla and IE Example

This section will show an example of how to use Internet Explorer or Mozilla as the engine depending on the operating system that is being used.

Mozilla and Internet Explorer

```python
"""
Embedding IE in pygtk via AtlAxWin and ctypes.
"""
# needs the comtypes package from http://sourceforge.net/projects/comtypes/
import sys
import pygtk
pygtk.require("2.0")
import gtk

if sys.platform=="win32":
    import win32con
    from ctypes import *
    from ctypes.wintypes
    import * from comtypes
    import IUnknown from comtypes.automation
    import IDispatch, VARIANT from comtypes.client
    import wrap
    kernel32 = windll.kernel32
    user32 = windll.user32
    atl = windll.atl
else:
    import gtkmozembed

class GUI:
    def __init__(self):
        self.home_url = "http://www.majorsilence.com/"

        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.set_title("Example Web browser that works on Linux and Windows")
        self.win.connect("destroy", gtk.main_quit) self.win.set_size_request(750, 550)
        self.win.realize()

        self.main_vbox = gtk.VBox()

        control_box = gtk.HBox(False, 0)
        back = gtk.Button("Back")
        forward = gtk.Button("Forward")
        refresh = gtk.Button("Refresh")
        stop = gtk.Button("Stop")
        home = gtk.Button("Home")
        self.address = gtk.Entry(max=0) # no limit on address length
        go = gtk.Button("Go")

        control_box.pack_start(back, True, True, 2)
        control_box.pack_start(forward, True, True, 2)
        control_box.pack_start(refresh, True, True, 2)
        control_box.pack_start(stop, True, True, 2)
        control_box.pack_start(home, True, True, 2)
        control_box.pack_start(self.address, True, True, 2)
        control_box.pack_start(go, True, True, 2)

        back.connect("clicked", self.on_backward_clicked, None)
        forward.connect("clicked", self.on_forward_clicked, None)
        refresh.connect("clicked", self.on_refresh_clicked, None)
        stop.connect("clicked", self.on_stop_clicked, None)
        home.connect("clicked", self.on_home_clicked, None)
        self.address.connect("key_press_event", self.on_address_keypress)
        go.connect("clicked", self.on_go_clicked, None)

        self.main_vbox.pack_start(control_box, False, True, 2)

        self.win.add(self.main_vbox)
        self.win.show_all()

        if sys.platform=="win32":
            self.init_ie()
        else:
            self.init_mozilla()

    def init_ie(self):
        # Create a DrawingArea to host IE and add it to the hbox.
        self.container = gtk.DrawingArea()
        self.main_vbox.add(self.container)
        self.container.show()

        # Make the container accept the focus and pass it to the control;
        # this makes the Tab key pass focus to IE correctly.
        self.container.set_property("can-focus", True)
        self.container.connect("focus", self.on_container_focus)

        # Resize the AtlAxWin window with its container.
        self.container.connect("size-allocate", self.on_container_size)

        # Create an instance of IE via AtlAxWin.
        atl.AtlAxWinInit()
        hInstance = kernel32.GetModuleHandleA(None)
        parentHwnd = self.container.window.handle
        self.atlAxWinHwnd = user32.CreateWindowExA(0, "AtlAxWin", self.home_url,
            win32con.WS_VISIBLE | win32con.WS_CHILD | win32con.WS_HSCROLL |
            win32con.WS_VSCROLL, 0, 0, 100, 100, parentHwnd, None, hInstance, 0)

        # Get the IWebBrowser2 interface for the IE control.
        pBrowserUnk = POINTER(IUnknown)()
        atl.AtlAxGetControl(self.atlAxWinHwnd, byref(pBrowserUnk))

        # the wrap call queries for the default interface
        self.browser = wrap(pBrowserUnk)

        # Create a Gtk window that refers to the native AtlAxWin window.
        self.gtkAtlAxWin = gtk.gdk.window_foreign_new(long(self.atlAxWinHwnd))

        # By default, clicking a GTK widget doesn't grab the focus away from
        # a native Win32 control.
        self.address.connect("button-press-event", self.on_widget_click)

    def init_mozilla(self):
        self.browser = gtkmozembed.MozEmbed()
        self.main_vbox.add(self.browser)
        self.browser.load_url(self.home_url)

    def on_backward_clicked(self, widget=None, data=None):
        if sys.platform=="win32":
            try:
                self.browser.GoBack()
            except:
                pass # No page to go back to
        else:
            if self.browser.can_go_back():
                self.browser.go_back()

    def on_forward_clicked(self, widget=None, data=None):
        if sys.platform=="win32":
            try:
                self.browser.GoForward()
            except:
                pass
        else:
            if self.browser.can_go_forward():
                self.browser.go_forward()

    def on_refresh_clicked(self, widget=None, data=None):
        if sys.platform=="win32":
            self.browser.Refresh()
        else:
            self.browser.reload(gtkmozembed.FLAG_RELOADNORMAL)

    def on_stop_clicked(self, widget=None, data=None):
        if sys.platform=="win32":
            self.browser.Stop()
        else:
            self.browser.stop_load()

    def on_home_clicked(self, widget=None, data=None):
        if sys.platform=="win32":
            # To go to Internet explorer's default home page use:
            #self.browser.GoHome()
            v = byref(VARIANT())
            self.browser.Navigate(self.home_url, v, v, v, v)
        else:
            self.browser.load_url(self.home_url)

    def on_go_clicked(self, widget=None, data=None):
        if sys.platform=="win32":
            v = byref(VARIANT())
            self.browser.Navigate(self.address.get_text(), v, v, v, v)
            #print dir(self.browser)
        else:
            self.browser.load_url(self.address.get_text())

    def on_address_keypress(self, widget, event):
        if gtk.gdk.keyval_name(event.keyval) == "Return":
            print "Key press: Return"
            self.on_go_clicked(None)

    def on_widget_click(self, widget, data):
        # used on win32 platform because by default a gtk application does
        # not grab control from native win32 control
        self.win.window.focus()

    def on_container_size(self, widget, sizeAlloc):
        self.gtkAtlAxWin.move_resize(0, 0, sizeAlloc.width, sizeAlloc.height)

    def on_container_focus(self, widget, data):
        # Used on win32 with Internet Explorer
        # Pass the focus to IE. First get the HWND of the IE control; this
        # is a bit of a hack but I couldn't make IWebBrowser2._get_HWND work.
        rect = RECT()
        user32.GetWindowRect(self.atlAxWinHwnd, byref(rect))
        ieHwnd = user32.WindowFromPoint(POINT(rect.left, rect.top))
        user32.SetFocus(ieHwnd)

if "__name__" == "__main__":
    gui = GUI()
    gtk.main()
```

[^1]: Mailing list found at at: <http://www.mail-archive.com/comtypes-users@lists.sourceforge.net/msg00084.html> and a direct link to the code found is: <http://www.mail-archive.com/comtypes-users@lists.sourceforge.net/msg00084/ie_in_gtk.py>
[^2]: Well as far as I can tell.
[^3]: I really have no idea what this does.
