#!/usr/bin/env python3
"""Storing preferences with GSettings.

GConf is gone. GSettings replaced it: a schema declares the keys, their types and
their defaults, and the values are stored by whatever backend the system uses
(dconf on a normal desktop, a keyfile inside a Flatpak).

The schema has to be compiled before it can be used. Installed programs put the
.gschema.xml in /usr/share/glib-2.0/schemas and run glib-compile-schemas there;
this example compiles into a temporary directory and loads it from disk, so it
runs from a checkout without installing anything.
"""

import pathlib
import subprocess
import sys
import tempfile
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GLib, Gtk

SCHEMA_ID = "com.example.Settings"
HERE = pathlib.Path(__file__).parent


def load_settings() -> Gio.Settings:
    """The installed path first; a locally compiled schema as a fallback."""
    source = Gio.SettingsSchemaSource.get_default()
    if source is not None and source.lookup(SCHEMA_ID, True) is not None:
        return Gio.Settings.new(SCHEMA_ID)

    compiled = pathlib.Path(tempfile.mkdtemp(prefix="schemas-"))
    (compiled / f"{SCHEMA_ID}.gschema.xml").write_bytes(
        (HERE / f"{SCHEMA_ID}.gschema.xml").read_bytes()
    )
    subprocess.run(["glib-compile-schemas", str(compiled)], check=True)

    source = Gio.SettingsSchemaSource.new_from_directory(
        str(compiled), Gio.SettingsSchemaSource.get_default(), False
    )
    schema = source.lookup(SCHEMA_ID, False)
    if schema is None:
        raise SystemExit(f"could not load the {SCHEMA_ID} schema")
    return Gio.Settings.new_full(schema, None, None)


class Window(Gtk.ApplicationWindow):
    def __init__(self, settings, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.settings = settings
        self.set_title("Settings")

        # A tuple key comes back as a GVariant-shaped Python tuple.
        width, height = settings.get_value("window-size").unpack()
        self.set_default_size(width, height)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        entry = Gtk.Entry()
        switch = Gtk.Switch(halign=Gtk.Align.START)
        spin = Gtk.SpinButton.new_with_range(1, 10, 1)

        # bind() keeps a widget property and a key in step, in both directions,
        # with no callbacks and no code to write the value back.
        settings.bind("greeting", entry, "text", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("enabled", switch, "active", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("repeat", spin, "value", Gio.SettingsBindFlags.DEFAULT)

        # A key can also drive another widget's sensitivity.
        settings.bind("enabled", entry, "sensitive", Gio.SettingsBindFlags.GET)
        settings.bind("enabled", spin, "sensitive", Gio.SettingsBindFlags.GET)

        self.preview = Gtk.Label(wrap=True)
        self.update_preview()

        # For anything that is not a widget property, watch the key.
        settings.connect("changed", lambda *_: self.update_preview())

        for label, widget in (
            ("Greeting", entry), ("Enabled", switch), ("Repeat", spin)
        ):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row.append(Gtk.Label(label=label, xalign=0, width_chars=8))
            row.append(widget)
            box.append(row)

        reset = Gtk.Button(label="Reset to defaults")
        reset.connect("clicked", self.on_reset)
        box.append(reset)
        box.append(self.preview)

        self.set_child(box)
        self.connect("close-request", self.on_close)

    def update_preview(self) -> None:
        if not self.settings.get_boolean("enabled"):
            self.preview.set_text("(disabled)")
            return
        greeting = self.settings.get_string("greeting")
        repeat = self.settings.get_int("repeat")
        self.preview.set_text(" ".join([greeting] * repeat))

    def on_reset(self, _button: Gtk.Button) -> None:
        for key in ("greeting", "enabled", "repeat"):
            self.settings.reset(key)

    def on_close(self, _window: Gtk.Window) -> bool:
        # Store the size as the tuple the schema declared.
        self.settings.set_value(
            "window-size",
            GLib.Variant("(ii)", (self.get_width(), self.get_height())),
        )
        return False


def on_activate(app: Gtk.Application) -> None:
    Window(load_settings(), application=app).present()


app = Gtk.Application(application_id=SCHEMA_ID)
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
