#!/usr/bin/env python3
"""Cairo inside a widget.

GTK 3's "draw" signal and GTK 2's "expose-event" are gone.  A GtkDrawingArea is
given a draw function, and GTK calls it with a context and the current size.
"""

import math
import sys

import cairo
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def draw(_area: Gtk.DrawingArea, context: cairo.Context,
         width: int, height: int) -> None:
    """Called whenever the area needs repainting. Never call it yourself."""
    # The context is already clipped to the area, and the origin is its top left.
    context.set_source_rgb(0.98, 0.97, 0.94)
    context.paint()

    # Draw relative to the size you were handed, not to a size you assumed.
    centre_x, centre_y = width / 2, height / 2
    radius = min(width, height) / 2 - 20

    context.set_source_rgb(0.2, 0.4, 0.8)
    context.arc(centre_x, centre_y, radius, 0, 2 * math.pi)
    context.fill()

    context.set_source_rgb(1, 1, 1)
    context.set_line_width(6)
    context.arc(centre_x, centre_y, radius / 2, 0, math.pi)
    context.stroke()


def on_activate(app: Gtk.Application) -> None:
    window = Gtk.ApplicationWindow(application=app, title="Drawing Area")
    window.set_default_size(400, 300)

    area = Gtk.DrawingArea()
    area.set_draw_func(draw)
    area.set_hexpand(True)
    area.set_vexpand(True)

    window.set_child(area)
    window.present()


app = Gtk.Application(application_id="com.example.DrawingArea")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
