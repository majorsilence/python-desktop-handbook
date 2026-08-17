#!/usr/bin/env python3
"""Toggle buttons, check buttons, radio groups and switches.

GTK 4 has no GtkRadioButton.  A radio group is several GtkCheckButtons joined
with set_group(); a check button that belongs to a group draws as a radio.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject, Gtk


def on_toggled(button: Gtk.Button) -> None:
    print(f"{button.get_label()} is now {button.get_active()}")


def on_switch_active(switch: Gtk.Switch, _pspec: GObject.ParamSpec) -> None:
    print(f"switch is now {switch.get_active()}")


def on_activate(app: Gtk.Application) -> None:
    window = Gtk.ApplicationWindow(application=app, title="Toggles")
    window.set_default_size(320, 300)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    toggle = Gtk.ToggleButton(label="Toggle me")
    toggle.connect("toggled", on_toggled)
    box.append(toggle)

    check = Gtk.CheckButton(label="Check me")
    check.connect("toggled", on_toggled)
    box.append(check)

    # Joining check buttons into a group turns them into radio buttons.
    first = None
    for name in ("Small", "Medium", "Large"):
        option = Gtk.CheckButton(label=name)
        if first is None:
            first = option
            option.set_active(True)
        else:
            option.set_group(first)
        option.connect("toggled", on_toggled)
        box.append(option)

    # A switch reports its state through the "active" property, not "toggled".
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    row.append(Gtk.Label(label="Enabled"))
    switch = Gtk.Switch()
    switch.set_halign(Gtk.Align.START)
    switch.connect("notify::active", on_switch_active)
    row.append(switch)
    box.append(row)

    window.set_child(box)
    window.present()


app = Gtk.Application(application_id="com.example.Toggles")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
