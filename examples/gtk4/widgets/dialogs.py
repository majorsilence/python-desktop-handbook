#!/usr/bin/env python3
"""Asking the user a question with GtkAlertDialog.

GtkMessageDialog and GtkDialog are deprecated in GTK 4.10.  GtkAlertDialog
replaces them and is asynchronous: you hand it a callback and get control back
immediately, rather than running a nested main loop and waiting for an answer.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GLib, Gtk


def ask_to_delete(window: Gtk.Window, label: Gtk.Label) -> None:
    dialog = Gtk.AlertDialog()
    dialog.set_message("Delete this file?")
    dialog.set_detail("Once it is gone it is gone. There is no undo.")
    dialog.set_buttons(["Cancel", "Delete"])
    dialog.set_cancel_button(0)   # chosen by Escape
    dialog.set_default_button(1)  # chosen by Enter
    dialog.choose(window, None, on_choice, label)


def on_choice(dialog: Gtk.AlertDialog, result: Gio.AsyncResult,
              label: Gtk.Label) -> None:
    try:
        button = dialog.choose_finish(result)
    except GLib.Error:
        # Raised when the dialog was dismissed rather than answered.
        label.set_text("Dismissed")
        return
    label.set_text("Deleted" if button == 1 else "Cancelled")


def show_note(window: Gtk.Window) -> None:
    """A dialog with a single button needs no callback at all."""
    dialog = Gtk.AlertDialog()
    dialog.set_message("Nothing happened")
    dialog.set_detail("This is what a plain notice looks like.")
    dialog.show(window)


def on_activate(app: Gtk.Application) -> None:
    window = Gtk.ApplicationWindow(application=app, title="Dialogs")
    window.set_default_size(360, 160)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    label = Gtk.Label(label="No answer yet")

    ask = Gtk.Button(label="Delete something")
    ask.connect("clicked", lambda _b: ask_to_delete(window, label))

    note = Gtk.Button(label="Show a notice")
    note.connect("clicked", lambda _b: show_note(window))

    box.append(ask)
    box.append(note)
    box.append(label)
    window.set_child(box)
    window.present()


app = Gtk.Application(application_id="com.example.Dialogs")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
