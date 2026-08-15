#!/usr/bin/env python3
"""A custom widget that draws with GtkSnapshot instead of Cairo.

GTK 4 does not paint with Cairo any more. Widgets build a tree of render nodes
in do_snapshot(), and GSK hands that tree to the GPU. A GtkDrawingArea is a
widget that wraps one Cairo node, which is why Cairo still works -- but a widget
that draws in rectangles, rounded borders and gradients is faster and sharper
without it.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Graphene, Gsk, Gtk


def rgba(red, green, blue, alpha=1.0):
    """Boxed types like GdkRGBA are built empty and filled in, not constructed."""
    colour = Gdk.RGBA()
    colour.red, colour.green, colour.blue, colour.alpha = red, green, blue, alpha
    return colour


def color_stop(offset, colour):
    stop = Gsk.ColorStop()
    stop.offset = offset
    stop.color = colour
    return stop


class Meter(Gtk.Widget):
    """A bar that fills up, drawn entirely from render nodes."""

    __gtype_name__ = "Meter"

    def __init__(self, fraction=0.6):
        super().__init__()
        self.fraction = fraction
        self.set_size_request(-1, 24)

    def do_snapshot(self, snapshot):
        width = self.get_width()
        height = self.get_height()

        track = Graphene.Rect().init(0, 0, width, height)
        filled = Graphene.Rect().init(0, 0, width * self.fraction, height)

        radius = Graphene.Size().init(height / 2, height / 2)
        rounded = Gsk.RoundedRect()
        rounded.init(track, radius, radius, radius, radius)

        # Everything after push_rounded_clip is clipped to the rounded rectangle.
        snapshot.push_rounded_clip(rounded)
        snapshot.append_color(rgba(0.9, 0.9, 0.89), track)
        snapshot.append_linear_gradient(
            filled,
            Graphene.Point().init(0, 0),
            Graphene.Point().init(width, 0),
            [
                color_stop(0.0, rgba(0.25, 0.5, 0.9)),
                color_stop(1.0, rgba(0.55, 0.3, 0.85)),
            ],
        )
        snapshot.pop()

    def set_fraction(self, fraction):
        self.fraction = max(0.0, min(1.0, fraction))
        self.queue_draw()


def on_activate(app):
    window = Gtk.ApplicationWindow(application=app, title="Snapshot Widget")
    window.set_default_size(400, 160)

    meter = Meter(0.35)

    scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 0.01)
    scale.set_value(0.35)
    scale.connect("value-changed", lambda s: meter.set_fraction(s.get_value()))

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
    box.set_margin_top(24)
    box.set_margin_bottom(24)
    box.set_margin_start(24)
    box.set_margin_end(24)
    box.append(meter)
    box.append(scale)

    window.set_child(box)
    window.present()


app = Gtk.Application(application_id="com.example.SnapshotWidget")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
