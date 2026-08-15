#!/usr/bin/env python3
"""The animations you get without writing any.

Most motion in a GTK application is not hand-animated. Containers animate their
own changes: a stack crossfades between pages, a revealer slides its child in, a
flap or a navigation view moves between views. Setting a transition type and a
duration is the whole of it.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GObject, Gtk

TRANSITIONS = [
    ("Crossfade", Gtk.StackTransitionType.CROSSFADE),
    ("Slide left/right", Gtk.StackTransitionType.SLIDE_LEFT_RIGHT),
    ("Slide up/down", Gtk.StackTransitionType.SLIDE_UP_DOWN),
    ("Over up", Gtk.StackTransitionType.OVER_UP),
    ("Rotate left/right", Gtk.StackTransitionType.ROTATE_LEFT_RIGHT),
]


def page(text, colour_class):
    label = Gtk.Label(label=text)
    label.add_css_class(colour_class)
    label.set_vexpand(True)
    frame = Gtk.Frame(child=label)
    return frame


class Window(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Transitions")
        self.set_default_size(520, 380)

        # -- a stack: one child visible at a time, animated between -------------
        self.stack = Gtk.Stack()
        self.stack.set_transition_duration(400)
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.add_titled(page("First page", "title-1"), "one", "One")
        self.stack.add_titled(page("Second page", "title-2"), "two", "Two")
        self.stack.add_titled(page("Third page", "title-3"), "three", "Three")

        switcher = Gtk.StackSwitcher(stack=self.stack)
        switcher.set_halign(Gtk.Align.CENTER)

        transition = Gtk.DropDown.new_from_strings([name for name, _ in TRANSITIONS])
        transition.connect(
            "notify::selected",
            lambda d, _p: self.stack.set_transition_type(TRANSITIONS[d.get_selected()][1]),
        )

        # -- a revealer: show and hide one child, animated ----------------------
        self.revealer = Gtk.Revealer()
        self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.revealer.set_transition_duration(300)
        self.revealer.set_child(
            Gtk.Label(label="A revealer slides its child in and out.",
                      margin_top=12, margin_bottom=12)
        )

        toggle = Gtk.ToggleButton(label="Show the extra bit")
        # The revealer's own property is the state, so bind rather than handle.
        toggle.bind_property("active", self.revealer, "reveal-child",
                             GObject.BindingFlags.SYNC_CREATE)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.append(switcher)
        box.append(transition)
        box.append(self.stack)
        box.append(toggle)
        box.append(self.revealer)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar())
        toolbar.set_content(box)
        self.set_content(toolbar)


def on_activate(app):
    Window(application=app).present()


app = Adw.Application(application_id="com.example.Transitions")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
