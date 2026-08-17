#!/usr/bin/env python3
"""Connecting a signal to a callback, with and without extra data."""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def on_button_clicked(button: Gtk.Button) -> None:
    button.set_label("Clicked!")


def on_counter_clicked(button: Gtk.Button, state: dict[str, int]) -> None:
    state["count"] += 1
    button.set_label(f"Clicked {state['count']} times")


def on_activate(app: Gtk.Application) -> None:
    window = Gtk.ApplicationWindow(application=app, title="Callbacks")
    window.set_default_size(320, 140)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    plain = Gtk.Button(label="Click me")
    plain.connect("clicked", on_button_clicked)

    # Anything passed after the callback is handed back to it unchanged.
    counter = Gtk.Button(label="Clicked 0 times")
    counter.connect("clicked", on_counter_clicked, {"count": 0})

    box.append(plain)
    box.append(counter)
    window.set_child(box)
    window.present()


app = Gtk.Application(application_id="com.example.Callbacks")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
