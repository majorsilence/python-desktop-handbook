#!/usr/bin/env python3
"""Watching the bus without a proxy.

A proxy is for one object you use often. When you want to hear about something
happening anywhere -- a name appearing, a signal from a program that may not be
running yet -- subscribe on the connection instead.
"""

import sys

import gi

from gi.repository import Gio, GLib

RUN_FOR_SECONDS = 3


def on_name_owner_changed(_connection, _sender, _path, _interface, _signal,
                          parameters):
    name, old_owner, new_owner = parameters.unpack()
    if name.startswith(":"):
        return                              # unique names, too noisy to report
    if new_owner and not old_owner:
        print(f"appeared:   {name}")
    elif old_owner and not new_owner:
        print(f"went away:  {name}")
    else:
        print(f"changed:    {name}")


def on_appeared(_connection, name, owner):
    print(f"watch: {name} is owned by {owner}")


def on_vanished(_connection, name):
    print(f"watch: {name} is gone")


connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)

# The general form. Any of the filters may be None, meaning "do not care".
subscription = connection.signal_subscribe(
    None,                                   # sender
    "org.freedesktop.DBus",                 # interface
    "NameOwnerChanged",                     # signal
    "/org/freedesktop/DBus",                # path
    None,                                   # first argument must equal this
    Gio.DBusSignalFlags.NONE,
    on_name_owner_changed,
)

# For the common case of "tell me when this service comes and goes", there is a
# helper that handles the fact that it may already be running.
watch = Gio.bus_watch_name(
    Gio.BusType.SESSION,
    "com.example.Counter",
    Gio.BusNameWatcherFlags.NONE,
    on_appeared,
    on_vanished,
)

print(f"watching the session bus for {RUN_FOR_SECONDS} seconds…")

loop = GLib.MainLoop()
GLib.timeout_add_seconds(RUN_FOR_SECONDS, loop.quit)
try:
    loop.run()
finally:
    connection.signal_unsubscribe(subscription)
    Gio.bus_unwatch_name(watch)

sys.exit(0)
