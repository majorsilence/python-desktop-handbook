---
layout: chapter
title: "PyGTK Introduction"
number: 1
---

> Please send any fixes or suggestions to peter@majorsilence.com or leave a comment at http://www.majorsilence.com/pygtk\_book.

## Introduction

This book has been created as a personal notebook that I may refer back to when I no longer remember how to program something I once did. There has been many a time that I have spent many hours figuring how to do something interesting just to forget how I did it, or where on the web it was found. As I have become tired of doing this I have decided to collect my notes and code samples in one location that is easy for myself to reference. Basically I am using open source code to write an open source book.

Hopefully this information will be useful to others as I have found that many of these topics are not currently collected together in a nice package making it easy to use.

The materials in this book are from several sources from the Internet and programming books that I have read in the past, or as in the instance of the case studies, code I have done myself.

If anything is not cited or referenced properly I now apologize to the original author and will correct it in the next edition.

Please check the books website regularly for updates and errata, the web site is located at: <http://www.majorsilence.com/pygtk_book>

## PyGTK Basics

### Widgets - What are they? {#sub-widgets-what-are-they}

Before creating your first program lets get out of the way what a widget is. A widget is what makes up a program. They are all the different parts that can be used and include the following:

- Labels
- Buttons
- Menus
- Text Entries
- etc..

So basically that is what they are. If you are used to programming using .NET and winforms you would be use to hearing them referred to as controls. The buttons, labels, text areas of all programs are widgets. There are many different types available when using PyGTK and many of them will be covered in this book, but to start off this chapter will only cover a few such as buttons, labels and text entry.

### Creating your first PyGTK application {#sub-creating-your-first-pygtk-application}

First thing, create a window that will display a small message. To do this pygtk and gtk must be imported.

```python
import pygtk
pygtk.require("2.0")
import gtk
```

Now create a label and a GTK window. As you can see below to set the text of a label you just supply the text when you instantiate it. To make add it to the window that you have created you use the windows add method and supply the widget (label). Then to show everything to the user you call the windows `show_all` method. Last but not least you must call the `gtk.main()` method.

```python
label = gtk.Label("Hello World!")
win = gtk.Window()
win.add(label)
win.show_all()
gtk.main()
```

If you do not call the `gtk.main()` method, nothing will happen. It is the main loop that waits for user input and and reactions. It runs all the code that is necessary to display your application.

### Layout - Boxes {#sub-layout-boxes}

Adding a label to a window is good and well if not useless. What you have to do is create a layout using horizontal and vertical boxes. These boxes can hold PyGTK widgets or other vertical and horiztonal boxes. You will have one main box that will hold all other boxes, this main box will be added to the window. To add a widget to a box, or a box to another box the `pack_start` and `pack_end` methods are used.

Now lets expand on the first PyGTK application to include a vertical and horizontal box to layout two labels and a button.

```python
import pygtk
pygtk.require("2.0")
import gtk

label_1 = gtk.Label("Hello World!")
label_2 = gtk.Label("Still in the HBox")
button = gtk.Button("This button is in the Vertical Box")
vbox = gtk.VBox()
hbox = gtk.HBox()
```

Start off by creating two labels and a button. A buttons text is set when creating the same way as a labels is by including the text when you create an instance of gtk.Button. Next two layout boxes are created.

The first box created is a vertical box and the second is a horizontal box. This boxes have the following definition gtk.HBox(homogeneous=False, spacing=0). *Homogeneous* is whether each object in the box has the same size. You can have a vertical box (gtk.VBox) or a horizontal box (gtk.HBox). This is how in PyGTK a program has its layout. Take some time and experiment using them. (I also recommend using Glade 3 (See [Glade 3](02-more-pygtk.html#sec-glade-3)) to create your user interfaces instead of doing it by hand).

```python
hbox.pack_start(label_1)
hbox.pack_start(label_2)
# Add the hbox as the first item in the vertical box
# that was created above
vbox.pack_start(hbox)
# Add the button as the next item in the vertical box.
vbox.pack_start(button)
```

With the layout boxes created the labels and button must be added to them. So now the pack\_start method of the boxes is used. The definition of these methods is pack\_start(child, expand=True, fill=True, padding=0). You have the option of using pack\_start which adds the widget to the beginning of the box, or pack\_end which appends the widget to the end of the box.

So this code adds label\_1 to the first position of the horizontal box then adds label\_2 to the next position at the beginning after label\_1. Next the horizontal (hbox) is added as the first widget in the vertical (vbox) box. Next the button is added to the next position of the vertical box. When you run this a window should open up with two labels above a button.

- *child* is the widget you are adding to the box
- *expand* argument is whether to fill the extra space in the box (gtk.HBox or gtk.VBox)
- *fill* argument only has an effect if the expand argument is set to True.

All that is left is to run the program. So just like in the first program a gtk.Window is created, but instead of adding a widget such as a label directly to it a layout box is added. Here the vertical box (vbox) is added as it is the top level box that we used to hold all other widgets in the code above. Then call the show\_all() method on the window to make all the widgets in the window visible. Now to actually run the program the gtk.main() method must be invoked.

```python
win = gtk.Window()
win.add(vbox)
win.show_all()
gtk.main()
```

Run the program and enjoy your glorious creation.

### Callbacks - Reacting to program events {#sub-callbacks-reacting-to-program-events}

A program that does not react to user input is usually a useless program. To react to user input such as a mouse click there must be assigned to a widget a signal handler. A signal handler is connected to a widget such as a gtk.Button and listens for a signal.

Take for example, a signal handler could be added to a button that reacts on a mouse click.

So lets create a button and add a signal handler:

```python
button = gtk.Button("example button")
button.connect("clicked", on_button_clicked)
```

What this code does is create a button that when "*clicked*" will call the function `on_button_clicked`. In the example below we there is no longer a gtk.HBox, only a vertical gtk.VBox is used and the button has signal handler to connect *clicked* signals to the `on_button_clicked` callback function. What this means is that when the button is clicked the function named on\_button\_clicked will be called.

```python
import pygtk
pygtk.require("2.0")
import gtk

def on_button_clicked(widget, data=None):
  label_1.set_text("Hello " + str(data))
  label_1 = gtk.Label("Hello World!")
  label_2 = gtk.Label("Still in the HBox")
  button = gtk.Button("Click Me")

  # Connect the "clicked" signal of the button to
  # our callback function that we have named
  # on_button_clicked. It also passes the string
  # "Anything can go here" to the callback function.
  button.connect("clicked", on_button_clicked, "Anything can go here")

  vbox = gtk.VBox()
  vbox.pack_start(label_1)
  vbox.pack_start(label_2)
  vbox.pack_start(button)
  win = gtk.Window()

  win.connect("destroy", lambda wid: gtk.main_quit())
  win.add(vbox)
  win.show_all()
  gtk.main()
```

## Widgets

Many of the widgets that are going to be discussed here will make use of a smaller gtk gui that will be shown here. However there will be a few examples that will utilize an object oriented design. Here the basic gui that creates a window and adds a vertical box (gtk.VBox) to add our test widgets into.

<a id="sec-widgets-basegui"></a>

```python
#!/usr/bin/env python
import pygtk, gtk
pygtk.require('2.0')

def main():
  win = gtk.Window(gtk.WINDOW_TOPLEVEL)
  win.connect("delete_event", lambda wid, we: gtk.main_quit())
  vbox = gtk.VBox(True, 2)
  win.add(vbox)
  # Add widget code here
  win.show_all()

if __name__ == "__main__":
  main()
  gtk.main()
```

So when adding the code, from widgets discussed below, make sure it is between the win.add(vbox) and win.show\_all() lines. All the widget will be added to the widget *vbox*.

### Buttons {#sub-widgets-buttons}

To create a button the gtk.Button class is instantiated.

```python
button = gtk.Button("Click Me")
button.connect("clicked", button_callback, "Button Click Me")
vbox.pack_start(button, True, True, 2)
```

This code creates a button that displays the text "Click Me" on the button. It then connects the buttons when clicked to the *function button\_callback* and sends the data "Button Click Me" as a function argument. Make sure that the button\_callback function is declared before the code that calls it.

```python
def button_callback(widget=None, data=None):
  print "%s was clicked." % data
```

The function button\_callback prints the out a small message that includes the "Button Click Me" string that was sent as an argument.

### Radio Buttons {#sub-widgets-radiobutton}

Radio buttons are created using the gtk.RadioButton(group, label) class. Groups are used so that only one radio button can be selected at a time within a group. The label of course being the text that is displayed along with the radio button.

To create the first radio button pass the value None in for the group. Than for each radio button you want in the group pass the first button in as the group. The following code will now show this.

```python
button1 = gtk.RadioButton(None, "Radio Button 1")
button2 = gtk.RadioButton(button1, label="Radio Button 2")
button3 = gtk.RadioButton(button1, label="Radio Button 3")
```

These three lines show three radio buttons being created with the first one having a group of None. The second and third buttons however have the group set to button1. This way only one of the three buttons can be selected at one time.

Now the buttons are connected to a callback.

```python
button1.connect("toggled", button_callback, "Button 1")
button2.connect("toggled", button_callback, "Button 2")
button3.connect("toggled", button_callback, "Button 3")
```

What this does is connect any toggled (switching from one button to another) signal to the function `button_callback`.

```python
def button_callback(widget=None, data=None):
  print "%s was toggled %s" % (data, ("off","on")[widget.get_active()])
```

This fuction will print out the data argument "on" when the button is selected and "off" when another button is selected. What this means is that when button1 is currently selected and then button two is clicked it will print the lines:

```python
Button 1 was toggled off
Button 2 was toggled on
```

### Toggle Buttons {#sub-widgets-toggle-buttons}

Toggle buttons are very much the same as normal buttons except they are either in a state of *on* (clicked) or *off* (not clicked). They work much the same say that radio and check buttons work. Toggle buttons are created using the gtk.ToggleButton class and take as an argument a label.

```python
button1 = gtk.ToggleButton("Toggle Button 1")
button2 = gtk.ToggleButton("Toggle Button 2")
```

This code shows two toggle buttons being created. To make them useful they are connected to the *toggled* signal to call the function `button_callback` with "Button 1" and "Button 2" as function arguments.

```python
button1.connect("toggled", button_callback, "Button 1")
button2.connect("toggled", button_callback, "Button 2")

def button_callback(widget=None, data=None):
  print "%s was toggled  %s" % (data, ("off",
    "on")[widget.get_active()])
```

The button\_callback function will print on or off for each button as they are toggled. The widget.get\_active() method can be used to decide the code path by doing one action when toggled and another action when it is toggled off.

All that is left is to add the buttons to the gtk.VBox that is in the user interface code.

```python
vbox.pack_start(button1, True, True, 2)
vbox.pack_start(button2, True, True, 2)
```

### Check Buttons {#sub-widgets-check-buttons}

To create a check button with a label of "Check Me" do the following

```python
check_button = gtk.CheckButton("Check Me")
```

Unlike a normal button, instead of connecting to the *clicked* signal, a check button connects a callback to a *toggled* signal. So to do some action on the above you would connect like so:

```python
check_button.connect("toggled", check_button_callback, "callback data")
```

So this will call the function named `check_button_callback` whenever the check box is toggled(clicked). Take a look at the following example to see how to detect whether a check button is checked or not.

```python
def check_button_callback(widget, data=None):
  print "%s was toggled: %s" % (data, ("off", "on")[widget.get_active()])
```

This function takes the check button widget and print the string data that was passed in. It also prints "off" for when the button is not clicked and "on" when the button has been clicked.

Below is the code that is needed to create the buttons and connect them to the `check_button_callback` function.

```python
  button1 = gtk.CheckButton("check button 1")
  button1.connect("toggled", check_button_callback, "Button 1")
  vbox.pack_start(button1, True, True, 2)

  button2 = gtk.CheckButton("check button 2")
  button2.connect("toggled", check_button_callback, "Button 2")
  vbox.pack_start(button2, True, True, 2)
```

### Labels {#sub-widgets-labels}

To create a label just do something like this but replace the labels text with your own.

```python
label = gtk.Label("Your label")
```

If you wish to change the text later you can use the labels `set_text` method.

```python
label.set_text("My new label")
```

Now the label will display the text "My new label" instead of "Your label".

### Text Entries {#sub-widgets-text-entries}

The text entry example is slightly more complicated than the examples that have been shown so far. This is because besides the text entry, two buttons and a label will be used in this example. The first button called `print_button` is used to print retrieve the text from the text entry and place it into the label. The second button*, clear\_button,* is used to clear the text from the text entry and label.

To create a text entry the gtk.Entry class is used. By default it is gtk.Entry(max=0). The max argument is the is the size of characters that the entry can hold. If it is set to 0 then there is no limit.

The following code creates a gtk.Entry called text\_box with no limit on the size.

```python
text_box = gtk.Entry()

print_button = gtk.Button("Print Text")
print_button.connect("clicked", print_callback, text_box)

clear_button = gtk.Button("Clear Text")
clear_button.connect("clicked", clear_callback)
```

After creating a text box two buttons are created. The first, `print_button`, is connected to the `print_callback` function when it is clicked and passes as an argument the text\_box gtk.Entry widget as an argument.

The `print_callback` funtion receives the gtk.Entry `text_box` as the argument data and sets the text of the global gtk.Label label to the text that was entered in the `text_box` widget using the gtk.Entry method `get_text()`

```python
label = gtk.Label("Hello")
def print_callback(widget=None, data=None):
  label.set_text(data.get_text())
```

The clear\_callback function clears the text in the text entry and just for fun the label as well.

```python
def clear_callback(widget=None, data=None):
  text_box.set_text("")
  label.set_text("")
```

Now the widgets just need to be added to the gtk.VBox that is in the user interface code.

```python
vbox.pack_start(label, True, True, 2)
vbox.pack_start(text_box, True, True, 2)
vbox.pack_start(print_button, True, True, 2)
vbox.pack_start(clear_button, True, True, 2)
```

Here are some methods available with gtk.Entry:

- insert\_text(text, position=0)
- get\_text()
- set\_text(text)
- set\_max\_length(max)
- set\_editable(is\_editable) - True or False
- set\_visibility(visible) - True or False
- select\_region(start, end)

### Menus {#sub-widgets-menus}

![File Menu Screenshot](images/pygtk-introduction/menu-screenshot.png){: #fig-menu}

This section will cover adding menus to applications that most everyone should be used to. The standard menus such File -> Save, File -> Quit, and Help -> About. Of course after reading this section you will be more than capable to add what ever menu you wish.

The method used this section will be using is to create the menus using straight code. There is another method using the UIManager[^1] and if you would like you can look into that instead.

There are three main class that are used in creating menus and they are:

- gtk.MenuBar - Is added to the the programs main window and is a container for gtk.Menu and gtk.MenuItem
- gtk.Menu - Is a container to hold sub gtk.MenuItem items
- gtk.MenuItem - Is the actual menus items the user sees and actually clicks such as "File", "Save", and "Quit"

Looking at the code below, it can be seen that the menu bar is created using the class gtk.MenuBar. This is the object that will be added to the main windows, in this case the top of the gtk.VBox that is being used in this example.

```python
menubar = gtk.MenuBar()
file_item = gtk.MenuItem("_File")
help_item = gtk.MenuItem("_Help")
```

After the MenuBar is created two MenuItems are created, `file_item` and `help_item`, these of course will have other sub menu items attached to them that will be displayed when they are clicked. These are the main menu items that are seen in most applications along the top of the window (Eg. File, Edit, View, Tools, Help, etc...) In this case only *File* and *Help* are shown. The underscores before the F and H indicate that

Here find the menu container `file_item_sub` being created as a gtk.Menu object to hold the menu items that will be apended to the file\_item MenuItem. Save and quit are both created as gtk.MenuItem objects. These are then added to file\_item\_sub. A few lines further down, file\_item\_sub will be added to file\_item.

```python
file_item_sub = gtk.Menu()
save = gtk.MenuItem("_Save")
quit = gtk.MenuItem("_Quit")
file_item_sub.append(save)
file_item_sub.append(quit)
```

As was done with creating file\_item\_sub so to this done here creating help\_item\_sub. This is a submenu container to hold the MenuItems for the Help MenuItem.

```python
help_item_sub = gtk.Menu()
about = gtk.MenuItem("_About")
help_item_sub.append(about)
```

Finally here can be seen the submenus being added to their respective parent MenuItems and then the parent MenItems being added to the MenuBar.

```python
file_item.set_submenu(file_item_sub)
help_item.set_submenu(help_item_sub)
menubar.append(file_item)
menubar.append(help_item)
```

To finish off each menu item that is to have a user action connects to the activate signal that is emitted on its selection, each MenuItem calling its respective callback function. And lets not forget, the menubar is added to the gtk.VBox that was created in the base user interface code ([Widgets](01-pygtk-introduction.html#sec-widgets-basegui)).

```python
save.connect("activate", save_callback)
quit.connect("activate", quit_callback)
about.connect("activate", about_callback)
vbox.pack_start(menubar, True, True, 2)
```

For the sake of completness these are the callback functions; very simple and not very much, but you can use your own imagination as what should be done in your own program.

```python
def save_callback(widget=None):
  print "Save menu item was pressed"

def quit_callback(widget=None):
  print "Quit menu item was pressed"
  gtk.main_quit()

def about_callback(widget=None):
  print "About menu item was pressed"
```

### Message Dialogs {#sub-widgets-messagedialog}

![MessageDialog Example](images/pygtk-introduction/MessageDialog-screenshot.png){: #fig-messagedialog}

Message Dialogs are small windows that are smiple and easy to use. Using them is as simple as calling the gtk.MessageDialog class. The default constructor of this class looks like this.

```python
gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_INFO,
   buttons=gtk.BUTTONS_NONE, message_format=None)
```

The *parent* is either the parent window of None if none.

The flags can be one of the following:

- gtk.DIALOG\_MODAL
- gtk.DIALOG\_DESTROY\_WITH\_PARENT
- or 0 for no flags.

The *type* can be one of the following:

- gtk.MESSAGE\_INFO - display an information icon
- gtk.MESSAGE\_WARNING - display a warning icon
- gtk.MESSAGE\_QUESTION - display a question icon
- gtk.MESSAGE\_ERROR - display an error icon

The buttons available are:

- gtk.BUTTONS\_NONE
- gtk.BUTTONS\_OK
- gtk.BUTTONS\_CLOSE
- gtk.BUTTONS\_CANCEL
- gtk.BUTTONS\_YES\_NO
- gtk.BUTTONS\_OK\_CANCEL

These are the responses to the button types:

- gtk.RESPONSE\_NONE
- gtk.RESPONSE\_REJECT
- gtk.RESPONSE\_ACCEPT
- gtk.RESPONSE\_DELETE\_EVENT
- gtk.RESPONSE\_OK
- gtk.RESPONSE\_CANCEL
- gtk.RESPONSE\_CLOSE
- gtk.RESPONSE\_YES
- gtk.RESPONSE\_NO
- gtk.RESPONSE\_APPLY
- gtk.RESPONSE\_HELP

The `message_format` is the message that will be displayed. So far this seems as if it is not complicated and it is not.

Here is an example showing a MessageDialog displaying a question with buttons to answer yes or no. As can be seen the message dialog is instantied with the *parent* set to None, the *button* type is gtk.BUTTONS\_YES\_NO, the *flag* is gtk.DIALOG\_DESTROY\_WITH\_PARENT. The *type* is set to gtk.MESSAGE\_QUESTION to go along with the yes/no button. The message that is displayed is "Is this a good example?".

```python
def button_callback(widget=None):
  dialog = gtk.MessageDialog(parent = None,
      buttons = gtk.BUTTONS_YES_NO,
      flags =gtk.DIALOG_DESTROY_WITH_PARENT,
      type = gtk.MESSAGE_QUESTION,
      message_format = "Is this a good example?")

  dialog.set_title("MessageDialog Example")
  result = dialog.run()
  dialog.destroy()

  if result == gtk.RESPONSE_YES:
    print "Yes was clicked"
  elif result == gtk.RESPONSE_NO:
    print "No was clicked"
```

After the Message dialog is assigned to the variable *dialog* the title of the dialog window is set to "MessageDialog Example". To run a dialog you must use the dialogs *run* method. The dialogs run method returns the result of the buttons that was clicked. This can be used to determine the course of action.

As can be seen in the example if the Yes buttons is clicked the message "Yes was clicked" is printed and if No is clicked the message "No was clicked" is printed. Also make sure that you remember to also call the dialogs *destroy* method otherwise it will never close. So `dialog.destroy()` is called on the line immedialty following `dialog.run()`.

Finally, lets not forget the code to display the button that will run the button\_callback function:

```python
button = gtk.Button("Show Dialog")
button.connect("clicked", button_callback)
vbox.pack_start(button, True, True, 2)
```

As can be seen the message dialog is easy to use and it makes it simple to display information, warnings, errors, or questions to the user.

### Spin Buttons {#sub-widgets-spinbutton}

![SpinButton Screenshot](images/pygtk-introduction/spinbutton-screenshot.png){: #fig-widgets-spinbutton-screenshot}

To create a spin button the gtk.SpinButton class is used.

```python
spin_button = gtk.SpinButton(adjustment=None, climb_rate=0.0, digits=0)
```

The adjustment is as follows:

```python
adjustment = gtk.Adjustment(value=0, lower=0, upper=0, step_incr=0,
    page_incr=0, page_size=0)
```

- value -initial value for the Spin Button
- lower - lower range value
- upper - upper range value
- step\_incr - value to increment/decrement when pressing mouse button-1 on a button
- step\_incr - value to increment/decrement when pressing mouse button-2 on a button
- page\_size unused

In this example andjustment is created with an inital value and lower limit of 0, an upper limit of 100, a step increment of 1, a page increment 5, and page size of 0)

```python
  #gtk.Adjustment(value=0, lower=0, upper=0, step_incr=0, page_incr=0, page_size=0)
   adjustment = gtk.Adjustment(0, 0, 100, 1, 5, 0)
   spin = gtk.SpinButton(adjustment, 0, 0)
   vbox.pack_start(spin, True, True, 2)
```

Here a button is added that will call the button\_callback function.

```python
   button = gtk.Button("Print SpinButton Value")
   button.connect("clicked", button_callback, spin)
   vbox.pack_start(button, True, True, 2)
```

The button callback prints the value of the spinbutton, first as a float and secondly as an integer.

```python
def button_callback(widget=None, spin=None):
  print spin.get_value()
  print spin.get_value_as_int()
```

For much more information and details on the gtk.SpinButton class see the PyGTK tutorial at: <http://www.pygtk.org>

### Combo Box

The easy way to create and populate a ComboBox is to use one of the following functions:

```python
# Setup up a read only combobox
item_list = gtk.combo_box_new_text()

# Setup a combobox that users may add to
item_list = gtk.combo_box_entry_new_text()
```

Using either of these functions setups a combo box and provides some easy to use convience functions. These are the methods that are provided when using combo\_box\_new\_text:

- append\_text(text)
- prepend\_text(text)
- insert\_text(position, text)
- combobox.remove\_text(position)

The example that will be shown below will use the second function, gtk.combo\_box\_entry\_new\_text, because it provides everything that the gtk.combo\_box\_new\_text does plus allows the user to update the list by typing in new data directly. If this functionality is not needed then it can be avoided by using the first function and not using the code below that pertains to adding new list items.

Now the ComboBox example will break from using the user interface supplied at the at the begginning of the widget section ([Widgets](01-pygtk-introduction.html#sec-widgets-basegui)), as it will use a slightly modified version so that it will now be used within a class. The example will use the same basic code but will now be within the CodeExample class that will be created. The only reason for this is because the author (thats me) does not like using global variables when it can be avoided.

```python
class ComboExample:
  def __init__(self):
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("delete_event", lambda wid, we: gtk.main_quit())
    vbox = gtk.VBox(True, 2)
    win.add(vbox)
```

So far the code is the same except instead of the main function the user interface code is in the \_\_init\_\_ method. Now the actual code for the comboboxes.

First the list default\_items is created to hold a couple of items that will be placed in the combobox, the combo box is created right beneath this using the function combo\_box\_entry\_new\_text. Using this function means that this will combobox will allow its users to enter text directly into a text entry that is provided in the combobox.

```python
    default_items = ["hello", "World"]
    self.item_list = gtk.combo_box_entry_new_text()
    self.item_list.child.connect('key-press-event',
        self.item_list_changed)
    for x in default_items:
      self.item_list.append_text(x)
```

After the combobox has been created and assisigned to the variable self.item\_list it is connects the key-press-event signal to all the item\_list\_changed method. The reason for doing this is to detect when text is entered into the combobox text entry area by the user. Following this the default\_items list is appended into the combox box using the append\_text method. Very simple, very easy.

To show how to retrieve the selected item a button is added that when clicked will retrieve the combobox item that is selected by calling the print\_selected\_item method.

```python
    button = gtk.Button("Print Selected Item")
    button.connect("clicked", self.print_selected_item)
    vbox.pack_start(self.item_list, True, True, 2)
    vbox.pack_start(button, True, True, 2)
    win.show_all()
```

The item\_list\_changed method is called every time there is a changed in the combobox text entry field. What this means is everytime a character is entered by a user this method is called and checks what keyboard button is pressed. If the keyboard character pressed is Return (Enter) than the text entry is append to the item\_list using the its append\_text method and then sets the combobox text entry back to an empty string.

```python
    def item_list_changed(self, widget=None, event=None):
      key = gtk.gdk.keyval_name(event.keyval)
      if key == "Return":
        self.item_list.append_text(widget.get_text())
        widget.set_text("")
```

The print\_selected\_item method is called when the button is pressed. Its sole purpose is to retrieve what item is selected in the combox. If there are no items selected then None is returend. Else the item is printed and also returned.

```python
     def print_selected_item(self, widget=None):
       model = self.item_list.get_model()
       active = self.item_list.get_active()
       if active < 0:
         return None
       print model[active][0]
       return model[active][0]
```

As can be seen to retrieve the selected items the combobox item\_list methods `get_model` and `get_active` most be used. The model is a gtk.TreeModel. If the active number is less than 0 then there are no selected items, otherwise is the postion of the selected item.

```python
if __name__ == "__main__":
  ComboExample()
  gtk.main()
```

### Statusbar {#sub-widgets-statusbar}

The status bar will break from using the user interface supplied at the beggining of this widget section, as it will use a slightly modified version so that it will now be used within a class. The example will use the same basic code but will now be within the StatusbarTest class that will be created. The only reason for this is because the author (thats me) does not like using global variables for no particular reason, I just do not like doing it unless it is a constant variable.

![Statusbar Example](images/pygtk-introduction/statusbar-screenshot.png){: #fig-statusbar-example}

Now that the user interface is within a class it is easy to work with multiple widgets by making them class level instance variables.

When working with the gtk.Statusbar class the important methods to know are:

- gtk.Statusbar() - Well not really a method but create an instance of the class
- pop(context\_id) - Remove the top level message
- push(context\_id, text) - Add a new top level message
- get\_context\_id(context\_id) - Used to retrieve the context that is used with the *pop* and *push* methods

```python
class StatusbarTest(object):
  def __init__(self):
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("delete_event", lambda wid, we: gtk.main_quit())
    vbox = gtk.VBox(False, 2)
    win.add(vbox)
```

So next is the code for creating the Statusbar. As can be seen once it is created a context\_id variable is assinged by using the statusbars `get_context_id` method using the context\_id "Status Test". So whenever a message needs to be popped or pushed it needs to use the context id that was created with the `get_context_id` method.

```python
    self.statusbar = gtk.Statusbar()
    self.context_id = self.statusbar.get_context_id("Status Test")
```

The rest of the code here is common user interface code that has been common throught the widget section, all it does is create a text entry and a button.

```python
    self.text_entry = gtk.Entry()
    button = gtk.Button("Click Me")
    button.connect("clicked", self.button_callback)

    vbox.pack_start(self.text_entry, False, True, 2)
    vbox.pack_start(button, True, True, 2)
    vbox.pack_start(self.statusbar, False, True, 2)

    win.show_all()
```

Here is the rest of the interesting code. First thing that is done in the button\_callback function is to remove the top level message using the pop method. Next the new message is displayed to the statusbar using the push method, the text is taken from the text entry widget. To test it out run the code, type something into the text entry and click the button.

```python
  def button_callback(self, widget=None):
    self.statusbar.pop(self.context_id)
    self.statusbar.push(self.context_id, self.text_entry.get_text())
```

The rest of the boring code that is needed to run the example.

```python
if __name__ == "__main__":
  StatusbarTest()
  gtk.main()
```

See [Statusbar Example](01-pygtk-introduction.html#fig-statusbar-example) to see what this example looks like.

[^1]: <http://www.pygtk.org/pygtk2tutorial/sec-UIManager.html>
