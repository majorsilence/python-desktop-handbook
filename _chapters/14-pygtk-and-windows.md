---
layout: chapter
title: "PyGTK and Windows"
number: 14
appendix: true
anchor: sec-appendix-pygtk-and-windows
---

## Install GTK and Glade

First thing you need before you start using PyGTK on Windows is to have GTK+ installed.

Go to the gtk web site (<http://www.gtk.org>) download section and download the GTK bundle for windows. Then you will need to set your path to include the location of gtk.

- Control Panel -> System -> Advanced tab -> Environment Variables -> Select "Path"

Now for the path select it for your current user or your system wide path and add the "bin" location from where you put your GTK bundle.

## Install PyGTK

Go to the PyGTK website (<http://www.pygtk.org>) download page. At the top of the page are the downloads for Windows. You will need all three and need to install them in this order:

- PyGObject
- PyCairo
- PyGTK

You may also want to download the GTK+ Preference Tool. You should be able to find it at <http://sourceforge.net/projects/gtk-win/files/>. This tool will allow you to set the GTK theme on your Windows user account. At this point you should have a PyGTK development environment on your computer.

If you want you can also install Win32 extensions for python from <http://sourceforge.net/projects/pywin32/files/>.

## Icons Not Displaying

Some win32 distributions of GTK+ have icons set to not display. This is a configuration option in the gtkrc theme files. One option to fix this and make sure that icons display for buttons and all other widgets is to place the following code in the main PyGTK file of your application.

```python
if sys.platform=="win32":
 gtk.settings_get_default().set_long_property("gtk-button-images", True, "main")
```

The other option is to do the following:

1. Open the C:\\GTK\\share\\themes\\MS-Windows\\gtk-2.0\\gtkrc file
1. And change the line "gtk-button-images = 0" to "gtk-button-images = 1"
