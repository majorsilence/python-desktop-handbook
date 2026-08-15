---
layout: chapter
title: "More PyGTK"
number: 2
---

> Please send any fixes or suggestions to peter@majorsilence.com or leave a comment at http://www.majorsilence.com/pygtk\_book.

## Drag and Drop

I will not be writing very much about drag and drop, just enough to be useful in the slide show demonstration program that this notebook is leading towards. There are a few things we need to know.

The only part of drag and drop that we care about for this program is drag\_dest\_set(flags, targets, actions).

flags [^1] - according to the PyGTK tutorial, flags are:

- gtk.DEST\_DEFAULT\_MOTION: If set for a widget, GTK+, during a drag over this widget will check if the drag matches this widget's list of possible targets and actions. GTK+ will then call drag\_status() as appropriate.
- gtk.DEST\_DEFAULT\_HIGHLIGHT: If set for a widget, GTK+ will draw a highlight on this widget as long as a drag is over this widget and the widget drag format and action is acceptable.
- gtk.DEST\_DEFAULT\_DROP: If set for a widget, when a drop occurs, GTK+ will check if the drag matches this widget's list of possible targets and actions. If so, GTK+ will call drag\_get\_data() on behalf of the widget. Whether or not the drop is successful, GTK+ will call drag\_finish(). If the action was a move and the drag was successful, then TRUE will be passed for the delete parameter to drag\_finish().
- gtk.DEST\_DEFAULT\_ALL: If set, specifies that all default actions should be taken.

targets -- is a list of target data types that are supported along with in app information such as mime types of those files that can be dragged along with some.

actions -- are the actions that are to be taken with the drag and include the following:

- gtk.gdk.ACTION\_DEFAULT
- gtk.gdk.ACTION\_COPY
- gtk.gdk.ACTION\_MOVE
- gtk.gdk.ACTION\_LINK
- gtk.gdk.ACTION\_PRIVATE
- gtk.gdk.ACTION\_ASK

The only action we will be using is gtk.gdk.ACTION\_COPY and this is only on non win32 systems. For whatever reason I do not believe anything really works on a Windows system properly. I believe this actually because I have never properly been able to get a target properly specified, thus it never works on Windows so I have never bothered to go beyond drag\_dest\_set(0, [], 0). I see no point.

With that you can drag a file(s) anywhere into application then bother sorting out where it goes based on the file type that it is. I am sure in more complicated applications that this would not be enough but I have never personally needed more then this.

Now back to targets on anything other then Windows (Linux programs). For a target we will want to set up its file type. It will be in the form of (string, int, int).

So what we will end up with for the target will be something such as ("text/plain", 0, TARGET\_STRING). TARGET\_STRING must be an integer assigned above. It is a number that keeps track of the target throughout the program.

For flags we will probably just want to go with gtk.DEST\_DEFAULT\_ALL covering all the flags leaving us with less typing.

As I said before we will only use gtk.gdk.ACTION\_COPY for the actions part and this will only be for the part that are running on Linux systems.

So what we end up with on Linux is a function call that looks like this:

```python
drag_dest_set(gtk.DEST_DEFAULT_DROP, [("text/plain", 0,
TARGET_STRING), ("image/*", 0, TARGET_IMAGE)],
gtk.gdk.ACTION_COPY)
```

While on windows we will only be using a much smaller:

```python
drag_dest_set(0, [], 0)
```

We will need to attach this to a widget. In our case the widget will be the main window:

```python
win = gtk.Window()
win.set_size_request(400, 400)
if sys.platform == "win32":
    win.drag_dest_set(0, [], 0)
else:
    win.drag_dest_set(gtk.DEST_DEFAULT_DROP,
        [("text/plain", 0, TARGET_STRING),
        ("image/*, 0, TARGET_IMAGE)],
        gtk.gdk.ACTION_COPY)
```

The thing is that using more then the method that is being used for Windows is not needed for this program and I am only showing the other version for Linux just to introduce flags, targets, and actions.

Now that drag\_dest\_set has been attached to our main window widget we need to handle three singles:

- drag\_motion
- drag\_drop
- drag\_data\_received

What we do is connect them to three functions like so:

```python
win.connect("drag_motion", self.motion_cb)
win.connect("drag_drop", self.drop_cb)
win.connect("drag_data_received", self.drag_data_received)
```

How this works is not very important for our purposes. We just want it accepting images for us. If you want more information on how this works check out the PyGTK drag and drop tutorial at <http://pygtk.org/pygtk2tutorial/ch-DragAndDrop.html> or check out the drag and drop demo included in the PyGTK source code found at <http://www.pygtk.org>.

One last thing that I want to mention is that in the function drag\_data\_received we will be detecting if the files are in an accepted list of file types. If they are, in this example we add them to a list. What we will do in the slide show program is add them to the Item list in the GUI using a TreeView.

What you should end up with when everything is said and done is some source code that is similar to the following.

```python
import pygtk
import gtk
import sys
import os

class DragDropExample:
    def __init__(self):
        TARGET_STRING = 82
        TARGET_IMAGE = 83
        self.file_list=[] # list to hold our images
        self.accepted_types = ["jpg", "jpeg", "png", "gif", "bmp"]

        win = gtk.Window()
        win.set_size_request(400, 400)
        win.connect("delete_event", lambda w,e: gtk.main_quit())

        vbox = gtk.VBox(False, 0)
        hello = gtk.Label("Test label to drag images to.")
        vbox.pack_start(hello, True, True, 0)
        win.add(vbox)

        if sys.platform=="win32":
            # gtk.DEST_DEFAULT_DROP, does not work on windows
            # because will not match list of possible target
            # matches if you set anything besides a blank []
            # for target on Microsoft windows, it will not call
            # drop_data_received. So we might as well leave it
            # like so and do your own detecting of the files
            # and what to do with them in drag_data_received.

            win.drag_dest_set(0, [], 0)
        else:
            win.drag_dest_set(gtk.DEST_DEFAULT_DROP,
                [("text/plain", 0, TARGET_STRING),
                ("image/*", 0, TARGET_IMAGE)],
                gtk.gdk.ACTION_COPY)

        win.connect("drag_motion", self.motion_cb)
        win.connect("drag_drop", self.drop_cb)
        win.connect("drag_data_received",
            self.drag_data_received)
        win.show_all()

    def motion_cb(self, wid, context, x, y, time):
        context.drag_status(gtk.gdk.ACTION_COPY, time)
        return True

    def drop_cb(self, wid, context, x, y, time):
        print "drop"
        if context.targets:
            wid.drag_get_data(context, context.targets[0], time)
            print "" .join([str(t) for t in context.targets])
            return True
        return False

    def drag_data_received(self, img, context, x, y, data, info, time):
        if data.format == 8:
            print "Received %s " % data.data

        # Checking for valid file types
        test_data = os.path.splitext(data.data)[1][1:4].lower().strip()
        if test_data in self.accepted_types:
            if sys.platform=="win32":
                # Remove the file:/// on window systems.
                self.file_list.append(data.data[8:])
                print data.data[8:]
            else:
                # Remove the file:// on linux systems.
                self.file_list.append(data.data[7:])
                print data.data[7:]
            context.finish(True, False, time)
        else:
            context.finish(False, False, time)

if __name__ == "__main__":
    DragDropExample()
    gtk.main()
```

## List Boxes - gtk.TreeView

A list box in PyGTK is a little more difficult then programming one on Windows with winforms. With PyGTK you must use a TreeView. A true view is relatively complicated to use for just a list box, but it is all that is available. A wrapper can be made around a TreeView to form a generic list box. But this will not be included in this code.

A treeview takes the form of gtk.TreeView(model). The model is the type of the item being stored. What will be used here is gtk.ListStore(type).

The type of a ListStore is can be any valid python type (str, int, etc...). This stores the type data and each type becomes a column in a row.

With the information we now have we can create the tree like so:

```python
liststore = gtk.ListStore(str)
treeview = gtk.TreeView(liststore)
```

The above code will create a list box with 1 column. Also it is possible to set the type of modal of the TreeView after creating an instance.

```python
treeview.set_model(liststore)
```

Now, to make this useful a CellRenderer is needed. I will be using a CellRendererText.

```python
cell = gtk.CellRendererText()
```

The cell is what is used to display the data from the treeview model (liststore) to the user. The cell is then added to a gtk.TreeViewColumn like so:

```python
treeviewcolumn = gtk.TreeViewColumn("Button Pushed", cell, text=0)
```

The above code will create a TreeViewColumn with a column header of "Button Pressed" assigned the data from the CellRendererText "cell" and display the cells text to column 0.

With the treeviewcolumn created we go ahead and append it to the treeview that we created:

```python
treeview.append_column(treeviewcolumn)
```

To append data to a treeview you use the following code:

```python
model = treeview.get_model()
model.append(["Your Message"])
```

To remove a selected row from a TreeView you would use the following code:

```python
selection = self.treeview.get_selection()
model, iter = selection.get_selected()
if iter:
model.remove(iter)
return
```

If you want more then 1 column you have to create a CellRenderer and TreeViewColumn for each and append to the treeview. You must also have a data type in the ListStore for each column that you will be using. Examine the code below to see how this is applied to making a small program with two columns.

```python
import pygtk
pygtk.require("2.0")
import gtk

class TreeViewExample:
    def __init__(self):
        # Count the items in the item list
        self.counter = 0

        self.win = gtk.Window()
        self.win.set_size_request(400, 400)
        self.win.connect("delete_event", lambda w,e: gtk.main_quit())

        vbox = gtk.VBox(False, 0)
        hbox = gtk.HBox(False, 0)
        add_button = gtk.Button("Add Item")
        add_button.connect("clicked", self.add_button_clicked)

        remove_button = gtk.Button("Remove Item")
        remove_button.connect("clicked", self.remove_button_clicked)

        # Treeview Stuff
        self.liststore = gtk.ListStore(str, str)
        self.treeview = gtk.TreeView(self.liststore)

        # Add cell and column.
        # data added to treeview.
        self.cell = gtk.CellRendererText()
        self.cell2 = gtk.CellRendererText()

        # text=number is the column the text is displayed from
        self.treeviewcolumn = gtk.TreeViewColumn("Button Pushed",
            self.cell, text=0)
        self.treeviewcolumn2 = gtk.TreeViewColumn(
"Second Useless Column", self.cell2, text=1)

        self.treeview.append_column(self.treeviewcolumn)
        self.treeview.append_column(self.treeviewcolumn2)

        vbox.pack_start(self.treeview, True, True, 0)
        vbox.pack_start(hbox, False, True, 0)
        hbox.pack_start(add_button, True, True, 0)
        hbox.pack_start(remove_button, True, True, 0)
        self.win.add(vbox)
        self.win.show_all()

    def add_button_clicked(self, w):
        self.counter += 1
        model = self.treeview.get_model()
        model.append(["Add Button Pushed %s times"
            % self.counter, "Column 2 Message"])

    def remove_button_clicked(self, w):
        selection = self.treeview.get_selection()
        model, iter = selection.get_selected()
        if iter:
            model.remove(iter)
            return

if __name__ == "__main__":
    TreeViewExample()
    gtk.main()
```

For a much more detailed look at the available options in a TreeView visit: <http://pygtk.org/pygtk2tutorial/ch-TreeViewWidget.html>

### Single Click - Multiple Select

Say that multiple items in the list need to be selected and by single clicking. This will be difficult to accomplish quickly wading through the official documentation[^2]. Basically a few things need to be added to the above TreeView example.

First of all the *selection* that is created in `remove_button_clicked` needs to be removed as it will now be created in the \_\_init\_\_ method. Now selection is a class instance variable `self.selection`, change the code to match.

So in the \_\_init\_\_ method after

```python
self.treeview = gtk.TreeView(self.liststore)
```

Please add the following two lines of code.

```python
self.selection = self.treeview.get_selection()
self.selection.set_mode(gtk.SELECTION_MULTIPLE)
```

These two lines create the selection as a class level instance and set it up to allow multiple selections. Now to work with this the *changed* signal is emitting and needs to be connected to.

```python
self.selection.connect("changed", self.on_media_files_changed)
```

The above lines connects the *changed* signal that is emitted by single clicks on items to call `self.on_treeview_changed`.

```python
def on_media_files_changed(self, widget=None, event=None):
  model, path = self.selection.get_selected_rows()
  for x in path:
    print model[x[0]][0] # model[path][column]
```

This method does not do much in its current form. What it does do is retrieve all the selected rows and prints out their values from column one.

## Status Icons

Status Icons can be useful for different reasons. Personally I like to use them to hide long running applications such as my music player. I set it playing then just minimize it to the notification area on my panel. If I want to to do something with it I left click the status icon and my music player pops up. If I want to switch songs I right click on it and it pops up menu with some options, one of which includes moving to the next song.

Creating a status icons is a matter of one line of code to make it display.

```python
icon = gtk.status_icon_new_from_stock(gtk.STOCK_ABOUT)
```

This creates a status icon with an icon set to the stock GTK icon[^3] about.

Then it is a matter of adding two more lines of code to add left and right click ability to it.

```python
icon.connect('popup-menu', on_right_click)
icon.connect('activate', on_left_click)
```

The first line here adds signal handling to catch the *popup-menu* signal. This is caught on when a right click happens. When the popup-menu signal is detected the on\_right\_click function is called.

The second line detects the *activate* signal when the status icon is left clicked and calls the on\_left\_click function.

As the example below will show, the programmer is responsible for creating the popup menu. The Status Icon Example creates a status icon, and then connects to the *popup-menu* and *activate* signal. When the popup-menu signal is activated, the on\_right\_click function creates and shows a popup menu by calling the make\_menu function.

The make\_menu function displays a menu with the options Open App and Close App. Clicking on Open App will call the function open\_app which will display a message dialog by calling the function message. The same thing happens when Close App is clicked.

Basically this is how a status icon works; just substitute the actions and functions here for what is needed for your application.

Status Icon Example

```python
#!/usr/bin/env python
import gtk

def message(data=None):
  """
  Function to display messages to the user.
  """
  msg=gtk.MessageDialog(None, gtk.DIALOG_MODAL,
    gtk.MESSAGE_INFO, gtk.BUTTONS_OK, data)
  msg.run()
  msg.destroy()

def open_app(data=None):
  message(data)

def close_app(data=None):
  message(data)
  gtk.main_quit()

def make_menu(event_button, event_time, data=None):
  menu = gtk.Menu()
  open_item = gtk.MenuItem("Open App")
  close_item = gtk.MenuItem("Close App")

  #Append the menu items
  menu.append(open_item)
  menu.append(close_item)
  #add callbacks
  open_item.connect_object("activate", open_app, "Open App")
  close_item.connect_object("activate", close_app, "Close App")
  #Show the menu items
  open_item.show()
  close_item.show()

  #Popup the menu
  menu.popup(None, None, None, event_button, event_time)

def on_right_click(data, event_button, event_time):
  make_menu(event_button, event_time)

def on_left_click(event):
  message("Status Icon Left Clicked")

if __name__ == '__main__':
  icon = gtk.status_icon_new_from_stock(gtk.STOCK_ABOUT)
  icon.connect('popup-menu', on_right_click)
  icon.connect('activate', on_left_click)
  gtk.main()
```

## File choosers

File choosers are used to select files to open or to display a save dialog to the user. This section will cover the gtk.FileChooserDialog, gtk.FileChooserButton, and will also cover using native Windows file choosers when on Windows.

### gtk.FileChooserDialog

The FileChooserDialog class provides an easy to use way to display a file chooser or save dialog to end users. It is created with a few options and then is run returning succuss or failure. To start off here is a GUI with two buttons and a file filter declard that will be used to launch the file chooser and save dialog.

```python
def main():
  #file filters used with the filechoosers
  text_filter=gtk.FileFilter()
  text_filter.set_name("Text files")
  text_filter.add_mime_type("text/*")
  all_filter=gtk.FileFilter()
  all_filter.set_name("All files")
  all_filter.add_pattern("*")

  window = gtk.Window(gtk.WINDOW_TOPLEVEL)
  window.set_title("Filechooser Example")
  window.connect("destroy", lambda wid: gtk.main_quit())
  window.connect("delete_event", lambda e1,e2:gtk.main_quit())

  button_save = gtk.Button("Save File")
  button_open = gtk.Button("Open File")
  button_save.connect("clicked", on_save_clicked, text_filter, all_filter)
  button_open.connect("clicked", on_open_clicked, text_filter, all_filter)
  hbox = gtk.HBox(True, 0) hbox.pack_start(button_save, True, True, 5)
  hbox.pack_start(button_open, True, True, 5)

  window.add(hbox) window.show_all()
```

As can be seen in the code above, the first thing that is done is to seta gtk.FileFilter. One filter for text files and one filter that will be for all file types. The text that is displayed with a file filter is created with the method set\_name and the pattern is set using the set\_pattern method. For every pattern that is to be matched against there needs to be an instance of the gtk.FileFilter.

Then the GTK window is created. After this two buttons are created; the button\_save and button\_open buttons. When these buttons are clicked they pass the filters that were created at the top of the function to their respective callback functions.

Now to focus on on the details of filechooser dialogs. First is the save dialog.

```python
def on_save_clicked(widget, text_filter=None, all_filter=None):
  filename=None
  dialog=gtk.FileChooserDialog(title="Select a File",
    action=gtk.FILE_CHOOSER_ACTION_SAVE,
    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE,
    gtk.RESPONSE_OK))

  if (text_filter != None) and (all_filter != None):
    dialog.add_filter(text_filter)
    dialog.add_filter(all_filter)

  response = dialog.run()
  if response == gtk.RESPONSE_OK:
    filename = dialog.get_filename()
  elif response == gtk.RESPONSE_CANCEL:
    print 'Cancel Clicked' dialog.destroy()

  if filename != None:
    save_file=open(filename, 'w')
    save_file.write("Sample Data")
    save_file.close()
  print filename
```

The on\_save\_clicked function starts off by setting the filename to None and quickly sets up the dialog. The dialog title is set to "Select a File". The action type of the dialog is set to save using gtk.FILE\_CHOOSER\_ACTION\_SAVE. The buttons are set with a tuple. The button uses the stock cancel using the gtk.RESPONSE\_CANCEL and the stock save button that uses the gtk.RESPONSE\_OK when it is clicked.

After this the function checks to see if there are any filters that should be applied and if so it applies them.

After the filters are added, the dialog is run with its return value assigned to the variable response.

```python
response = dialog.run()
```

It then checks the value of response to be of gtk.RESPONSE\_OK and if so assigns the name of the file to the variable filename using:

```python
filename = dialog.get_filename()
```

If the response is set to gtk.RESPONSE\_CANCEL, no actions are taken.

The last action to take with the dialog is to call the destroy method. If the destroy method is not called the dialog will stay on the screen.

```python
dialog.destroy()
```

The final part of the on\_save\_clicked function is to save the string "Sample Data" to the file that was specified to save to.

The on\_open\_clicked function is very similar to the on\_save\_clicked function. Instead of opening a dialog to save a file it opens a dialog to select a file for the application to load.

```python
def on_open_clicked(widget, text_filter=None, all_filter=None):
  filename=None
  dialog=gtk.FileChooserDialog(title="Select a File",
    action=gtk.FILE_CHOOSER_ACTION_OPEN,
    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
    gtk.STOCK_OPEN, gtk.RESPONSE_OK))

  if (text_filter != None) and (all_filter != None):
    dialog.add_filter(text_filter)
    dialog.add_filter(all_filter)

  response = dialog.run()
  if response == gtk.RESPONSE_OK:
    filename = dialog.get_filename()
  elif response == gtk.RESPONSE_CANCEL:
    print 'Cancel Clicked'

  dialog.destroy()
  print "File Choosen: ", filename
```

Just like in the on\_save\_clicked function the on\_open\_clicked starts off by setting the filename to None. Then it sets up the open dialog using the gtk.FileChooserDialog. It sets the dialog title to "Select a File", the action to open with gtk.FILE\_CHOOSER\_ACTION\_OPEN. The buttons for the dialog are set as a tuple with the button type and button response next to each other. It sets a cancel button with gtk.STOCK\_CANCEL with a response of gtk.RESPONSE and open button with gtk.STOCK\_OPEN with a response of gtk.RESPONSE\_OK.

After it checks to see if there are filters set and if so adds filters to the dialog using the add\_filter method.

The dialog is run using the run method and assigns the response to the variable response like so:

```python
response = dialog.run()
```

The on\_open\_clicked function then checks the value of the response variable. If the response is gtk.RESPONSE\_OK the file name is set by using the dialogs get\_filename() method.

```python
filename = dialog.get_filename()
```

If the response is gtk.RESPONSE\_CANCEL no action is taken. The very last action that is taken is to call the dialogs destroy method.

```python
dialog.destroy()
```

If the destroy method is not called the dialog will stay on screen.

### gtk.FileChooserButton

The gtk.FileChooserButton eases the use of a open file dialog by taking care of the run and destroy code and also provides a button. This is easier than the previous section on the FileChooserDialog.

File Chooser Button

```python
def main():
  #file filters used with the filechoosers
  text_filter=gtk.FileFilter()
  text_filter.set_name("Text files")
  text_filter.add_mime_type("text/*")
  all_filter=gtk.FileFilter()
  all_filter.set_name("All files")
  all_filter.add_pattern("*")

  window = gtk.Window(gtk.WINDOW_TOPLEVEL)
  window.set_title("Native Filechooser")
  window.connect("destroy", lambda wid: gtk.main_quit())
  window.connect("delete_event", lambda e1,e2:gtk.main_quit())

  button_open = gtk.FileChooserButton("Open File")
  button_open.add_filter(text_filter)
  button_open.add_filter(all_filter)
  button_open.connect("selection-changed", on_file_selected)

  window.add(button_open)
  window.show_all()

def on_file_selected(widget):
  filename = widget.get_filename()
  print "File Choosen: ", filename

if __name__ == "__main__":
  main()
  gtk.main()
```

This example starts by creating two filter types using the gtk.FileFilter class. One filter for text files and one filter for any type of file. Skip a few lines and a FileChooserButton is created like this:

```python
button_open = gtk.FileChooserButton("Open File")
```

To retrieve the selected file from a FileChooserButton it must connect the *selection-changed* signal to a function. So this example connects the selection-changed signal to the on\_file\_selected function. The on\_file\_selected function retrieves the filename that was choosen and then prints it.

### Windows File Chooser

The native GTK filechoosers are generally ok, but they are very ugly if the GTK application is running on Windows. For PyGTK apps that are running on Windows the option exists to use a native Windows file chooser dialog. The following example will show how to open a file and to save a file. This example will require that the pywin32 package be installed[^4].

First off the os, win32con, and win32gui modules will need to be imported along with the pygtk and gtk modules.

```python
import os
import win32gui, win32con
```

Like all the other examples about file choosers the Windows file chooser will start off with some GUI code.

```python
def main():
  file_filter="""Text files\0*.txt\0All Files\0*.*\0"""

  window = gtk.Window(gtk.WINDOW_TOPLEVEL)
  window.set_title("Windows Filechooser Example")
  window.connect("destroy", lambda wid: gtk.main_quit())
  window.connect("delete_event", lambda e1,e2:gtk.main_quit())

  button_save = gtk.Button("Save File")
  button_open = gtk.Button("Open File")
  button_save.connect("clicked", on_save_clicked, file_filter)
  button_open.connect("clicked", on_open_clicked, file_filter)

  hbox = gtk.HBox(True, 0)
  hbox.pack_start(button_save, True, True, 5)
  hbox.pack_start(button_open, True, True, 5)

  window.add(hbox) window.show_all()
```

First thing that is done is to create a file filter that will be used with the open and save dialogs. The file filter is in the form of "Display Name, Seperator, File Type, Seperator, Display Name, Seperator, File Type, Seperator" and looks like this:

```python
file_filter="""Text files\0*.txt\0All Files\0*.*\0"""
```

The GUI creates one button to launch the save dialog and one to launch the open dialog. The button called button\_save is clicked it will call the on\_save\_clicked function passing along the file filter. When the button called button\_open is clicked, it will call the on\_open\_clicked function passing along the file filter.

The on\_save\_clicked and on\_open\_clicked function are very similar in form with some minor differences. Here is the on\_save\_clicked function.

```python
def on_save_clicked(widget, file_filter=None):
  filename=None
  try:
    filename, customfilter, flags=win32gui.GetSaveFileNameW(
      InitialDir=os.path.join(os.environ['USERPROFILE'],"My Documents"),
      Flags=win32con.OFN_ALLOWMULTISELECT|win32con.OFN_EXPLORER, File='',
      DefExt='txt', Title='Save a File', Filter=file_filter, FilterIndex=0)
  except win32gui.error:
    print "Cancel clicked"

  print filename
  if filename != None:
    save_file = open(filename, 'w')
    save_file.write("Test Save Data")
    save_file.close()
  return filename
```

This is a simple funtion that takes a file filter as an argument and sets it as the filter for Windows save dialog. To use and display the save dialog the win32gui.GetSaveFileNameW function is used. Arguments that are used with it include Initial Directory, Flags, File, Default Extention, Title, File Filter, and FilterIndex. As can be seen the inital directory is set to the users My Documents folder. Flags are set to allow multiple selection. The default extention type is txt. When it is called it must be done by assigning its return value to three variables; filename, customfilter, flags.

The GetSaveFileNameW function must be used with exception handling as it will through an exception if the cancel button is clicked. So this example catches win32gui.error exceptions and prints the message "Cancel clicked" instead of crashing.

If a file has been selected to save this example saves it with the string "Test Save Data".

The GetOpenFileNameW function is used to select and open file on Windows. It is very simliar to the GetSaveFileNameW function covered above. Here is the on\_open\_clicked function that uses the Windows open dialog.

```python
def on_open_clicked(widget, file_filter=None):
  filename=None
  try:
  filename, customfilter, flags=win32gui.GetOpenFileNameW(
    InitialDir=os.path.join(os.environ['USERPROFILE'],"My Documents"),
    Flags=win32con.OFN_ALLOWMULTISELECT|win32con.OFN_EXPLORER, File='',
    DefExt='txt', Title='Select a File', Filter=file_filter, FilterIndex=0)
  except win32gui.error:
    print "Cancel clicked"
  print 'open file names:', filename
  return filename
```

The GetOpenFileNameW functions takes as arguments Intial Directory, Flags, File, Default Extention, Title, File Filter, and Filter Index. As can be seen the inital directory is set to the users My Documents folder. Flags are set to allow multiple selection. The default extention type is txt. When calling this function the return value must be assigned to three variables; these being the filename, customfilter, and flags.

Like the save GetSaveFileNameW the GetOpenFileNameW function requires that it used with exception handling as it will give win32gui.error if the cancel button is pressed. If everything goes as planed the function should continue to the end where it prints the message "open file names: filename".

## Glade 3 {#sec-glade-3}

Glade is a program that allows the creation of the user interface graphical. Windows and dialogs can be created. Widgets can be dragged and dropped into place. Names assigned to widgets, callback functions assigned. All this is saved to a xml file with an extension of .glade.

Docked on the left side of glade is the palette. The palette contains the top level elements such as:

- windows (gtk.Window)
- dialogs (gtk.Dialog etc...)

Under the Toplevels is are the Containers. The containers contain:

- Horizontal Box (gtk.HBox)
- Vertical box (gtk.VBox)
- Table (gtk.Table)
- Notebook (gtk.Notebook)
- Frame (gtk.Frame)
- etc...

After and under the Containers are the Control and Display widgets, they contain:

- Button (gtk.Button)
- Toggle Button (gtk.ToggleButton)
- Check Button (gtk.CheckButton)
- Spin Button (gtk.SpinButton)
- Raido Button (gtk.RadioButton)
- etc...

To create a simple application, from the Toplevels select and add a Window. Next select a Horizontal Box and add it to the Window. When prompted for how many items, select two. When this is done the window will be split in half horizontally with a line going down through the center (see figure [Basic Glade User Interface Designer](02-more-pygtk.html#fig-basic-glade-user-interface)). Each of these can hold a widget.

![Basic Glade User Interface Designer](images/more-pygtk/Screenshot-glade-example.png){: #fig-basic-glade-user-interface width="30%"}

Next add two buttons from the container. The one on the left label Message and the one on the right label About. Also change the names to message and about. To do this click the first button. On the right hand side the editor should change for a button type (see figure [Glade Editor with Button](02-more-pygtk.html#fig-glade-editor-with-button)). As can be seen in figure[Glade Editor with Button](02-more-pygtk.html#fig-glade-editor-with-button); the class is of type GtkButton, the name is set to message meaning that when it is called with PyGTK it uses the name message. For the Label it is set to Message. The label is what is displayed to the user as the button text.

![Glade Editor with Button](images/more-pygtk/Screenshot-glade-example-button-editor.png){: #fig-glade-editor-with-button width="50%"}

Once the buttons have been added and setup with the names and labels then the signals that are to be caught should be added (see figure [Signal Handler Specified](02-more-pygtk.html#fig-glade-signal-handler-specified)). To add signal methods to the buttons first select the message button. Then in the editor window select the Signals tab. Under GtkButton there will be a signal called *clicked*. For clicked add a handler. If the handler space is clicked it will provide a default list to choose from. To see what it should look like look at figure [Signal Handler Specified](02-more-pygtk.html#fig-glade-signal-handler-specified). What is typed as the Handler is the function or method in the python code that will be called.

![Signal Handler Specified](images/more-pygtk/Screenshot-glade-example-signal-handler.png){: #fig-glade-signal-handler-specified width="50%"}

Now that the buttons have been added to the main window (whose name is window1) it is time to make sure that this window is visible. Select the main window and in the editor select the Common tab. Once in the Common tab find the *Visible* option and make sure it is set to *Yes* (see figure [Main Windows Set as Visible](02-more-pygtk.html#fig-glade-main-windows-set-as-visible)).

![Main Windows Set as Visible](images/more-pygtk/Screenshot-glade-example-main-window-visible.png){: #fig-glade-main-windows-set-as-visible width="50%"}

Now the main window is done. Save your work. Next an about dialog will be added. To add an about dialog it is selected from the Toplevel elements on the palette. Leave it with the default name *aboutdialog1*. The about dialog will be used to show how to interact with more than one window in glade.

A PyGTK program interacts with the created glade file using gtk.glade.

```python
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

class GladeExample(object):
  def __init__(self):
    self.gladefile = gtk.glade.XML("glade-example.glade")
    self.gladefile.signal_autoconnect(self)
    self.main_window = self.gladefile.get_widget("window1")
    self.about_dialog = self.gladefile.get_widget("aboutdialog1")
    self.message_dialog = self.gladefile.get_widget("messagedialog1")
```

Here the class GladeExample is declared with an intiation method that connects to the glade file that was created. The glade file is loaded using the gtk.glade.XML class. It takes as arguments the glade file and optionally a widget and translation domain.

Then to use a widget as if it was created using PyGTK code it must be retrieved using the get\_widget method. The get\_widget method works by taking as an argument the name of the widget. In the glade example above the main windows name is window1, the about dialogs name is aboutdialog1, and the message dialog is messagedialog1. As can be seen the main window is assigned to self.main\_window and so on with the about and message dialog.

What can be noticed that the buttons that were adding to the glade file to launch the about and message dialog were not assigned with the get\_widget method. This is because they were set to automatically call handler functions and do not need to write code for each button to connect them. This is handled with one line of code, self.gladefile.signal\_autoconnect(self). This one line will automatically connect any signal handlers that were specified in the glade file without having to write any extra code.

```python
  def on_about_clicked(self, widget):
    self.about_dialog.run()
    self.about_dialog.destroy()
```

As was specified with glade, when the about button is clicked, the method on\_about\_clicked is called. This method displays the about dialog that was created with glade and destroys the dialog when it is closed.

```python
  def on_message_clicked(self, widget):
    self.message_dialog.run()
    self.message_dialog.destroy()
```

As was specified with glade, when the message button is clicked, the method on\_message\_clicked is called. This method displays the message dialog that was created with glade and destroys the dialog when it is closed.

```python
  def on_window1_delete_event(self, widget, event):
    gtk.main_quit()
```

the on\_window1\_delete\_event will quite the PyGTK application when the main window(window1) is closed. This to is specified with glade under the main windows Signal tab; GtkWidget --> delete-event.

```python
if __name__ == "__main__":
  app = GladeExample()
  gtk.main()
```

And of course a few lines that runs the glade example.

## Builder {#sec-gtk-builder-convert}

Builder refers to gtk.Builder which is the future as it is a replacement for gtk.glade. Basically what it is is including support for xml files to build applications inside of GTK itself, unlike glade which is a library. Currently the glade program does not support saving to the Builder format, but it will soon. In the mean time glade files must be converted to Builder files using *gtk-builder-convert*[^5]. This program will take a glade xml file and convert it to a Builder xml file.

To convert a glade file to a Builder file the following command is issued:

```python
gtk-builder-convert glade-example.glade glade-example.xml
```

Now instead of using gtk.glade.XML to access this new builder xml file, gtk.Builder is used as shown here.

```python
builder = gtk.Builder()
builder.add_from_file("glade-example.xml")
```

Also instead of using get\_widget like in the glade example (see [Glade 3](02-more-pygtk.html#sec-glade-3)), the method `get_object` is used.

```python
main_window = builder.get_object("window1")
about_dialog = builder.get_object("aboutdialog1")
message_dialog = builder.get_object("messagedialog1")
```

With this done, the widgets can be used as if they were programmed normally with PyGTK.

To auto connect the signals like is avialbe using glade the following code is used.

```python
builder.connect_signals(self)
```

Remember this needs to be done from within a class.

## Loading Images

To load an image with PyGTK an instance of the gtk.Image class must be created. With this becomes available several methods for loading different types of images. This example will cover loading images from file and from the GTK stock images.

Loading Images

```python
import pygtk, gtk
def main():
  win = gtk.Window()
  win.connect("delete_event", lambda w,e: gtk.main_quit())
  vbox = gtk.VBox(False, 0)

  image1 = gtk.Image()
  image1.set_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_DND)

  image2 = gtk.Image()
  image2.set_from_file("flower.jpg")

  vbox.pack_start(image1, False, False, 5)
  vbox.pack_start(image2, False, False, 5)
  win.add(vbox)
  win.show_all()

if __name__ == "__main__":
  main()
  gtk.main()
```

This example creates a window with a gtk.VBox and adds two images. The first image is set from stock gtk images created with the set\_from stock method. The set\_from\_stock method requires a GTK stock image and a stock size. The stock types available can be found in the appendix ([Stock Icons](15-stock-icons.html#sec-appendix-stock-icons)). The stock sizes include:

- gtk.ICON\_SIZE\_MENU
- gtk.ICON\_SIZE\_SMALL\_TOOLBAR
- gtk.ICON\_SIZE\_LARGE\_TOOLBAR
- gtk.ICON\_SIZE\_BUTTON
- gtk.ICON\_SIZE\_DND
- gtk.ICON\_SIZE\_DIALOG

The second image is loaded using set\_from\_file method. All this method requires is location on the computer to the image.

All that needs to be done once the images are loaded is add them to a widget. In this example they are added to gtk.VBox.

There are many different methods for loading images and they can be found at the PyGTK reference site[^6].

## Tooltips

A tooltip is used to display useful information to the screen a user puts a mouse over a widget such as label or button. To use a simple tooltip requires only on method call on the widget: set\_tooltip\_text

```python
label = gtk.Label("Display Tooltip")
label.set_tooltip_text("This is a Tooltip")
```

When a mouse is placed over this label a tooltip will display the text "This is a Tooltip". Very simple to use and there is nothing more to be said on that.

For more fancy tooltips a custom tooltip must be created. To do this the has\_tooltip property must be set to True. Then the widget that is to display the custom tooltip must connect to the query-tooltip signal. For example, the callback function can create a new tooltip by creating an gtk.HBox that holds an image and text then use set\_custom on the tooltip to use this hbox.

Here is an example.

```python
fancy_label = gtk.Label("A fancy Tooltip")
fancy_label.props.has_tooltip = True
fancy_label.connect("query-tooltip", on_query_tooltip)
```

So this creates a label, sets the tooltip to true using fancy\_label.props.has\_tooltip property, and then connects the query-tooltip signal to the function on\_query\_tooltip.

Here is an example of the on\_query\_tooltip function. This function creates a label and an image that is displayed instead of plain text.

```python
def on_query_tooltip(widget, x, y, keyboard_tip, tooltip):
  hbox = gtk.HBox()
  label = gtk.Label('Fancy Tooltip with an Image')

  image = gtk.Image()
  image.set_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_DND)

  hbox.pack_start(image, False, False, 0)
  hbox.pack_start(label, False, False, 0)
  hbox.show_all()

  tooltip.set_custom(hbox)
  return True
```

As can be seen this creates a gtk.HBox to hold a label and an Image. It then uses the tooltip argument to set it to a custom tooltip. A custom tooltip can be anything but this example has kept it simple for understandability sake. For more tooltip options visit the PyGTK tooltip reference page[^7].

## Summary

This section is not yet written :)

[^1]: Take a look at: <http://pygtk.org/pygtk2tutorial/sec-DNDMethods.html>
[^2]: Oh do I ever know it. Talk about wasted hours of my life I am never getting back.
[^3]: For a full listing of GTK stock icons take a look at the list of stock icons on page [Stock Icons](15-stock-icons.html#sec-appendix-stock-icons) or the pygtk website at: <http://www.pygtk.org/docs/pygtk/gtk-stock-items.html>
[^4]: See section[PyGTK and Windows](14-pygtk-and-windows.html#sec-appendix-pygtk-and-windows) for instructions on using PyGTK on Windows for more information. Or just go to <http://sourceforge.net/projects/pywin32/files/> and download and install it.
[^5]: For more information on gtk-builder-convert visit: <http://library.gnome.org/devel/gtk/2.12/gtk-builder-convert.html>. Also if you plan on using gtk-builder-convert, gtk development files must be installed to have it installed. This is accomplished on Ubuntu by installing libgtk2.0-dev.
[^6]: The PyGTK image class can be found at: <http://www.pygtk.org/docs/pygtk/class-gtkimage.html>
[^7]: The PyGTK tooltip reference page can be found at: <http://www.pygtk.org/docs/pygtk/class-gtktooltip.html>
