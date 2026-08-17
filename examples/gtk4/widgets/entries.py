#!/usr/bin/env python3
"""Single-line entries, password entries, search entries and multi-line text."""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def on_activate(app: Gtk.Application) -> None:
    window = Gtk.ApplicationWindow(application=app, title="Entries")
    window.set_default_size(420, 320)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    entry = Gtk.Entry(placeholder_text="Your name")
    # "activate" fires on Enter; "changed" fires on every keystroke.
    entry.connect("activate", lambda e: print("entered:", e.get_text()))
    entry.connect("changed", lambda e: print("now:", e.get_text()))
    box.append(entry)

    password = Gtk.PasswordEntry(show_peek_icon=True)
    box.append(password)

    search = Gtk.SearchEntry()
    search.connect("search-changed", lambda e: print("searching for:", e.get_text()))
    box.append(search)

    # Multi-line text lives in a GtkTextView backed by a GtkTextBuffer.
    view = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD)
    view.get_buffer().set_text("Several lines of text\ngo in a GtkTextView.")
    scroller = Gtk.ScrolledWindow(vexpand=True)
    scroller.set_child(view)
    box.append(scroller)

    def report(_button: Gtk.Button) -> None:
        buffer = view.get_buffer()
        start, end = buffer.get_bounds()
        print("name:", entry.get_text())
        print("password length:", len(password.get_text()))
        print("text:", buffer.get_text(start, end, False))

    button = Gtk.Button(label="Read the values")
    button.connect("clicked", report)
    box.append(button)

    window.set_child(box)
    window.present()


app = Gtk.Application(application_id="com.example.Entries")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
