#!/usr/bin/env python3
"""A drawing that responds to the pointer.

Two things make custom drawing interactive: an event controller to hear about
input, and queue_draw() to ask for a repaint. Never call the draw function
yourself -- GTK decides when to redraw, and may coalesce several requests.
"""

import sys

import cairo
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class Sketch(Gtk.DrawingArea):
    def __init__(self) -> None:
        super().__init__()
        self.points = []
        self.hover = None

        self.set_draw_func(self.on_draw)
        self.set_hexpand(True)
        self.set_vexpand(True)

        click = Gtk.GestureClick()
        click.connect("pressed", self.on_pressed)
        self.add_controller(click)

        motion = Gtk.EventControllerMotion()
        motion.connect("motion", self.on_motion)
        motion.connect("leave", self.on_leave)
        self.add_controller(motion)

    def on_draw(self, _area: Gtk.DrawingArea, cr: cairo.Context,
                width: int, height: int) -> None:
        cr.set_source_rgb(0.99, 0.98, 0.96)
        cr.paint()

        cr.set_source_rgb(0.85, 0.85, 0.82)
        cr.set_line_width(1)
        for x in range(0, width, 20):
            cr.move_to(x + 0.5, 0)          # the half pixel keeps the line crisp
            cr.line_to(x + 0.5, height)
        for y in range(0, height, 20):
            cr.move_to(0, y + 0.5)
            cr.line_to(width, y + 0.5)
        cr.stroke()

        if len(self.points) > 1:
            cr.set_source_rgb(0.2, 0.4, 0.8)
            cr.set_line_width(2)
            cr.move_to(*self.points[0])
            for point in self.points[1:]:
                cr.line_to(*point)
            cr.stroke()

        cr.set_source_rgb(0.8, 0.3, 0.2)
        for x, y in self.points:
            cr.arc(x, y, 4, 0, 6.2832)
            cr.fill()

        if self.hover is not None:
            cr.set_source_rgba(0.2, 0.4, 0.8, 0.35)
            cr.arc(self.hover[0], self.hover[1], 10, 0, 6.2832)
            cr.fill()

    def on_pressed(self, gesture: Gtk.GestureClick, n_press: int,
                   x: float, y: float) -> None:
        if n_press == 2:
            self.points.clear()             # double click starts over
        else:
            self.points.append((x, y))
        self.queue_draw()

    def on_motion(self, _controller: Gtk.EventControllerMotion,
                  x: float, y: float) -> None:
        self.hover = (x, y)
        self.queue_draw()

    def on_leave(self, _controller: Gtk.EventControllerMotion) -> None:
        self.hover = None
        self.queue_draw()


def on_activate(app: Gtk.Application) -> None:
    window = Gtk.ApplicationWindow(application=app, title="Click to draw")
    window.set_default_size(480, 360)
    window.set_child(Sketch())
    window.present()


app = Gtk.Application(application_id="com.example.Sketch")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
