#!/usr/bin/env python3
"""A list of objects in a GtkListView.

GtkTreeView and GtkListStore are deprecated in GTK 4.  Their replacement splits
the job three ways: a list model holds the data, a factory builds and fills the
rows, and a selection model tracks what is selected.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GObject, Gtk


class Task(GObject.Object):
    """One row's worth of data. List models hold GObjects, not tuples."""

    __gtype_name__ = "Task"

    title = GObject.Property(type=str, default="")
    done = GObject.Property(type=bool, default=False)

    def __init__(self, title, done=False):
        super().__init__(title=title, done=done)


def on_setup(_factory, list_item):
    """Build an empty row. Called once per row widget, then reused."""
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    box.append(Gtk.CheckButton())
    box.append(Gtk.Label(xalign=0))
    list_item.set_child(box)


def on_bind(_factory, list_item):
    """Point an existing row at an item. Called every time a row is recycled."""
    task = list_item.get_item()
    box = list_item.get_child()
    check, label = box.get_first_child(), box.get_last_child()

    label.set_text(task.title)
    check.set_active(task.done)

    # Keep the binding so it can be undone when the row is recycled.
    list_item.binding = check.bind_property(
        "active", task, "done", GObject.BindingFlags.BIDIRECTIONAL
    )


def on_unbind(_factory, list_item):
    binding = getattr(list_item, "binding", None)
    if binding is not None:
        binding.unbind()
        list_item.binding = None


def on_activate(app):
    window = Gtk.ApplicationWindow(application=app, title="List View")
    window.set_default_size(360, 320)

    store = Gio.ListStore(item_type=Task)
    for title in ("Buy milk", "Write chapter two", "Walk the dog", "Rewrite chapter two"):
        store.append(Task(title))

    factory = Gtk.SignalListItemFactory()
    factory.connect("setup", on_setup)
    factory.connect("bind", on_bind)
    factory.connect("unbind", on_unbind)

    selection = Gtk.SingleSelection(model=store)
    selection.connect(
        "notify::selected",
        lambda s, _p: print("selected:", s.get_selected_item().title),
    )

    view = Gtk.ListView(model=selection, factory=factory)

    scroller = Gtk.ScrolledWindow(vexpand=True)
    scroller.set_child(view)
    window.set_child(scroller)
    window.present()


app = Gtk.Application(application_id="com.example.ListView")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
