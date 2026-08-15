---
layout: chapter
title: "GObject: Properties, Signals and Bindings"
number: 2
part: 1
---

> Every listing in this chapter is a file under `examples/gtk4/gobject/`. They are
> run on each build, so if one of them stops working the build says so.

## Introduction

GTK is written in C, and C has no objects. GObject is the object system that was
built to give it some — classes, inheritance, virtual methods, properties, signals
and runtime type information, in plain C.

You could reasonably ask why a Python programmer should care. Python already has
all of that.

The answer is that **GObject's versions of those things are the ones GTK can see**.
A Python attribute is invisible to GTK. A GObject property can be watched for
changes, bound to another object's property, read by a `Gtk.Expression`, sorted
and filtered on, set from a `.ui` file, and animated by libadwaita. Everything in
[More GTK 4](03-more-gtk4.html) — list models, sorters, filters — is built on
properties, and none of it works on a plain attribute.

This chapter is the fifteen minutes that makes the rest of Part I stop feeling
arbitrary.

## Subclassing {#subclassing}

```python
from gi.repository import GObject


class Person(GObject.Object):
    __gtype_name__ = "Person"

    def __init__(self, name=""):
        super().__init__()
        self.name = name
```

Two things are different from an ordinary Python class.

**`super().__init__()` is not optional**, and it has to run before anything touches
a property. GObject construction happens on the C side; skipping it leaves a
half-built object that fails later and confusingly.

**`__gtype_name__` gives the type a name on the C side.** Without it PyGObject
invents one from the class name, which is fine until two classes in one process
end up with the same invented name — at which point registration fails outright.
Set it, make it unique, and prefix it with something of your own in a library.

You subclass GTK widgets the same way, which is how
`class Window(Adw.ApplicationWindow)` works in every other chapter.

## Properties {#properties}

```python
class Person(GObject.Object):
    __gtype_name__ = "Person"

    name = GObject.Property(type=str, default="")
    age = GObject.Property(type=int, default=0, minimum=0, maximum=150)
```

That is the whole declaration. `name` and `age` now read and write like ordinary
attributes:

```python
person.age = 37
print(person.name)
```

and also by name, which is the part that matters:

```python
person.get_property("name")
person.set_property("age", 37)
```

Anything generic — a binding, a sorter, a `.ui` file, an animation — reaches your
data through that second form.

### Naming {#property-naming}

A property declared as `date_of_birth` is called **`date-of-birth`** by GTK.
Underscores become hyphens at the boundary. Python code uses the underscore
spelling, and everything taking a property *name* as a string — `bind_property`,
`notify::`, `Gtk.PropertyExpression` — uses hyphens. Both spellings are accepted
in most places; hyphens are what the documentation uses.

### Computed and validating properties {#property-accessors}

For a property that is derived, or that has to check or normalise what it is
given, use the decorator form:

```python
@GObject.Property(type=str)
def nickname(self):
    return self._nickname

@nickname.setter
def nickname(self, value):
    self._nickname = value.strip().title()
```

A read-only property is one with no setter and the `READABLE` flag:

```python
@GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
def summary(self):
    return f"{self.name}, aged {self.age}"
```

A derived property has to be **told** when its inputs change, or nothing watching
it will ever hear:

```python
self.connect("notify::name", lambda *_: self.notify("summary"))
self.connect("notify::age", lambda *_: self.notify("summary"))
```

### Watching for changes {#notify}

Every property emits `notify::<name>` when it changes:

```python
person.connect("notify::age", lambda obj, pspec: print(obj.age))
```

The handler takes the object and a `GParamSpec` describing the property. You will
ignore the second argument almost every time, and it still has to be in the
signature.

This is the same mechanism as the `notify::selected`, `notify::active` and
`notify::timestamp` handlers in earlier chapters. It is not a special case for
widgets — it is how every GObject reports change.

### How they fail {#property-failures}

The two failure modes are not symmetrical, and one of them is easy to miss:

```python
person.age = 300        # out of range
person.age = "thirty"   # wrong type
```

**Out of range warns and leaves the old value in place.** It is not clamped, and
nothing is raised — you get a `Warning` on stderr and `person.age` is still
whatever it was. In a program that already prints warnings, this is invisible.

**The wrong type raises `TypeError`**, because the conversion cannot even be
attempted.

So a range on a property is a good assertion and a bad validator. If a value
coming from outside your program has to be inside a range, check it yourself
before assigning.

The full example is `examples/gtk4/gobject/properties.py`.

## Signals {#signals}

Widgets emit signals; so can your own objects. A custom signal is right whenever a
component needs to announce something without knowing who is listening — which
keeps a component from having to hold a reference to everything that cares about
it.

```python
class Download(GObject.Object):
    __gtype_name__ = "Download"

    @GObject.Signal(arg_types=(str,))
    def started(self, url):
        print(f"started {url}")

    finished = GObject.Signal()
```

`finished` is a signal with no arguments and no body. `started` takes a string, and
its method body is the signal's **default handler**.

```python
download.emit("started", "https://example.com/f")
download.connect("started", lambda _d, url: ...)
```

### The default handler runs first {#run-first}

With no flags, a signal is `RUN_FIRST`: the method body runs **before** anything
connected with `connect()`. That surprises people who expect the class's own
behaviour to be the fallback. If you want it to be a fallback, say so:

```python
@GObject.Signal(flags=GObject.SignalFlags.RUN_LAST)
```

### Return values and vetoes {#accumulators}

A signal can return a value, and an **accumulator** decides what happens when
several handlers each return one. The useful one is
`signal_accumulator_true_handled`: emission stops at the first handler returning
`True`, and that becomes the result.

```python
@GObject.Signal(return_type=bool, arg_types=(str,),
                flags=GObject.SignalFlags.RUN_LAST,
                accumulator=GObject.signal_accumulator_true_handled)
def confirm_overwrite(self, filename):
    return False        # nobody objected


if self.emit("confirm_overwrite", filename):
    return              # somebody did
```

That is the veto pattern, and it is exactly how GTK's own `delete-event`-style
signals work: any listener can say "I have handled this, stop".

With no listeners connected, the default handler's `False` stands — so the
sensible behaviour is the one you get for free.

### Disconnecting {#disconnecting}

```python
handler = obj.connect("finished", on_finished)
obj.disconnect(handler)
```

Worth caring about for one reason: **a connected handler holds a reference**. If a
long-lived object holds a handler that closes over a window, that window cannot be
finalised when it closes. The symptom is a program whose memory grows every time a
dialog is opened.

The rule of thumb: connecting a widget to itself, or to something it owns, needs no
thought. Connecting a *short-lived* object to a *long-lived* one means keeping the
handler id and disconnecting when the short-lived one goes away.

The full example is `examples/gtk4/gobject/signals.py`.

## Bindings {#bindings}

`bind_property()` is the most under-used thing in GObject. Any time you would
write "when this changes, set that", a binding is shorter, cannot get the two out
of sync, and cleans itself up when either object is finalised.

```python
switch.bind_property("active", settings, "enabled",
                     GObject.BindingFlags.SYNC_CREATE
                     | GObject.BindingFlags.BIDIRECTIONAL)
```

The flags are the whole API:

`SYNC_CREATE`
: Copy the current value across immediately. **Almost always what you want.**
  Without it the target keeps whatever it had until the source next changes,
  which is the usual cause of "my binding does not work" on the first frame.

`BIDIRECTIONAL`
: Changes flow both ways.

`INVERT_BOOLEAN`
: For the commonest transform of all.

For anything else, supply a transform function. It returns a `(handled, value)`
pair, and returning `False` rejects the value and leaves the target alone:

```python
def to_percent(_binding, value):
    return True, f"{value * 100:.0f}%"

settings.bind_property("volume", label, "label",
                       GObject.BindingFlags.SYNC_CREATE, to_percent)
```

One property can drive several targets, which is how a single `enabled` setting
greys out four widgets with no handler at all.

### Not everything is a property {#not-a-property}

A method called `get_value()` does not imply a property called `value`. The one
that catches everyone:

```python
scale.bind_property("value", settings, "volume", ...)
# TypeError: Cannot create binding from <Gtk.Scale ...>.value
```

A `Gtk.Scale` keeps its value in its `Gtk.Adjustment`, and that is what the
binding attaches to:

```python
scale.get_adjustment().bind_property("value", settings, "volume", ...)
```

Similarly `Gtk.WebView.can_go_back()` in
[Embedding Web Content](12-web-content.html) is a method with no property behind
it. When a binding fails with "cannot create binding", the property does not
exist under that name — check the API reference, or ask the object:

```python
print([p.name for p in obj.list_properties()])
```

### Keeping the binding {#binding-lifetime}

`bind_property()` returns a `GObject.Binding`. You can ignore it — the binding
lives as long as both objects — but keep it if it has to be taken apart early:

```python
binding = source.bind_property(...)
binding.unbind()
```

The full example is `examples/gtk4/gobject/bindings.py`.

## Why the list widgets needed all this {#why-lists}

Now the shape of [More GTK 4](03-more-gtk4.html) should make sense.

A `Gio.ListStore` holds GObjects because the machinery around it — sorters,
filters, expressions — reaches values through the property system. A
`Gtk.PropertyExpression.new(Package, None, "name")` is a compiled instruction to
read the `name` property, evaluated in C over a million rows without Python being
involved. The `bind_property` in a list factory's `bind` handler keeps a check
button and a data object in step with no callback. And a row updates when the
underlying object changes because the object emits `notify`.

None of it can see `self.name = name`. All of it can see
`name = GObject.Property(type=str)`.

## Summary

- `super().__init__()` first, and set `__gtype_name__`.
- `GObject.Property` is what GTK can see; a plain attribute is not.
- `date_of_birth` in Python is `date-of-birth` to anything taking a name.
- Every property emits `notify::<name>`; derived properties must call `notify()`
  themselves.
- Out-of-range assignment warns and keeps the old value; the wrong type raises.
- A signal's default handler runs *first* unless you ask for `RUN_LAST`.
- `signal_accumulator_true_handled` gives you a veto.
- Keep handler ids when a short-lived object connects to a long-lived one.
- `bind_property` with `SYNC_CREATE` replaces most "when this changes" handlers.
- "Cannot create binding" means the property does not exist under that name.

[More GTK 4](03-more-gtk4.html) is next, and now the list machinery has a reason
for being the shape it is.
