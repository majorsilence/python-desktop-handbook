#!/usr/bin/env python3
"""AdwDialog and AdwAlertDialog: dialogs that adapt instead of floating.

GtkAlertDialog (in dialogs.py) is the plain GTK answer and is still correct.
libadwaita 1.5 added its own, and in a libadwaita application they are the ones
to reach for, because of what they do at phone width: instead of opening a
separate floating window, they slide up from the bottom as a sheet inside the
parent window. Same code, both shapes, decided by the available space.

Responses here are *strings*, not indices into a button list. That is the other
difference worth noticing: "delete" stays "delete" when someone inserts a button
before it.
"""

import sys

from collections.abc import Callable
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, Gtk


def ask_to_delete(parent: Gtk.Widget, label: Gtk.Label) -> None:
    dialog = Adw.AlertDialog(heading="Delete this file?",
                             body="Once it is gone it is gone. There is no undo.")
    dialog.add_response("cancel", "Cancel")
    dialog.add_response("delete", "Delete")

    # Destructive paints the button red; suggested paints it as the accent
    # colour. Marking the dangerous one is not decoration -- it is how the user
    # tells the two apart at a glance.
    dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
    dialog.set_default_response("cancel")   # chosen by Enter
    dialog.set_close_response("cancel")     # chosen by Escape, or by dismissal

    dialog.choose(parent, None, on_choice, label)


def on_choice(dialog: Adw.AlertDialog, result: Gio.AsyncResult, label: Gtk.Label) -> None:
    # Unlike Gtk.AlertDialog.choose_finish(), this does not raise when the
    # dialog is dismissed: dismissal returns the close response, which you
    # already named. There is no error case to forget about.
    response = dialog.choose_finish(result)
    label.set_text({"delete": "Deleted", "cancel": "Cancelled"}[response])


class RenameDialog(Adw.Dialog):
    """A dialog with your own content in it, rather than a message and buttons.

    Subclassing AdwDialog is the general case: set a title, set a child, and
    present it against a widget. Everything about how it is displayed -- floating
    window or bottom sheet -- is libadwaita's decision, not yours.
    """

    def __init__(self, on_renamed: Callable[[str], None]) -> None:
        super().__init__()
        self.on_renamed = on_renamed
        self.set_title("Rename")
        self.set_content_width(360)

        self.entry = Adw.EntryRow(title="New name")

        group = Adw.PreferencesGroup()
        group.add(self.entry)
        group.set_margin_top(12)
        group.set_margin_bottom(12)
        group.set_margin_start(12)
        group.set_margin_end(12)

        cancel = Gtk.Button(label="Cancel")
        cancel.connect("clicked", lambda _b: self.close())

        rename = Gtk.Button(label="Rename")
        rename.add_css_class("suggested-action")
        rename.connect("clicked", self.on_rename)

        header = Adw.HeaderBar(show_end_title_buttons=False)
        header.pack_start(cancel)
        header.pack_end(rename)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(header)
        toolbar.set_content(group)
        self.set_child(toolbar)

    def on_rename(self, _button: Gtk.Button) -> None:
        self.on_renamed(self.entry.get_text() or "(nothing)")
        self.close()


class Window(Adw.ApplicationWindow):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.set_title("Adwaita Dialogs")
        self.set_default_size(420, 220)

        self.label = Gtk.Label(label="No answer yet")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        delete = Gtk.Button(label="Delete something")
        delete.connect("clicked", lambda _b: ask_to_delete(self, self.label))

        rename = Gtk.Button(label="Rename something")
        rename.connect("clicked", self.on_rename_clicked)

        box.append(delete)
        box.append(rename)
        box.append(self.label)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar())
        toolbar.set_content(box)
        self.set_content(toolbar)

    def on_rename_clicked(self, _button: Gtk.Button) -> None:
        # present() takes any widget, not just a window: libadwaita walks up to
        # find the right place to put the dialog.
        RenameDialog(lambda name: self.label.set_text(f"Renamed to {name}")).present(self)


def on_activate(app: Adw.Application) -> None:
    Window(application=app).present()


app = Adw.Application(application_id="com.example.AdwDialogs")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
