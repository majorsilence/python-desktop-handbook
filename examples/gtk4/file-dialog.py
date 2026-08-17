#!/usr/bin/env python3
"""Opening and saving files with GtkFileDialog.

GtkFileChooserDialog is deprecated.  GtkFileDialog replaces it, is asynchronous
like GtkAlertDialog, and under Flatpak is answered by the desktop's file portal
rather than by a widget in your process.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GLib, Gtk


def text_filters() -> Gio.ListStore:
    """A dialog's filters are a list model of GtkFileFilter."""
    filters = Gio.ListStore(item_type=Gtk.FileFilter)

    text = Gtk.FileFilter()
    text.set_name("Text files")
    text.add_mime_type("text/plain")
    text.add_suffix("txt")
    filters.append(text)

    everything = Gtk.FileFilter()
    everything.set_name("All files")
    everything.add_pattern("*")
    filters.append(everything)

    return filters


def open_file(window: Gtk.Window, label: Gtk.Label) -> None:
    dialog = Gtk.FileDialog(title="Open a file")
    dialog.set_filters(text_filters())
    dialog.open(window, None, on_opened, label)


def on_opened(dialog: Gtk.FileDialog, result: Gio.AsyncResult,
              label: Gtk.Label) -> None:
    try:
        file = dialog.open_finish(result)
    except GLib.Error:
        label.set_text("Open cancelled")
        return

    # You get a GFile, not a path. It might not be a local file at all.
    try:
        ok, contents, _etag = file.load_contents(None)
    except GLib.Error as error:
        label.set_text(f"Could not read it: {error.message}")
        return

    text = contents.decode("utf-8", "replace") if ok else ""
    label.set_text(f"{file.get_basename()}: {len(text)} characters")


def save_file(window: Gtk.Window, label: Gtk.Label) -> None:
    dialog = Gtk.FileDialog(title="Save as")
    dialog.set_initial_name("untitled.txt")
    dialog.set_filters(text_filters())
    dialog.save(window, None, on_saved, label)


def on_saved(dialog: Gtk.FileDialog, result: Gio.AsyncResult,
             label: Gtk.Label) -> None:
    try:
        file = dialog.save_finish(result)
    except GLib.Error:
        label.set_text("Save cancelled")
        return

    try:
        file.replace_contents(
            b"Written by the file dialog example.\n",
            None, False, Gio.FileCreateFlags.NONE, None,
        )
    except GLib.Error as error:
        label.set_text(f"Could not write it: {error.message}")
        return

    label.set_text(f"Wrote {file.get_path()}")


def choose_folder(window: Gtk.Window, label: Gtk.Label) -> None:
    dialog = Gtk.FileDialog(title="Choose a folder")
    dialog.select_folder(window, None, on_folder_chosen, label)


def on_folder_chosen(dialog: Gtk.FileDialog, result: Gio.AsyncResult,
                     label: Gtk.Label) -> None:
    try:
        folder = dialog.select_folder_finish(result)
    except GLib.Error:
        label.set_text("Folder choice cancelled")
        return
    label.set_text(f"Chose {folder.get_path()}")


def on_activate(app: Gtk.Application) -> None:
    window = Gtk.ApplicationWindow(application=app, title="File Dialog")
    window.set_default_size(420, 160)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    label = Gtk.Label(label="Nothing chosen yet", wrap=True)

    for text, handler in (
        ("Open a file", open_file),
        ("Save a file", save_file),
        ("Choose a folder", choose_folder),
    ):
        button = Gtk.Button(label=text)
        button.connect("clicked", lambda _b, fn=handler: fn(window, label))
        box.append(button)

    box.append(label)
    window.set_child(box)
    window.present()


app = Gtk.Application(application_id="com.example.FileDialog")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
