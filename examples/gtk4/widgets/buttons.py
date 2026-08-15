#!/usr/bin/env python3
"""The three ways a GTK 4 button carries a label: text, icon, or both."""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def on_clicked(button, message):
    print(message)


def on_activate(app):
    window = Gtk.ApplicationWindow(application=app, title="Buttons")
    window.set_default_size(520, 120)

    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    text = Gtk.Button(label="Save")
    text.connect("clicked", on_clicked, "text button clicked")

    icon = Gtk.Button(icon_name="document-save-symbolic")
    icon.set_tooltip_text("Save")
    icon.connect("clicked", on_clicked, "icon button clicked")

    # For an icon and a label together, put a box inside the button.
    content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    content.append(Gtk.Image.new_from_icon_name("document-save-symbolic"))
    content.append(Gtk.Label(label="Save As"))
    both = Gtk.Button(child=content)
    both.connect("clicked", on_clicked, "icon+label button clicked")

    # A button can be styled to signal what it does.
    suggested = Gtk.Button(label="Confirm")
    suggested.add_css_class("suggested-action")
    destructive = Gtk.Button(label="Delete")
    destructive.add_css_class("destructive-action")

    for button in (text, icon, both, suggested, destructive):
        box.append(button)

    window.set_child(box)
    window.present()


app = Gtk.Application(application_id="com.example.Buttons")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
