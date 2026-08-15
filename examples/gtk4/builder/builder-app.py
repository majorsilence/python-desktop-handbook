#!/usr/bin/env python3
"""Building a window from a .ui file with GtkTemplate.

Glade cannot edit GTK 4 files.  The format it wrote lives on as GtkBuilder XML,
which you write by hand, generate from Blueprint, or edit in Cambalache.

Gtk.Template binds a class to a <template> in a .ui file: children marked with an
id become attributes, and handlers named in <signal> are found on the class.
"""

import pathlib
import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

UI_FILE = pathlib.Path(__file__).parent / "window.ui"


@Gtk.Template(filename=str(UI_FILE))
class ExampleWindow(Gtk.ApplicationWindow):
    # Must match the class attribute of <template> in the .ui file.
    __gtype_name__ = "ExampleWindow"

    # Each of these matches an id in the .ui file.
    name_entry = Gtk.Template.Child()
    greet_button = Gtk.Template.Child()
    greeting = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def on_greet_clicked(self, _button):
        name = self.name_entry.get_text().strip() or "stranger"
        self.greeting.set_text(f"Hello, {name}!")


def on_activate(app):
    ExampleWindow(application=app).present()


app = Gtk.Application(application_id="com.example.BuilderApp")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
