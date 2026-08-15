---
layout: chapter
title: "Desktop Integration"
number: 5
part: 1
---

> **Not yet rewritten.** This chapter still describes GTK 2 and PyGTK,
> carried over from the previous edition. It is queued for the GTK 4 and
> PyGObject rewrite; the code in it will not run against GTK 4.

## GConfig

Save your applications configuration file using GConfig. This example is based off the gconfig-basic-app.py file that comes with the pygtk source code, I have changed it into something I find easier to understand.

```python
import gconf, gobject, gtk

class GConfigExample:
  def __init__(self):
    client = gconf.client_get_default()
    client.add_dir ("/apps/pygtk-book-gconf-example-app",
       gconf.CLIENT_PRELOAD_NONE)
```

Before even creating the gtk window, get the default gconf client, then tell the gconf client that we are interested in the given directory. This means the gconf client will receive notification of changes to this directory, and will also cache keys under this directory. To avoid getting a copy of the whole gconf database do not add "/" as that would specify the entire database. Also gconf.CLIENT\_PRELOAD\_NONE is used to avoid loading all config keys on startup. If the application reads all the config keys on startup, then preloading the cache may make sense, otherwise preload none is the way to go.

After setting up the initial gconf code the gtk window is created.

```python
    self.window = gtk.Window()
    self.window.set_title("GConfig Example")
    vbox = gtk.VBox(False, 5)
    self.window.add(vbox)
```

Next, the program will have eight labels that will show the database directory path as well as the value that is being stored. The method create\_configurable\_widget is used to create, display, and hook up the labels to be updated on changes to the gconf database.

```python
    config = self.create_configurable_widget(client,
        "/apps/pygtk-book-gconf-example-app/foo")
    vbox.pack_start(config, True, True)

    config = self.create_configurable_widget(client,
        "/apps/pygtk-book-gconf-example-app/bar")
    vbox.pack_start(config, True, True)

    config = self.create_configurable_widget(client,
        "/apps/pygtk-book-gconf-example-app/baz")
    vbox.pack_start (config, True, True)

    config = self.create_configurable_widget(client,
        "/apps/pygtk-book-gconf-example-app/blah")
    vbox.pack_start(config, True, True)

    self.window.connect("delete_event", lambda wid, we: gtk.main_quit())
```

Here we use the set\_data method on the applications main window, setting the key to "client" and the value to the gconf object that was created abouve; *client*. As well a preferences button is created and added to the window. The preferences button will open a preference dialog that will edit the gconfig entries directly and does not interact at all with the GConfigExample class that shows reading from gconf.

```python
    self.window.set_data ("client", client)
    prefs_button = gtk.Button ("Preferences")
    vbox.pack_end (prefs_button, False, False)
    prefs_button.connect ("clicked",   self.prefs_button_clicked_callback)

    self.window.show_all()
```

Once the widget monitoring notification that was created in the create\_configurable\_widget method is destroyed, the notification callback is removed.

```python
  def configurable_widget_destroy_callback(self, widget):
    client = widget.get_data("client")
    notify_id = widget.get_data("notify_id")

    if notify_id:
      client.notify_remove (notify_id)
```

Here there is a notification callback for the value label widgets that monitor the current value of a gconf key, when a gconf value is changed so is the label within the program. Note that the *value* can be None (unset) or it can have the wrong type. The program needs to check to make sure it can survive *gconftool --break-key*.

```python
  def configurable_widget_config_notify(self, client, cnxn_id, entry, label):
    if not entry.value:
      label.set_text("")
    elif entry.value.type == gconf.VALUE_STRING:
      label.set_text( entry.value.to_string() )
    else:
      label.set_text("!type error!")
```

This is the create\_configurable\_widget method that creates the labels that are displayed. Each gconf database directory will have a label to show the location as well as one label to show the value.

```python
  def create_configurable_widget(self, client, config_key):
    hbox = gtk.HBox(True)

    key_label = gtk.Label(config_key + ": ")
    label = gtk.Label ("")

    hbox.pack_start(key_label)
    hbox.pack_start(label)

    s = client.get_string(config_key)

    if s:
      label.set_text(s)

    notify_id = client.notify_add(config_key, self.configurable_widget_config_notify, label)
```

It should be noted here that notify\_id will be 0 if there is an error, so that is handled in the destroy callback.

```python
    label.set_data("notify_id", notify_id)
    label.set_data("client", client)

    label.connect("destroy", self.configurable_widget_destroy_callback)

    return hbox

  def prefs_button_clicked_callback(self, widget):
    client = self.window.get_data("client")
    prefs_dialog = EditConfigValues(client)
```

Next is the code for the preference dialog. the code will be in the EditConfigValues class. It is important to know that the preference dialog will never directly edit any values in the main window, it will only edit values in the gconf database. This is to test that the program works correctly as sometimes the values will be edited using gconf-editor instead of the applications preference window.

```python
class EditConfigValues:
  def __init__(self, client):
    self.dialog = gtk.Dialog ("GConfig Example Preferences",                              None, 0, (gtk.STOCK_CLOSE, gtk.RESPONSE_ACCEPT))

    self.dialog.connect('response', lambda wid,ev: wid.destroy ())
    self.dialog.set_default_response (gtk.RESPONSE_ACCEPT)

    vbox = gtk.VBox(False, 5)
```

Create four labels and four text entries that are used to display the gconf location as well as the current value in an entry area, this is accomplished using the create\_config\_entry method.

```python
    self.dialog.vbox.pack_start(vbox)
    entry = self.create_config_entry(client,
        "/apps/pygtk-book-gconf-example-app/foo", True)
    vbox.pack_start (entry, False, False)

    entry = self.create_config_entry(client,
        "/apps/pygtk-book-gconf-example-app/bar")
    vbox.pack_start (entry, False, False)

    entry = self.create_config_entry (client,
        "/apps/pygtk-book-gconf-example-app/baz")
    vbox.pack_start (entry, False, False)

    entry = self.create_config_entry (client,
        "/apps/pygtk-book-gconf-example-app/blah")
    vbox.pack_start (entry, False, False)

    self.dialog.show_all()
```

The config\_entry\_commit method does as its names says and commits changes to the gconf database. If the *text* string is zero-length it is unset, otherwise it is set.

```python
  def config_entry_commit(self, entry, *args):
    client = entry.get_data("client")
    text = entry.get_chars(0, -1)
    key = entry.get_data ('key')

    if text:
      client.set_string(key, text)
    else:
      client.unset(key)
```

The create\_config\_entry method takes as arguments the gconf client, the config key that is to be created, as well as whether the text entry has focus. This method creates a label that shows the config key and a text entry that shows the value. Editing the text entry changes the value of the gconf value.

```python
  def create_config_entry(self, client, config_key, focus=False):
    hbox = gtk.HBox(False, 5)
    label = gtk.Label(config_key)
    entry = gtk.Entry()

    hbox.pack_start(label, False, False, 0)
    hbox.pack_end(entry, False, False, 0)
```

Calling client.get\_string(config\_key) will print an error via the default error handler if the key is not set to a string.

```python
    s = client.get_string(config_key)
    if s:
      entry.set_text(s)

    entry.set_data("client", client)
    entry.set_data("key", config_key)
```

The changes will be commited if the user moves focus away from the text entry they are in, or if they hit enter; Changes are not commited on the *changed* signal as that would mean every new character entered would be sent, instead it waits for the user to finish first. Finally if the gconf client key is not writable the text entry is set to not writtable.

```python
    entry.connect("focus_out_event", self.config_entry_commit)
    entry.connect ("activate", self.config_entry_commit)
    entry.set_sensitive( client.key_is_writable(config_key) )
    if focus:
      entry.grab_focus()
    return hbox

if __name__ == "__main__":
  GConfigExample()
  gtk.main()
```

## PyGobject {#sec-pygobject}

I am not going to cover very much in this section because that would be a lot, maybe in a later verion. For now this section will cover one useful function. For more information check out its documentation at <http://pygtk.org/docs/pygobject/index.html>.

gobject.timeout\_add(interval,callback)
: is a function that will call the function specified in the callback as often as is specified by the interval until the callback function returns False.

Interval
: The number of seconds between calls. Eg. 1 for one second, 100 for 100 seconds. That is pretty simple

Callback
: The function that will be called at each interval.

I find this is a useful function to use when I want to periodically check to see if a long running process has finished. Another good example is lets say you have a music player with a progress bar, once a second while a song is playing you would want to update the progress bar. To do this you could setup a `gobject.timeout_add` to call an update function that checks the position of the currently playing song and update the progress bar with that information.

## Gnome Menus (.desktop files)

If an application is to be added to the main menu it will need an appname.desktop file with details about the application. The .desktop file will hold various information about the application including the name, how to execute it, tool tip comment, icon, category and more.

### Keys

The way that a .desktop file holds information is with keys. There are several keys and a few of them are required. The required keys are:

- Type - Application, Link, Directory
- Name - The name of the application and what will show up in the menu
- Exec - The program to execute with arguments
- URL - Only required if the entry is a Link Type

There are several other keys besides the required ones. To see what is available visit the .desktop files specification web page[^1].

.desktop Example

```ini
[Desktop Entry]
Version=1.0
Encoding=UTF-8
Name=Hello World
GenericName=Display Hello World
Comment=This is my first PyGTK application
X-MultipleArgs=false
Type=Application
TryExec=helloworld
Exec=helloworld
Categories=Utility
Icon=helloworld
```

Save this example as helloworld.desktop. When it is viewed with a file manger it will show up as "Hello World" because that is what the Name key is set to.

This Example sets up a .desktop with a version of 1.0. The encoding type is UTF-8. The GenericName is a generic name to describe the application. It is assigned to the Application type. It will try to execute helloworld. The category is Utility. The utility category means that it will be placed in the Accessories category in the menu. The comment is the tooltip for the that will be displayed on hovering over it. And last the icon is set to helloworld.

When using Icons it must be set to the absolute path or be installed in a location that it is able to be found. This helloworld icon is a image with the name helloworld.png and can be found on the books website. Supported icon image types are png, xpm and svg.

### Category Information

Included in the keys that can be used with a .desktop file is the category key. The category is the category that the Application, Link, or Directory will be included under. If for example we have an Application and it is in the Office category; then when the main menu is opened and the office subcategory is opened the application will show up there.

Here is a list of the default categories. More categories can be found on the menu specification web page[^2].

- AudioVideo - A multimedia (audio/video) application
- Audio - An audio application Desktop entry must include AudioVideo as well
- Video - A video application Desktop entry must include AudioVideo as well
- Development - An application for development
- Education - Educational software
- Game - A game
- Graphics - Graphical application
- Network - Network application such as a web browser
- Office - An office type application
- Settings - Settings applications Entries may appear in a separate menu or as part of a "Control Center"
- System - System application, "System Tools" such as say a log viewer or network monitor
- Utility - Small utility application, "Accessories"

### Installing and Using .desktop files

Creating a .desktop file without installing is pointless. It must be installed to be used. This section is going to use a small sample PyGTK application with a .desktop file to show how they work together. Then a small shell script will be created to install or uninstall the application, application data, and related .desktop file.

First lets create a small python program that is the main file to create the GUI and a second python file that will only have one function that returns a small message. These two files are used to show how it can be installed and set the path in the main python file to the correct install location of the supporting python modules that are included in the application[^3].

```python
#!/usr/bin/env python
import sys
sys.path.append("/usr/local/lib/helloworld")
import gtk
import helloworld_message

if __name__ == '__main__':
  win = gtk.Window()
  win.connect("delete_event", lambda w,e: gtk.main_quit())
  label = gtk.Label(helloworld_message.message())
  win.add(label)
  win.show_all()
  gtk.main()
```

At the very top of this example sys is import and the location /usr/local/lib/helloworld is append to the system path. The reason this is done is because this is where all the applications modules will be installed. If it does not append this directory then importing the helloworld\_message module will fail.

The helloworld\_message.py file only contains one function and is only two lines long.

```python
def message():
  return ".desktop example program"
```

Now that there is a working application and a desktop file that was created above it is time to install everything. For the purposes of installing the helloworld.desktop, helloworld.py, and helloworld\_message.py files a bash shell script will be used.

The shell script will take one argument that may be either --install or --uninstall. Anything other then that will display how to use this shell script. This script has been kept very simple so that it will be easy to understand.

To start off lets cover the beginning of the script.

```python
#!/bin/bash
# Get script directory path.
scriptdir="`dirname ${0}`"
DESTDIR="${DESTDIR:-}"
```

These first few lines set the shell script to be run by bash and set the variables "scriptdir" and "DESTDIR".

Next is the installation function. This function will install the main python file as a binary and the supporting python modules and data files.

```python
install_program() # arg1=bindir, arg2=datadir, arg3=pkglibdir,
        # arg4=pkgdatadir, arg5=pkgdocdir.
{
  echo ${DESTDIR}
  # Install binary data - /usr/local/bin/helloworld
  install -m 755 -d "${DESTDIR}${1}"
  install -m 755 "${scriptdir}/helloworld.py" "${DESTDIR}${1}/helloworld"

  # Install package library - /usr/local/lib/helloworld
  install -m 755 -d "${DESTDIR}${3}"
  install "${scriptdir}"/helloworld_*.py "${DESTDIR}${3}/"

  # Install package data /usr/local/share/helloworld
  #install -m 755 -d "${DESTDIR}${4}"
  #install -m 644 "${scriptdir}/helloworld.png" "${DESTDIR}${4}/"

  # Install data directory - /usr/local/share/pixmaps
  install -m 755 -d "${DESTDIR}${2}/pixmaps"
  install -m 644 "${scriptdir}/helloworld.png" "${DESTDIR}${2}/pixmaps/"

  # /usr/local/share/applications
  install -m 755 -d "${DESTDIR}${2}/applications"
  install -m 644 "${scriptdir}/helloworld.desktop" \
      "${DESTDIR}${2}/applications/"

  echo "Finished Install"
}
```

This function takes five arguments that specifiy where the binary, data, library, package data, and documentation are to be installed. It installs the helloworld.py file to /usr/local/bin/helloworld so it may be run by executing helloworld. It then install all python files that start with "helloworld\_" to the /usr/local/lib/helloworld directory. If there were any data files they would be installed to /usr/local/share/helloworld directory, but since there were none those lines are commented out(they are only using the helloworld.png file as an example).

The helloworld.png file is installed to the /usr/local/share/pixmaps directory, making it usable as an icon from the helloworld.desktop file. And at the very last, helloworld.desktop is installed to the /usr/local/share/applications directory. Once this is completed the the helloworld application should show up in the menu (Applications -> Accessories -> Hello World).

The next and last function in the install script is used to uninstall the helloworld application and is much smaller then the install function.

```bash
uninstall_program() # arg1=bindir, arg2=datadir, arg3=pkglibdir,
        # arg4=pkgdatadir, arg5=pkgdocdir.
{
  rm -f "${DESTDIR}${1}/helloworld"
  rm -f "${DESTDIR}${1}/helloworld.py"
  rm -rf "${DESTDIR}${3}"
  rm -rf "${DESTDIR}${4}"
  rm -rf "${DESTDIR}${5}"
  rm -f "${DESTDIR}${2}/pixmaps/helloworld.png"
  rm -f "${DESTDIR}${2}/applications/helloworld.desktop"
  echo "Finished Uninstall"
}
```

The uninstall function deletes all the files that were installed and all the directories that were created by the install function. This is very simple and there is no more to say about it.

The last part is to read the arguments given to the shell script and call the right function.

```python
# First arg to the script
action=$1
if test "$action" = --install
then
  echo "install selected"
  install_program "/usr/local/bin" \
        "/usr/local/share" \
        "/usr/local/lib/helloworld" \
        "/usr/local/share/helloworld" \
        "/usr/local/share/doc/helloworld"
elif test "$action" = --uninstall
then
  echo "uninstall selected"
  uninstall_program "/usr/local/bin" \
        "/usr/local/share" \
        "/usr/local/lib/helloworld" \
        "/usr/local/share/helloworld" \
        "/usr/local/share/doc/helloworld"
else
  echo ""
  echo "Usage:"
  echo " --install - Use this argument to install"
  echo " --uninstall - Use this argument to uninstall"
  echo ""
fi
```

This part of the install script reads the first argument to it and assigns it to the variable action. Then action is tested to see if it should install, uninstall, or display the accepted arguments.

That is all to creating a .desktop file for use with an application.

[^1]: For more information on keys that can be used with .desktop files please visit: <http://standards.freedesktop.org/desktop-entry-spec/latest/ar01s05.html>
[^2]: If you would like more information on categories please visit: <http://standards.freedesktop.org/menu-spec/menu-spec-1.0.html>
[^3]: A better way would probably be to install all the files to the library directory including the main python file. Then install a shell script to the binary directory that looks for and launches the directory. This way it does not need to append the to the system path the location of the applications python modules.
