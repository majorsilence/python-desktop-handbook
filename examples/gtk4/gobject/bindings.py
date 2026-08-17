#!/usr/bin/env python3
"""Bindings: keeping two properties in step without writing a handler.

bind_property() is the most under-used thing in GObject. Any time you would
write "when this changes, set that", a binding is shorter, cannot get the two out
of sync, and cleans itself up when either object dies.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject, Gtk


class Settings(GObject.Object):
    __gtype_name__ = "BindingSettings"

    enabled = GObject.Property(type=bool, default=True)
    volume = GObject.Property(type=float, default=0.5, minimum=0.0, maximum=1.0)
    label = GObject.Property(type=str, default="")


def on_activate(app: Gtk.Application) -> None:
    window = Gtk.ApplicationWindow(application=app, title="Bindings")
    window.set_default_size(420, 340)

    settings = Settings()

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    switch = Gtk.Switch(halign=Gtk.Align.START)
    scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 0.01)
    entry = Gtk.Entry(placeholder_text="Type here")
    echo = Gtk.Label(xalign=0)
    percent = Gtk.Label(xalign=0)

    # SYNC_CREATE copies the current value across immediately. Without it the
    # target keeps whatever it had until the source next changes, which is the
    # usual cause of "my binding does not work" on the first frame.
    switch.bind_property("active", settings, "enabled",
                         GObject.BindingFlags.SYNC_CREATE
                         | GObject.BindingFlags.BIDIRECTIONAL)

    # One property can drive several targets.
    settings.bind_property("enabled", scale, "sensitive",
                           GObject.BindingFlags.SYNC_CREATE)
    settings.bind_property("enabled", entry, "sensitive",
                           GObject.BindingFlags.SYNC_CREATE)

    # Not everything with a get_value() has a "value" *property*. A GtkScale keeps
    # its value in its GtkAdjustment, so that is what the binding attaches to;
    # scale.bind_property("value", ...) fails with "cannot create binding".
    scale.get_adjustment().bind_property("value", settings, "volume",
                                         GObject.BindingFlags.SYNC_CREATE
                                         | GObject.BindingFlags.BIDIRECTIONAL)

    entry.bind_property("text", settings, "label",
                        GObject.BindingFlags.SYNC_CREATE
                        | GObject.BindingFlags.BIDIRECTIONAL)
    settings.bind_property("label", echo, "label",
                           GObject.BindingFlags.SYNC_CREATE)

    # When the two properties are not the same type or the same scale, supply a
    # transform. Returning False from it rejects the value and leaves the target
    # alone; returning (True, value) accepts it.
    def to_percent(_binding: GObject.Binding, value: float) -> tuple[bool, str]:
        return True, f"{value * 100:.0f}%"

    settings.bind_property("volume", percent, "label",
                           GObject.BindingFlags.SYNC_CREATE,
                           to_percent)

    # INVERT_BOOLEAN saves writing a transform for the commonest case of all.
    spinner = Gtk.Spinner()
    settings.bind_property("enabled", spinner, "spinning",
                           GObject.BindingFlags.SYNC_CREATE
                           | GObject.BindingFlags.INVERT_BOOLEAN)

    for widget in (switch, scale, percent, entry, echo, spinner):
        box.append(widget)

    # A binding is an object. Keep it if you need to take it apart early --
    # otherwise it lives as long as the two objects it joins.
    binding = settings.bind_property("label", window, "title",
                                     GObject.BindingFlags.SYNC_CREATE)
    print("binding:", binding.get_source_property(), "->",
          binding.get_target_property())
    binding.unbind()
    window.set_title("Bindings")

    window.set_child(box)
    window.present()


app = Gtk.Application(application_id="com.example.Bindings")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
