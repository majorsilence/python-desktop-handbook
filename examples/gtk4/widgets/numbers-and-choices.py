#!/usr/bin/env python3
"""Spin buttons, scales and drop downs.

GtkComboBoxText is deprecated in GTK 4; GtkDropDown replaces it.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def on_activate(app):
    window = Gtk.ApplicationWindow(application=app, title="Numbers and choices")
    window.set_default_size(360, 220)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    # min, max, step.  Use get_value_as_int() when you want an int back.
    spin = Gtk.SpinButton.new_with_range(0, 100, 1)
    spin.set_value(25)
    spin.connect("value-changed", lambda s: print("spin:", s.get_value_as_int()))
    box.append(spin)

    scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
    scale.set_draw_value(True)
    scale.set_value(50)
    scale.connect("value-changed", lambda s: print("scale:", round(s.get_value())))
    box.append(scale)

    # A drop down over a plain list of strings.
    flavours = ["Vanilla", "Chocolate", "Strawberry"]
    dropdown = Gtk.DropDown.new_from_strings(flavours)
    dropdown.connect(
        "notify::selected",
        lambda d, _p: print("chose:", flavours[d.get_selected()]),
    )
    box.append(dropdown)

    window.set_child(box)
    window.present()


app = Gtk.Application(application_id="com.example.NumbersAndChoices")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
