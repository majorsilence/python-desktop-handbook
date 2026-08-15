#!/usr/bin/env python3
"""Talking to the service in export-a-service.py.

A GDBusProxy is the comfortable way to use a remote object: it caches the
properties, gives you a signal for the remote signals, and turns a method call
into one line. Start export-a-service.py first.
"""

import sys

import gi

from gi.repository import Gio, GLib

NAME = "com.example.Counter"
PATH = "/com/example/Counter"


def on_signal(_proxy, _sender, signal, parameters):
    print(f"signal {signal}{parameters.unpack()}")


def on_properties_changed(proxy, changed, invalidated):
    for key in changed.keys():
        print(f"property {key} is now {proxy.get_cached_property(key).unpack()}")
    for key in invalidated:
        print(f"property {key} changed, value not sent")


def main():
    try:
        proxy = Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SESSION,
            Gio.DBusProxyFlags.NONE,
            None,               # introspection data; None means fetch it
            NAME, PATH, NAME,
            None,
        )
    except GLib.Error as error:
        print(f"could not reach {NAME}: {error.message}")
        return 1

    # A proxy is created even when nobody owns the name -- it is a placeholder
    # waiting for the service to appear. This is how you tell.
    if proxy.get_name_owner() is None:
        print(f"{NAME} is not running. Start export-a-service.py first.")
        return 0

    proxy.connect("g-signal", on_signal)
    proxy.connect("g-properties-changed", on_properties_changed)

    # Method calls are ordinary calls on the proxy: the name, then the argument
    # signature, then the arguments.
    print("Increment(3) ->", proxy.Increment("(i)", 3))
    print("Increment(4) ->", proxy.Increment("(i)", 4))
    print("Describe()   ->", proxy.Describe())

    # Cached properties cost nothing to read; they arrived with the proxy.
    print("Value        =", proxy.get_cached_property("Value").unpack())

    # Setting a property is a call on the standard Properties interface.
    proxy.call_sync(
        "org.freedesktop.DBus.Properties.Set",
        GLib.Variant("(ssv)", (NAME, "Label", GLib.Variant("s", "tally"))),
        Gio.DBusCallFlags.NONE, -1, None,
    )
    print("Describe()   ->", proxy.Describe())

    # An asynchronous call, which is what a program with a window should use:
    # a synchronous one blocks the interface until the reply arrives.
    loop = GLib.MainLoop()

    def on_reset(proxy, result, _data=None):
        try:
            proxy.call_finish(result)
            print("Reset()      -> done")
        except GLib.Error as error:
            print(f"Reset failed: {error.message}")
        loop.quit()

    proxy.call("Reset", None, Gio.DBusCallFlags.NONE, -1, None, on_reset)
    GLib.timeout_add_seconds(5, loop.quit)
    loop.run()

    return 0


sys.exit(main())
