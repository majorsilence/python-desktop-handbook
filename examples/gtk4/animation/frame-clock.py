#!/usr/bin/env python3
"""Animating by hand, against the frame clock.

Every widget has a frame clock, and add_tick_callback() runs a function once per
frame with the current time. This is the low level: no easing, no interpolation,
just "it is now t, draw the frame for t".

Never animate with GLib.timeout_add(16, ...). A timeout is not synchronised with
the display, so frames arrive slightly early or late and the motion judders.
"""

import math
import sys

import cairo
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GLib, Gtk

PERIOD_US = 3_000_000        # one full circuit, in microseconds


class Orbit(Gtk.DrawingArea):
    def __init__(self) -> None:
        super().__init__()
        self.start_time = None
        self.phase = 0.0
        self.set_draw_func(self.on_draw)
        self.set_content_width(320)
        self.set_content_height(220)

        # The callback runs until it returns GLib.SOURCE_REMOVE, and stops on its
        # own if the widget is unmapped.
        self.add_tick_callback(self.on_tick)

    def on_tick(self, widget: Gtk.Widget, frame_clock: Gdk.FrameClock) -> bool:
        # Frame time is monotonic and in microseconds. Use the clock's time, not
        # time.monotonic(): it is the time the frame will be *displayed*, which is
        # what keeps motion smooth.
        now = frame_clock.get_frame_time()
        if self.start_time is None:
            self.start_time = now

        elapsed = (now - self.start_time) % PERIOD_US
        self.phase = elapsed / PERIOD_US

        widget.queue_draw()
        return GLib.SOURCE_CONTINUE

    def on_draw(self, _area: Gtk.DrawingArea, cr: cairo.Context,
                width: int, height: int) -> None:
        cr.set_source_rgb(0.99, 0.98, 0.96)
        cr.paint()

        centre_x, centre_y = width / 2, height / 2
        radius = min(width, height) / 3
        angle = self.phase * 2 * math.pi

        cr.set_source_rgb(0.85, 0.85, 0.82)
        cr.set_line_width(1)
        cr.arc(centre_x, centre_y, radius, 0, 2 * math.pi)
        cr.stroke()

        cr.set_source_rgb(0.2, 0.4, 0.8)
        cr.arc(centre_x + radius * math.cos(angle),
               centre_y + radius * math.sin(angle),
               12, 0, 2 * math.pi)
        cr.fill()


def on_activate(app: Gtk.Application) -> None:
    window = Gtk.ApplicationWindow(application=app, title="Frame clock")
    window.set_default_size(360, 260)
    window.set_child(Orbit())
    window.present()


app = Gtk.Application(application_id="com.example.FrameClock")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
