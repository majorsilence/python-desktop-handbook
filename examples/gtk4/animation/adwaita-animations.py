#!/usr/bin/env python3
"""Animation the way libadwaita does it.

An AdwAnimation is three things: a widget (for the frame clock), a range of
values, and a target that receives each value. Two kinds:

  AdwTimedAnimation   runs for a fixed duration through an easing curve
  AdwSpringAnimation  runs until a simulated spring settles, with no fixed duration

The target decides what the value does. A property target writes it to a GObject
property; a callback target hands it to a function.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk

EASINGS = [
    ("Linear", Adw.Easing.LINEAR),
    ("Ease in out cubic", Adw.Easing.EASE_IN_OUT_CUBIC),
    ("Ease out bounce", Adw.Easing.EASE_OUT_BOUNCE),
    ("Ease in out back", Adw.Easing.EASE_IN_OUT_BACK),
]


class Window(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Animations")
        self.set_default_size(520, 320)

        self.dot = Gtk.Image.new_from_icon_name("media-record-symbolic")
        self.dot.set_pixel_size(48)
        self.dot.set_halign(Gtk.Align.START)
        self.dot.set_valign(Gtk.Align.CENTER)

        track = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        track.set_size_request(-1, 80)
        track.append(self.dot)

        # -- a timed animation driving a callback ------------------------------
        #
        # The callback target is the general case: the value is a float and what
        # it means is up to you. Here it is a left margin, which moves the dot.
        self.slide = Adw.TimedAnimation.new(
            self.dot, 0, 380, 900,
            Adw.CallbackAnimationTarget.new(self.on_slide),
        )
        self.slide.set_easing(Adw.Easing.EASE_IN_OUT_CUBIC)

        # -- a timed animation driving a property ------------------------------
        #
        # A property target needs no callback at all: name the property and the
        # animation writes to it every frame.
        self.fade = Adw.TimedAnimation.new(
            self.dot, 1.0, 0.15, 600,
            Adw.PropertyAnimationTarget.new(self.dot, "opacity"),
        )
        self.fade.set_easing(Adw.Easing.EASE_IN_OUT_CUBIC)
        # Alternate + repeat 2 gives a fade out and back in from one animation.
        self.fade.set_alternate(True)
        self.fade.set_repeat_count(2)

        # -- a spring ----------------------------------------------------------
        #
        # damping ratio, mass, stiffness. Under 1 overshoots and wobbles; 1 is
        # critically damped, arriving as fast as it can without overshooting.
        self.spring = Adw.SpringAnimation.new(
            self.dot, 0, 380,
            Adw.SpringParams.new(0.6, 1, 180),
            Adw.CallbackAnimationTarget.new(self.on_slide),
        )

        easing = Gtk.DropDown.new_from_strings([name for name, _ in EASINGS])
        easing.connect(
            "notify::selected",
            lambda d, _p: self.slide.set_easing(EASINGS[d.get_selected()][1]),
        )

        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        for label, animation in (
            ("Slide", self.slide), ("Fade", self.fade), ("Spring", self.spring)
        ):
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_play, animation)
            buttons.append(button)

        self.status = Gtk.Label(label="")
        self.slide.connect("done", lambda _a: self.status.set_text("slide finished"))
        self.spring.connect("done", lambda _a: self.status.set_text("spring settled"))

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.append(track)
        box.append(easing)
        box.append(buttons)
        box.append(self.status)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar())
        toolbar.set_content(box)
        self.set_content(toolbar)

    def on_slide(self, value):
        self.dot.set_margin_start(int(value))

    def on_play(self, _button, animation):
        # Playing an animation that is already running restarts it; reset() puts
        # it back to the start without playing.
        self.dot.set_margin_start(0)
        self.dot.set_opacity(1.0)
        animation.play()


def on_activate(app):
    Window(application=app).present()


app = Adw.Application(application_id="com.example.Animations")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
