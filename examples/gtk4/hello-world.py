#!/usr/bin/env python3
"""The smallest useful GTK 4 program: an application with one window."""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def on_activate(app: Gtk.Application) -> None:
    window = Gtk.ApplicationWindow(application=app, title="Hello World")
    window.set_default_size(320, 120)
    window.set_child(Gtk.Label(label="Hello World!"))
    window.present()


app = Gtk.Application(application_id="com.example.HelloWorld")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
