#!/usr/bin/env python3
"""Putting your own object on the bus.

Being a D-Bus service means three things: owning a well-known name, exporting an
object at a path, and answering the methods your interface declares. The
interface is described in XML -- the same XML that comes back from Introspect,
which is how other programs and the command-line tools discover you.

Run this, then run call-our-service.py in another terminal.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GLib

NAME = "com.example.Counter"
PATH = "/com/example/Counter"

INTERFACE_XML = """
<node>
  <interface name="com.example.Counter">

    <method name="Increment">
      <arg type="i" name="by" direction="in"/>
      <arg type="i" name="value" direction="out"/>
    </method>

    <method name="Reset"/>

    <method name="Describe">
      <arg type="s" name="text" direction="out"/>
    </method>

    <signal name="Changed">
      <arg type="i" name="value"/>
    </signal>

    <property name="Value" type="i" access="read"/>
    <property name="Label" type="s" access="readwrite"/>

  </interface>
</node>
"""


class Counter:
    def __init__(self, connection: Gio.DBusConnection) -> None:
        self.connection = connection
        self.value = 0
        self.label = "counter"

    # -- the method call handler ------------------------------------------------
    #
    # One callback for every method on the interface. Parameters arrive as a
    # GVariant tuple; the reply has to be a GVariant tuple too, or None for a
    # method that returns nothing.

    def on_method_call(self, _connection: Gio.DBusConnection, _sender: str,
                       _path: str, _interface: str, method: str,
                       parameters: GLib.Variant,
                       invocation: Gio.DBusMethodInvocation) -> None:
        if method == "Increment":
            (by,) = parameters.unpack()
            self.value += by
            self.emit_changed()
            invocation.return_value(GLib.Variant("(i)", (self.value,)))

        elif method == "Reset":
            self.value = 0
            self.emit_changed()
            invocation.return_value(None)

        elif method == "Describe":
            text = f"{self.label} is at {self.value}"
            invocation.return_value(GLib.Variant("(s)", (text,)))

        else:
            # Always answer. A caller that gets no reply waits for its timeout,
            # which is 25 seconds by default.
            invocation.return_error_literal(
                Gio.dbus_error_quark(),
                Gio.DBusError.UNKNOWN_METHOD,
                f"no such method: {method}",
            )

    # -- properties -------------------------------------------------------------

    def on_get_property(self, _connection: Gio.DBusConnection, _sender: str,
                        _path: str, _interface: str,
                        prop: str) -> GLib.Variant | None:
        if prop == "Value":
            return GLib.Variant("i", self.value)
        if prop == "Label":
            return GLib.Variant("s", self.label)
        return None

    def on_set_property(self, _connection: Gio.DBusConnection, _sender: str,
                        path: str, interface: str, prop: str,
                        value: GLib.Variant) -> bool:
        if prop != "Label":
            return False
        self.label = value.get_string()

        # Changing a property does not announce itself; you emit the standard
        # PropertiesChanged signal by hand.
        self.connection.emit_signal(
            None, path, "org.freedesktop.DBus.Properties", "PropertiesChanged",
            GLib.Variant("(sa{sv}as)",
                         (interface, {"Label": GLib.Variant("s", self.label)}, [])),
        )
        return True

    def emit_changed(self) -> None:
        self.connection.emit_signal(
            None, PATH, NAME, "Changed", GLib.Variant("(i)", (self.value,))
        )
        # Value is a property as well as a signal argument, and a proxy caches
        # properties. Without this, every client keeps reporting the value the
        # property had when it connected.
        self.connection.emit_signal(
            None, PATH, "org.freedesktop.DBus.Properties", "PropertiesChanged",
            GLib.Variant("(sa{sv}as)",
                         (NAME, {"Value": GLib.Variant("i", self.value)}, [])),
        )


def on_startup(app: Gio.Application) -> None:
    connection = app.get_dbus_connection()
    if connection is None:
        raise SystemExit("no session bus; run this under dbus-run-session")

    counter = Counter(connection)
    node = Gio.DBusNodeInfo.new_for_xml(INTERFACE_XML)

    connection.register_object(
        PATH,
        node.interfaces[0],
        counter.on_method_call,
        counter.on_get_property,
        counter.on_set_property,
    )
    print(f"exported {NAME} at {PATH}")


# Gio.Application owns the well-known name for us: the application id *is* the
# bus name, and registering it is what claims it.
app = Gio.Application(application_id=NAME, flags=Gio.ApplicationFlags.IS_SERVICE)
app.set_inactivity_timeout(60_000)
app.connect("startup", on_startup)
app.connect("activate", lambda a: a.hold())
sys.exit(app.run(sys.argv))
