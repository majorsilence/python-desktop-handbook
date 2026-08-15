---
layout: chapter
title: "IronPython and Gtk-Sharp"
number: 11
---

> Please send any fixes or suggestions to peter@majorsilence.com or leave a comment at http://www.majorsilence.com/pygtk\_book.

## Introduction

The purpose of this chapter is to introduce using Gtk with IronPython. It will include a few short examples covering:

- Layouts with Gtk.VBox and Gtk.HBox
- Gtk.Buttons
- Gtk.Entry
- Widget Events (Callbacks)
- Gtk.MessageDialog
- Gtk.Label
- Gtk.CheckButton
- Gtk.RadioButton
- Gtk.ComboBox
- Gtk.Statusbar
- Gtk.StatusIcon

## Example 1

Example 1 shows the basics of using:

- Layouts with Gtk.VBox
- Gtk.Buttons
- Gtk.Entry
- Widget Events (Callbacks)
- Message Dialogs

To use Gtk Sharp from IronPython first you need to import the clr and add a reference to the gtk-sharp. Once this is finished you can import Gtk. The example below creates one window, adds a Gtk.Entry and Gtk.Button. The button has one event which is the self.HelloWorld function. The self.HelloWorld function displays a MessageDialog that will change the gtk.Entry default value to "Hello World!" if Yes is clicked. A Gtk.VBox is created and added to the window. This vbox is used to pack the self.textentry1 and button vertically. You can also use a Gtk.HBox instead or a combination of Gtk.VBox and Gtk.HBox.

Gtk.Application.Init() must be called before using Gtk and Gtk.Application.Run() starts the Gtk main event loop. The window has the DeleteEvent attached to call the self.DeleteEvent function. The self.DeleteEvent function alls Gtk.Application.Quite() which exits the application.

```python
import clr
clr.AddReference('gtk-sharp')
import Gtk

class GtkExample(object):
    def __init__(self):
        Gtk.Application.Init()
        self.window = Gtk.Window("Hello World")
        self.window.DeleteEvent += self.DeleteEvent

        vbox = Gtk.VBox()

        button = Gtk.Button("Show Message")
        button.Clicked += self.HelloWorld

        self.textentry1 = Gtk.Entry("Default Text")
        vbox.PackStart(self.textentry1)

        vbox.PackStart(button)

		self.window.Add(vbox)
        self.window.ShowAll()
        Gtk.Application.Run()

    def DeleteEvent(self, widget, event):
        Gtk.Application.Quit()

    def HelloWorld(self, widget, event):
        m = Gtk.MessageDialog(None, Gtk.DialogFlags.Modal, Gtk.MessageType.Info, \
            Gtk.ButtonsType.YesNo, False, 'Change the text entry to "Hello World?"')

        result = m.Run()
        m.Destroy()

        if result == int(Gtk.ResponseType.Yes):
            self.textentry1.Text = "Hello World!"

if __name__ == "__main__":
    GtkExample()
```

## Summary

At this point you should be able to create a basic Gtk application using IronPython and be able to extrapolate based on the c# gtk documation how to use more features from within IronPython.
