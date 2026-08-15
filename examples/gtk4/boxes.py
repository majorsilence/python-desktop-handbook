#!/usr/bin/env python3
"""Laying widgets out with nested boxes."""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def on_activate(app):
    window = Gtk.ApplicationWindow(application=app, title="Boxes")
    window.set_default_size(360, 140)

    # The outer box stacks its children top to bottom.
    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    outer.set_margin_top(12)
    outer.set_margin_bottom(12)
    outer.set_margin_start(12)
    outer.set_margin_end(12)

    # The inner box lays its children out left to right.
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    row.append(Gtk.Label(label="Hello World!"))
    row.append(Gtk.Label(label="Still in the row"))

    outer.append(row)
    outer.append(Gtk.Button(label="This button is below the row"))

    window.set_child(outer)
    window.present()


app = Gtk.Application(application_id="com.example.Boxes")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
