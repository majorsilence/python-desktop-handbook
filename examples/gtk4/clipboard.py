#!/usr/bin/env python3
"""Copy and paste with GdkClipboard.

The clipboard belongs to the display, not to your window, so you get it from a
widget: `widget.get_clipboard()`. There are two of them on Linux -- the ordinary
clipboard that Ctrl+C fills, and the *primary* selection that middle-click
pastes, which is filled just by selecting text. Respect both; only one of them
is yours to write on Ctrl+C.

Reading is asynchronous, and has to be: on Wayland the content lives in whatever
application owns the selection, and fetching it is inter-process communication.
There is no `get_text()` that returns a string, and there was never a safe one.
"""

import sys

from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk


class Window(Adw.ApplicationWindow):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.set_title("Clipboard")
        self.set_default_size(480, 340)

        self.entry = Gtk.Entry(text="Something worth copying",
                               placeholder_text="Type, then copy")
        self.status = Gtk.Label(xalign=0, wrap=True, label="—")
        self.picture = Gtk.Picture(vexpand=True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.append(self.entry)

        for label, handler in (
            ("Copy the text", self.on_copy),
            ("Paste text", self.on_paste),
            ("Paste an image", self.on_paste_image),
        ):
            button = Gtk.Button(label=label)
            button.connect("clicked", handler)
            box.append(button)

        box.append(self.status)
        box.append(self.picture)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar())
        toolbar.set_content(box)
        self.set_content(toolbar)

    # -- writing ----------------------------------------------------------------

    def on_copy(self, _button: Gtk.Button) -> None:
        # set() takes a Python value and works out the content formats to
        # advertise. Underneath it is set_content(Gdk.ContentProvider), which is
        # what you use directly when you want to offer several formats at once
        # -- say, both text/plain and text/html -- via ContentProvider.new_union.
        self.get_clipboard().set(self.entry.get_text())
        self.status.set_text("Copied. Paste it somewhere else to prove it.")

    # -- reading ----------------------------------------------------------------

    def on_paste(self, _button: Gtk.Button) -> None:
        self.status.set_text("reading…")
        self.get_clipboard().read_text_async(None, self.on_text_ready)

    def on_text_ready(self, clipboard: Gdk.Clipboard, result: Gio.AsyncResult) -> None:
        try:
            text = clipboard.read_text_finish(result)
        except GLib.Error as error:
            # The normal failure: the clipboard holds something that is not
            # text, or is empty. Not an exceptional case -- handle it quietly.
            self.status.set_text(f"nothing to paste ({error.message})")
            return
        self.status.set_text(f"pasted {len(text or '')} characters: {text!r}")

    def on_paste_image(self, _button: Gtk.Button) -> None:
        self.status.set_text("reading an image…")
        self.get_clipboard().read_texture_async(None, self.on_texture_ready)

    def on_texture_ready(self, clipboard: Gdk.Clipboard, result: Gio.AsyncResult) -> None:
        try:
            texture = clipboard.read_texture_finish(result)
        except GLib.Error as error:
            self.status.set_text(f"no image on the clipboard ({error.message})")
            return
        self.picture.set_paintable(texture)
        self.status.set_text(f"pasted a {texture.get_width()}×{texture.get_height()} image")


def on_activate(app: Adw.Application) -> None:
    Window(application=app).present()


app = Adw.Application(application_id="com.example.Clipboard")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
