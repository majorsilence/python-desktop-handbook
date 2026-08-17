#!/usr/bin/env python3
"""Properties: the part of GObject that everything else is built on.

A plain Python attribute is invisible to GTK. A GObject property can be watched
for changes, bound to another object's property, read by a Gtk.Expression, sorted
on, and set from a .ui file. Every list model in this book depends on that.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject, Gtk


class Person(GObject.Object):
    # The name this type has on the C side. Without it PyGObject invents one, and
    # two classes with the same invented name in one process is an error.
    __gtype_name__ = "Person"

    # The simple form: a type and a default. PyGObject creates the storage.
    name = GObject.Property(type=str, default="")
    age = GObject.Property(type=int, default=0, minimum=0, maximum=150)

    # Read-only from outside: no setter, so it cannot be assigned.
    @GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
    def summary(self) -> str:
        return f"{self.name}, aged {self.age}"

    # The explicit form, when setting has to do something. Note the property name
    # seen by GTK is the attribute name with underscores turned into hyphens:
    # "nickname" here, but "date-of-birth" for a date_of_birth attribute.
    @GObject.Property(type=str)
    def nickname(self) -> str:
        return self._nickname

    @nickname.setter
    def nickname(self, value: float) -> None:
        self._nickname = value.strip().title()

    def __init__(self, name: str = "", age: int = 0) -> None:
        super().__init__(name=name, age=age)
        self._nickname = ""

        # summary is derived, so it has to be told when its inputs change.
        self.connect("notify::name", lambda *_: self.notify("summary"))
        self.connect("notify::age", lambda *_: self.notify("summary"))


def on_activate(app: Gtk.Application) -> None:
    window = Gtk.ApplicationWindow(application=app, title="Properties")
    window.set_default_size(420, 300)

    person = Person(name="Ada", age=36)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    # Properties are read and written like attributes...
    print("name is", person.name)
    person.age = 37

    # ...or by name, which is what makes them useful to anything generic.
    print("by name:", person.get_property("name"), person.get_property("age"))
    print("summary:", person.summary)

    # Range and type violations fail differently, and neither does what you might
    # guess. Out of range warns and *leaves the old value in place* -- it is not
    # clamped, and nothing is raised, so a bug here is easy to miss.
    person.age = 300
    print("after setting 300, age is still", person.age)

    # The wrong type does raise, because the conversion cannot even be attempted.
    try:
        person.age = "thirty"
    except TypeError as error:
        print("wrong type rejected:", error)

    name_entry = Gtk.Entry(text=person.name)
    age_spin = Gtk.SpinButton.new_with_range(0, 150, 1)
    age_spin.set_value(person.age)
    summary = Gtk.Label(xalign=0)

    # Two-way bindings, so the widgets and the object cannot disagree.
    name_entry.bind_property("text", person, "name",
                             GObject.BindingFlags.BIDIRECTIONAL)
    age_spin.bind_property("value", person, "age",
                           GObject.BindingFlags.BIDIRECTIONAL)

    # And a one-way notify for the derived value.
    person.connect("notify::summary", lambda p, _s: summary.set_text(p.summary))
    summary.set_text(person.summary)

    nickname = Gtk.Entry(placeholder_text="Nickname (gets tidied up)")
    nickname.connect("activate", lambda e: (setattr(person, "nickname", e.get_text()),
                                            e.set_text(person.nickname)))

    for widget in (name_entry, age_spin, nickname, summary):
        box.append(widget)
    window.set_child(box)
    window.present()


app = Gtk.Application(application_id="com.example.Properties")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
