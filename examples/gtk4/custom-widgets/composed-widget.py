#!/usr/bin/env python3
"""The custom widget you should usually write: a composed one.

Before overriding do_measure and do_size_allocate, ask whether you are really
making a new *kind* of widget or just a reusable arrangement of existing ones.
Almost always it is the second, and then the answer is a subclass that builds
some children in __init__, with its own properties and signals so the rest of the
program can treat it as a single thing.

This one is a search-and-filter bar: it looks like one widget from outside, has a
"query" property that can be bound, and emits "search-requested".
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GObject, Gtk

SCOPES = ["Everywhere", "Titles", "Bodies"]


class SearchBar(Gtk.Box):
    __gtype_name__ = "SearchBar"

    # The public surface: two properties and a signal. Nothing outside needs to
    # know there is an entry and a drop down in here.
    query = GObject.Property(type=str, default="")
    scope = GObject.Property(type=int, default=0)

    @GObject.Signal(arg_types=(str, int))
    def search_requested(self, query, scope):
        """Default handler; there is nothing for it to do."""

    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, **kwargs)
        self.add_css_class("toolbar")

        self._entry = Gtk.SearchEntry(hexpand=True, placeholder_text="Search…")
        self._scope = Gtk.DropDown.new_from_strings(SCOPES)
        self._button = Gtk.Button(label="Search")
        self._button.add_css_class("suggested-action")

        self.append(self._entry)
        self.append(self._scope)
        self.append(self._button)

        # Bindings rather than handlers: the property and the widget cannot drift.
        self._entry.bind_property("text", self, "query",
                                  GObject.BindingFlags.BIDIRECTIONAL
                                  | GObject.BindingFlags.SYNC_CREATE)
        self._scope.bind_property("selected", self, "scope",
                                  GObject.BindingFlags.BIDIRECTIONAL
                                  | GObject.BindingFlags.SYNC_CREATE)

        self._entry.connect("activate", lambda _e: self.emit_search())
        self._button.connect("clicked", lambda _b: self.emit_search())

    def emit_search(self):
        self.emit("search-requested", self.query, self.scope)

    def grab_focus(self):
        # Overriding this makes the composed widget behave like one widget when
        # something focuses it.
        return self._entry.grab_focus()


class Window(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Composed widget")
        self.set_default_size(520, 260)

        search = SearchBar()
        result = Gtk.Label(xalign=0, wrap=True, label="Nothing searched for yet.")

        # From out here it is one widget with one signal.
        search.connect(
            "search-requested",
            lambda _b, query, scope: result.set_text(
                f"Searching {SCOPES[scope]} for {query!r}"
                if query else "Type something first."
            ),
        )

        # And one property, which can drive anything else.
        live = Gtk.Label(xalign=0)
        search.bind_property("query", live, "label",
                             GObject.BindingFlags.SYNC_CREATE)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.append(search)
        box.append(live)
        box.append(result)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar())
        toolbar.set_content(box)
        self.set_content(toolbar)

        search.grab_focus()


def on_activate(app):
    Window(application=app).present()


app = Adw.Application(application_id="com.example.ComposedWidget")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
