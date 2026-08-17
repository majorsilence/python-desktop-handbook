#!/usr/bin/env python3
"""Storing a password with libsecret.

gnome-keyring's own API is gone; libsecret is what talks to it now, and to any
other Secret Service provider (KWallet, KeePassXC with the right plugin).

Never put a password in GSettings. GSettings values are world-readable within the
user's session, are synced by some setups, and end up in backups in the clear.
"""

import sys
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Secret", "1")
from gi.repository import Gio, GLib, GObject, Gtk, Secret

# A schema names the attributes a secret is looked up by. It is not a security
# boundary -- it is how you find the item again.
SCHEMA = Secret.Schema.new(
    "com.example.Passwords",
    Secret.SchemaFlags.NONE,
    {
        "service": Secret.SchemaAttributeType.STRING,
        "username": Secret.SchemaAttributeType.STRING,
    },
)


def attributes(username: str) -> dict[str, str]:
    return {"service": "com.example.Passwords", "username": username}


class Window(Gtk.ApplicationWindow):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.set_title("Passwords")
        self.set_default_size(380, 220)

        self.username = Gtk.Entry(placeholder_text="Username", text="alice")
        self.password = Gtk.PasswordEntry(show_peek_icon=True)
        self.status = Gtk.Label(wrap=True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.append(self.username)
        box.append(self.password)

        for label, handler in (
            ("Store", self.on_store),
            ("Look up", self.on_lookup),
            ("Forget", self.on_clear),
        ):
            button = Gtk.Button(label=label)
            button.connect("clicked", handler)
            box.append(button)

        box.append(self.status)
        self.set_child(box)

    # Every call has a synchronous and an asynchronous form. The keyring may be
    # locked, in which case the desktop prompts the user -- so use the async one.
    def on_store(self, _button: Gtk.Button) -> None:
        Secret.password_store(
            SCHEMA,
            attributes(self.username.get_text()),
            Secret.COLLECTION_DEFAULT,
            f"Example password for {self.username.get_text()}",
            self.password.get_text(),
            None,
            self.on_stored,
        )

    def on_stored(self, _source: GObject.Object, result: Gio.AsyncResult) -> None:
        try:
            Secret.password_store_finish(result)
            self.status.set_text("Stored in the keyring.")
        except GLib.Error as error:
            self.status.set_text(f"Could not store it: {error.message}")

    def on_lookup(self, _button: Gtk.Button) -> None:
        Secret.password_lookup(
            SCHEMA, attributes(self.username.get_text()), None, self.on_looked_up
        )

    def on_looked_up(self, _source: GObject.Object, result: Gio.AsyncResult) -> None:
        try:
            password = Secret.password_lookup_finish(result)
        except GLib.Error as error:
            self.status.set_text(f"Could not read it: {error.message}")
            return
        if password is None:
            self.status.set_text("Nothing stored for that username.")
        else:
            self.password.set_text(password)
            self.status.set_text(f"Found a password of {len(password)} characters.")

    def on_clear(self, _button: Gtk.Button) -> None:
        Secret.password_clear(
            SCHEMA, attributes(self.username.get_text()), None, self.on_cleared
        )

    def on_cleared(self, _source: GObject.Object, result: Gio.AsyncResult) -> None:
        try:
            removed = Secret.password_clear_finish(result)
        except GLib.Error as error:
            self.status.set_text(f"Could not remove it: {error.message}")
            return
        self.status.set_text("Removed." if removed else "There was nothing to remove.")


def on_activate(app: Gtk.Application) -> None:
    Window(application=app).present()


app = Gtk.Application(application_id="com.example.Passwords")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
