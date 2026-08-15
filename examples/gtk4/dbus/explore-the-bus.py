#!/usr/bin/env python3
"""Looking around the session bus from Python.

Before writing any D-Bus code it helps to see what is there. On the command line
that is `gdbus`, `busctl` or D-Spy; this does the same three things in Python.

  1. which names are on the bus
  2. what an object exposes, by introspecting it
  3. calling one of its methods
"""

import sys

import gi

from gi.repository import Gio, GLib

BUS = Gio.bus_get_sync(Gio.BusType.SESSION, None)


def list_names():
    """Every name on the bus. The ones starting with ':' are unique connection
    names; the rest are well-known names somebody has claimed."""
    reply = BUS.call_sync(
        "org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus",
        "ListNames", None,
        GLib.VariantType("(as)"),      # the reply signature you expect
        Gio.DBusCallFlags.NONE, -1, None,
    )
    # Replies are always a tuple, even when there is one value in it.
    (names,) = reply.unpack()
    return sorted(name for name in names if not name.startswith(":"))


def introspect(name, path):
    """Ask an object to describe itself. This is what the tools display."""
    try:
        reply = BUS.call_sync(
            name, path, "org.freedesktop.DBus.Introspectable", "Introspect", None,
            GLib.VariantType("(s)"), Gio.DBusCallFlags.NONE, 2000, None,
        )
    except GLib.Error as error:
        return f"  (could not introspect: {error.message})"

    (xml,) = reply.unpack()
    info = Gio.DBusNodeInfo.new_for_xml(xml)

    lines = []
    for interface in info.interfaces:
        lines.append(f"  interface {interface.name}")
        for method in interface.methods:
            args = ", ".join(f"{a.signature} {a.name}" for a in method.in_args)
            out = ", ".join(a.signature for a in method.out_args)
            lines.append(f"    {method.name}({args})" + (f" -> {out}" if out else ""))
        for signal in interface.signals:
            lines.append(f"    signal {signal.name}")
        for prop in interface.properties:
            lines.append(f"    property {prop.name}: {prop.signature}")
    return "\n".join(lines)


def main():
    names = list_names()
    print(f"{len(names)} well-known names on the session bus:")
    for name in names:
        print(f"  {name}")

    # The bus daemon itself is always there, which makes it a safe thing to
    # introspect in an example.
    print("\norg.freedesktop.DBus at /org/freedesktop/DBus:")
    print(introspect("org.freedesktop.DBus", "/org/freedesktop/DBus"))

    return 0


sys.exit(main())
