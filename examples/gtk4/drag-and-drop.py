#!/usr/bin/env python3
"""Drag and drop with event controllers.

GTK 4 has no drag-and-drop signals on widgets.  You add a GtkDragSource to
whatever can be dragged and a GtkDropTarget to whatever can receive, and both
talk in GValues rather than in GTK-specific selection data.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GObject, Gtk


def make_source(text):
    """A label that can be dragged, offering its text as a string."""
    label = Gtk.Label(label=text)
    label.add_css_class("card")
    label.set_size_request(120, 48)

    def on_prepare(_source, _x, _y):
        # What is being dragged, as a GValue. Return None to refuse the drag.
        value = GObject.Value(str, text)
        return Gdk.ContentProvider.new_for_value(value)

    def on_drag_begin(source, _drag):
        # An icon to drag around; without one the pointer drags nothing visible.
        icon = Gtk.WidgetPaintable.new(label)
        source.set_icon(icon, 0, 0)

    source = Gtk.DragSource(actions=Gdk.DragAction.COPY)
    source.connect("prepare", on_prepare)
    source.connect("drag-begin", on_drag_begin)
    label.add_controller(source)
    return label


def make_target(on_text):
    """A frame that accepts dropped strings."""
    label = Gtk.Label(label="Drop here")
    frame = Gtk.Frame(child=label)
    frame.set_size_request(200, 120)

    def on_drop(_target, value, _x, _y):
        on_text(value)
        label.set_text(f"Got: {value}")
        return True          # True accepts the drop, False rejects it

    def on_enter(_target, _x, _y):
        frame.add_css_class("accent")
        return Gdk.DragAction.COPY

    def on_leave(_target):
        frame.remove_css_class("accent")

    target = Gtk.DropTarget.new(GObject.TYPE_STRING, Gdk.DragAction.COPY)
    target.connect("drop", on_drop)
    target.connect("enter", on_enter)
    target.connect("leave", on_leave)
    frame.add_controller(target)
    return frame


def on_activate(app):
    window = Gtk.ApplicationWindow(application=app, title="Drag and Drop")
    window.set_default_size(460, 220)

    sources = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    for text in ("Vanilla", "Chocolate", "Strawberry"):
        sources.append(make_source(text))

    layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
    layout.set_margin_top(12)
    layout.set_margin_bottom(12)
    layout.set_margin_start(12)
    layout.set_margin_end(12)
    layout.append(sources)
    layout.append(make_target(lambda text: print("dropped:", text)))

    window.set_child(layout)
    window.present()


app = Gtk.Application(application_id="com.example.DragAndDrop")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
