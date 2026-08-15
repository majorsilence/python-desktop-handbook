---
layout: chapter
title: "D-Bus"
number: 7
part: 1
---

> Every listing in this chapter is a file under `examples/gtk4/dbus/`. They are run
> on each build, under a private session bus, so the client and the service in the
> last two sections are known to talk to each other.

## Introduction

D-Bus is how programs on a Linux desktop talk to each other. Your music player
tells the shell what is playing; the shell asks your application to open a file;
your program asks the desktop to show a notification, unlock a keyring or pick a
file on its behalf. Almost everything in
[Desktop Integration](05-desktop-integration.html) is D-Bus with a wrapper over it.

There are two buses:

The **session bus**
: one per logged-in session, for the programs a user is running. This is where
  nearly everything in this chapter happens.

The **system bus**
: one per machine, for services that outlive a login — NetworkManager, systemd,
  UPower. Reading from it is usually allowed; changing things needs
  authorisation through polkit.

Use **GDBus**, which is part of GLib and therefore already imported. The old
`dbus-python` module still exists and still appears in search results; it has its
own main loop integration, its own type system and its own pitfalls, and there is
no reason to start with it now.

```python
from gi.repository import Gio, GLib

connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)
```

## The vocabulary {#vocabulary}

Five words, and then everything else is detail:

A **bus name** identifies a connection. Well-known names look like
`org.gnome.Shell`; unique names look like `:1.42` and are handed out by the bus.

An **object path** looks like a file path: `/org/gnome/Shell`. One program can
export many objects.

An **interface** is a named group of members: `org.freedesktop.DBus.Properties`.
One object can implement several.

**Methods** are calls with a reply. **Signals** are broadcasts with no reply.
**Properties** are values, read and written through a standard interface.

**Signatures** describe types: `s` string, `i` int32, `u` uint32, `b` boolean,
`d` double, `o` object path, `v` variant, `as` array of strings, `a{sv}` a
dictionary from string to variant — the shape almost every "options" argument has.
`(is)` is a struct.

## Looking before you write {#exploring}

Do not start by writing code. Start by looking at what is on the bus, with
`gdbus`, `busctl` or the D-Spy application:

```bash
gdbus introspect --session --dest org.freedesktop.Notifications \
  --object-path /org/freedesktop/Notifications

busctl --user list
```

The same three moves in Python are listing the names, introspecting an object, and
calling a method:

```python
reply = connection.call_sync(
    "org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus",
    "ListNames", None,
    GLib.VariantType("(as)"),          # the reply signature you expect
    Gio.DBusCallFlags.NONE, -1, None,
)
(names,) = reply.unpack()
```

That `(names,)` is not a typo. **A D-Bus reply is always a tuple**, even when it
carries one value, so unpacking one result means unpacking a one-element tuple.
Forgetting it gives you a tuple where you expected a list, and the error appears
somewhere else entirely.

`Gio.DBusNodeInfo.new_for_xml()` turns the introspection XML into objects, which
is how the graphical tools build their trees:

```python
info = Gio.DBusNodeInfo.new_for_xml(xml)
for interface in info.interfaces:
    for method in interface.methods:
        print(method.name, [a.signature for a in method.in_args])
```

The full example is `examples/gtk4/dbus/explore-the-bus.py`.

## Calling a service {#proxies}

`call_sync()` is fine for one call. For an object you use repeatedly, a
**proxy** is much better: it fetches the introspection data, caches the
properties, and turns method calls into ordinary Python calls.

```python
proxy = Gio.DBusProxy.new_for_bus_sync(
    Gio.BusType.SESSION,
    Gio.DBusProxyFlags.NONE,
    None,                      # introspection data; None means fetch it
    "com.example.Counter",     # bus name
    "/com/example/Counter",    # object path
    "com.example.Counter",     # interface
    None,
)

print(proxy.Increment("(i)", 3))     # method name, signature, arguments
print(proxy.Describe())
```

That `"(i)"` is the signature of the **arguments**, and it is required because
Python cannot tell an int32 from an int64 from a uint32. Get it wrong and the call
fails with a type error rather than silently sending the wrong thing.

Two things about proxies surprise people:

**Creating a proxy succeeds even when nobody is there.** It is a placeholder that
starts working when the service appears. To find out whether anything is home:

```python
if proxy.get_name_owner() is None:
    print("not running")
```

**Properties are cached, and the cache is only as fresh as the last
`PropertiesChanged` signal.**

```python
proxy.get_cached_property("Value").unpack()
```

costs nothing because the value arrived with the proxy — but if the service
changes it without announcing it, you will read the old value forever. This cuts
both ways: when you *write* a service, emit `PropertiesChanged`, and when you use
one that does not, call `Get` explicitly instead of trusting the cache.

### Calling asynchronously {#async-calls}

`call_sync()` and the proxy's attribute-style calls block until the reply comes
back, and the default timeout is 25 seconds. In a program with a window that is 25
seconds of frozen interface. Anything triggered by a user action should be
asynchronous:

```python
def on_reset(proxy, result, _data=None):
    try:
        proxy.call_finish(result)
    except GLib.Error as error:
        print(f"failed: {error.message}")

proxy.call("Reset", None, Gio.DBusCallFlags.NONE, -1, None, on_reset)
```

Same shape as every other asynchronous call in this book: a callback, a
`*_finish()` inside a `try`, and `GLib.Error` for the failure. A D-Bus call can
fail because the service is not running, because it returned an error, because it
took too long, or because you were not allowed — all of them arrive here.

The full example is `examples/gtk4/dbus/call-our-service.py`.

## Listening {#signals}

A proxy re-emits its object's signals as `g-signal`:

```python
proxy.connect("g-signal", lambda p, sender, signal, params: print(signal, params.unpack()))
proxy.connect("g-properties-changed", on_properties_changed)
```

When you want to hear about something that is not tied to one object — or from a
program that is not running yet — subscribe on the connection:

```python
subscription = connection.signal_subscribe(
    None,                            # sender
    "org.freedesktop.DBus",          # interface
    "NameOwnerChanged",              # signal
    "/org/freedesktop/DBus",         # path
    None,                            # first argument must equal this
    Gio.DBusSignalFlags.NONE,
    on_name_owner_changed,
)
```

Any filter may be `None`, meaning "do not care", but the more of them you fill in
the less traffic the bus sends you. `NameOwnerChanged` in particular fires
constantly on a busy session.

For the common case — "tell me when this service comes and goes" — there is a
helper that also handles the case where it is *already* running, which a plain
subscription does not:

```python
watch = Gio.bus_watch_name(
    Gio.BusType.SESSION, "com.example.Counter",
    Gio.BusNameWatcherFlags.NONE, on_appeared, on_vanished,
)
```

Keep the ids and undo both when you are finished:
`connection.signal_unsubscribe(subscription)` and
`Gio.bus_unwatch_name(watch)`.

The full example is `examples/gtk4/dbus/watch-signals.py`.

## Being a service {#exporting}

Exporting your own object is three things: own a name, describe an interface, and
answer calls.

Describe the interface in the same XML that `Introspect` returns:

```xml
<node>
  <interface name="com.example.Counter">
    <method name="Increment">
      <arg type="i" name="by" direction="in"/>
      <arg type="i" name="value" direction="out"/>
    </method>
    <method name="Reset"/>
    <signal name="Changed">
      <arg type="i" name="value"/>
    </signal>
    <property name="Value" type="i" access="read"/>
    <property name="Label" type="s" access="readwrite"/>
  </interface>
</node>
```

Register an object with one callback per job:

```python
node = Gio.DBusNodeInfo.new_for_xml(INTERFACE_XML)
connection.register_object(
    PATH, node.interfaces[0],
    counter.on_method_call, counter.on_get_property, counter.on_set_property,
)
```

The method handler dispatches on the name:

```python
def on_method_call(self, _connection, _sender, _path, _interface,
                   method, parameters, invocation):
    if method == "Increment":
        (by,) = parameters.unpack()
        self.value += by
        invocation.return_value(GLib.Variant("(i)", (self.value,)))
    elif method == "Reset":
        self.value = 0
        invocation.return_value(None)
    else:
        invocation.return_error_literal(
            Gio.dbus_error_quark(), Gio.DBusError.UNKNOWN_METHOD,
            f"no such method: {method}",
        )
```

**Always answer the invocation**, on every path through the handler, including the
ones you did not expect. A caller that gets no reply does not get an error — it
waits for its timeout and then gets a confusing one. `return_value(None)` is the
reply for a method that returns nothing, and it is not optional.

The reply is a GVariant **tuple** again, so a method returning one integer returns
`GLib.Variant("(i)", (value,))`.

Signals are emitted on the connection:

```python
connection.emit_signal(
    None, PATH, NAME, "Changed", GLib.Variant("(i)", (self.value,))
)
```

And when a property changes, say so — nothing does it for you:

```python
connection.emit_signal(
    None, PATH, "org.freedesktop.DBus.Properties", "PropertiesChanged",
    GLib.Variant("(sa{sv}as)", (NAME, {"Value": GLib.Variant("i", value)}, [])),
)
```

Leave that out and every client's cached copy stays at whatever it was when they
connected. The three parts of the payload are the interface, the properties whose
new values you are sending, and a list of properties that changed but whose values
you are not sending.

### Owning the name {#owning-a-name}

You can call `Gio.bus_own_name()` directly, but if your program is a
`Gio.Application` — or a `Gtk.Application` — it already owns a name: the
application id **is** the bus name.

```python
app = Gio.Application(application_id="com.example.Counter",
                      flags=Gio.ApplicationFlags.IS_SERVICE)
app.connect("startup", on_startup)          # register the object here
```

`app.get_dbus_connection()` gives you the connection to register on.
`IS_SERVICE` means the process exists to serve, and `set_inactivity_timeout()`
lets it exit when nothing has called it for a while — combined with a
`.service` file, that is how a service gets started on demand rather than at login.

There is a bonus you get without asking. Every `Gio.Action` you add to a
`Gtk.Application` is already exported over D-Bus, on the standard
`org.gtk.Actions` interface. Which means this works against any GTK application,
with no code on your side at all:

```bash
gdbus call --session --dest com.example.App --object-path /com/example/App \
  --method org.gtk.Actions.Activate quit "[]" "{}"
```

That is also how the shell shows your application's menu, and how a desktop file
with `DBusActivatable=true` gets you started.

The full example is `examples/gtk4/dbus/export-a-service.py`.

## Testing without a desktop {#testing}

D-Bus code is easy to test, because a bus is cheap:

```bash
dbus-run-session -- python3 my-service.py
dbus-run-session -- sh -c "python3 export-a-service.py & sleep 1; python3 call-our-service.py"
```

`dbus-run-session` starts a private session bus, runs the command with
`DBUS_SESSION_BUS_ADDRESS` pointing at it, and tears it down afterwards. Nothing
else on the machine can see it, so tests cannot collide, and it is how the
examples in this chapter are verified on each build.

## Portals are D-Bus {#portals}

The portals from the desktop integration chapter are ordinary D-Bus services on
`org.freedesktop.portal.Desktop` at `/org/freedesktop/portal/desktop`, and
anything without a GTK wrapper is reachable the way anything else is.

They have one unusual convention. A portal method does not return the answer; it
returns an **object path for a request**, and the answer arrives later as a
`Response` signal on that object. That is because a portal call may involve asking
the user, which can take as long as the user takes. So the sequence is: subscribe
to the response path, make the call, and wait for the signal.

This is exactly the sort of thing worth using a library for.
[libportal](https://github.com/flatpak/libportal) wraps every portal in a normal
asynchronous API and has GObject introspection, so it is `Xdp` in PyGObject:

```python
gi.require_version("Xdp", "1.0")
from gi.repository import Xdp

portal = Xdp.Portal.new()
portal.request_background(parent, "Syncing in the background", None,
                          Xdp.BackgroundFlags.AUTOSTART, None, on_done)
```

Screenshots, screen casting, location, inhibiting suspend, autostart, opening a
URI, and the trash all live there.

## Summary

- Use GDBus from GLib, not `dbus-python`.
- Session bus for the user's programs, system bus for the machine's.
- Every reply is a tuple: `(value,) = reply.unpack()`.
- Method arguments need an explicit signature, because Python's ints do not have
  one.
- A proxy exists even when the service does not; check `get_name_owner()`.
- Cached properties are only as fresh as the last `PropertiesChanged` — emit it
  from your services, and do not trust it from services that do not.
- Use the asynchronous calls in anything with a window. The default timeout is 25
  seconds.
- In a method handler, answer the invocation on every path, including the
  unexpected ones.
- A `Gtk.Application`'s id is already a bus name, and its actions are already
  exported.
- `dbus-run-session` gives you a private bus for testing.

[Animation and Transitions](08-animation.html) is next.
