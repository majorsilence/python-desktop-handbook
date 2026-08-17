#!/usr/bin/env python3
"""Handing something to the rest of the desktop, and finding where files go.

Opening a URL used to mean shelling out to xdg-open. GTK 4.10 added launchers
that go through the portal when there is one, so they work inside a sandbox and
outside it without changing.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GLib, Gtk


def open_url(window: Gtk.Window, status: Gtk.Label) -> None:
    launcher = Gtk.UriLauncher(uri="https://gtk.org/")

    def done(launcher: Gtk.UriLauncher, result: Gio.AsyncResult,
             _data: object = None) -> None:
        try:
            launcher.launch_finish(result)
            status.set_text("Handed the URL to the desktop.")
        except GLib.Error as error:
            status.set_text(f"Could not open it: {error.message}")

    launcher.launch(window, None, done)


def show_in_files(window: Gtk.Window, status: Gtk.Label) -> None:
    """Open the user's Downloads folder in whatever file manager they use."""
    folder = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD)
    launcher = Gtk.FileLauncher(file=Gio.File.new_for_path(folder or GLib.get_home_dir()))

    def done(launcher: Gtk.FileLauncher, result: Gio.AsyncResult,
             _data: object = None) -> None:
        try:
            launcher.launch_finish(result)
            status.set_text("Opened the folder.")
        except GLib.Error as error:
            status.set_text(f"Could not open it: {error.message}")

    launcher.launch(window, None, done)


def describe_directories() -> str:
    """Where a well-behaved program puts its files.

    Never build these by joining "~" with ".myapp": the XDG variables move them,
    and a Flatpak redirects them into the sandbox.
    """
    return "\n".join(
        f"{name}: {value}"
        for name, value in (
            ("config", GLib.get_user_config_dir()),
            ("data", GLib.get_user_data_dir()),
            ("cache", GLib.get_user_cache_dir()),
            ("state", GLib.get_user_state_dir()),
            ("runtime", GLib.get_user_runtime_dir()),
            ("documents", GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS)),
        )
    )


def on_activate(app: Gtk.Application) -> None:
    window = Gtk.ApplicationWindow(application=app, title="Launch and locate")
    window.set_default_size(560, 360)

    status = Gtk.Label(wrap=True)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    for label, handler in (
        ("Open gtk.org", open_url),
        ("Show my Downloads folder", show_in_files),
    ):
        button = Gtk.Button(label=label)
        button.connect("clicked", lambda _b, fn=handler: fn(window, status))
        box.append(button)

    directories = Gtk.Label(label=describe_directories(), xalign=0, selectable=True)
    directories.add_css_class("monospace")
    box.append(directories)
    box.append(status)

    window.set_child(box)
    window.present()


app = Gtk.Application(application_id="com.example.LaunchAndLocate")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
