#!/usr/bin/env python3
"""Menus in GTK 4 are a GMenu model plus GAction implementations.

The model says what the menu looks like; the actions say what the items do.
Nothing in a menu item names a callback directly, which is why the same model
can drive a menu bar, a popover menu and a keyboard shortcut at once.
"""

import sys

from collections.abc import Callable
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, Gtk


def add_action(app: Gtk.Application, name: str,
               callback: Callable[..., None]) -> None:
    action = Gio.SimpleAction.new(name, None)
    action.connect("activate", callback)
    app.add_action(action)


def build_menu() -> Gio.Menu:
    menu = Gio.Menu()

    file_menu = Gio.Menu()
    file_menu.append("New", "app.new")
    file_menu.append("Open", "app.open")
    # A section draws a separator around its items.
    quit_section = Gio.Menu()
    quit_section.append("Quit", "app.quit")
    file_menu.append_section(None, quit_section)
    menu.append_submenu("File", file_menu)

    help_menu = Gio.Menu()
    help_menu.append("About", "app.about")
    menu.append_submenu("Help", help_menu)

    return menu


def on_startup(app: Gtk.Application) -> None:
    add_action(app, "new", lambda *_: print("New"))
    add_action(app, "open", lambda *_: print("Open"))
    add_action(app, "about", lambda *_: print("About"))
    add_action(app, "quit", lambda *_: app.quit())

    app.set_accels_for_action("app.new", ["<Control>n"])
    app.set_accels_for_action("app.quit", ["<Control>q"])

    # The menu bar has to be in place before any window is built.
    app.set_menubar(build_menu())


def on_activate(app: Gtk.Application) -> None:
    window = Gtk.ApplicationWindow(application=app, title="Menus")
    window.set_default_size(420, 200)
    window.set_show_menubar(True)

    # The same model again, this time as a popover on the header bar.
    header = Gtk.HeaderBar()
    header.pack_end(
        Gtk.MenuButton(icon_name="open-menu-symbolic", menu_model=app.get_menubar())
    )
    window.set_titlebar(header)

    window.set_child(Gtk.Label(label="Try the menu bar, the button, or Ctrl+Q."))
    window.present()


app = Gtk.Application(application_id="com.example.Menus")
app.connect("startup", on_startup)
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
