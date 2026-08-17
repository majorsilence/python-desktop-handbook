#!/usr/bin/env python3
"""A sortable, filterable table in a GtkColumnView.

The same model/factory split as GtkListView, with one factory per column, plus
two model wrappers: a filter model and a sort model chained in front of the store.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GObject, Gtk


class Package(GObject.Object):
    __gtype_name__ = "Package"

    name = GObject.Property(type=str, default="")
    version = GObject.Property(type=str, default="")
    size = GObject.Property(type=int, default=0)

    def __init__(self, name: str, version: str, size: int) -> None:
        super().__init__(name=name, version=version, size=size)


PACKAGES = [
    Package("gtk4", "4.22.4", 24_000),
    Package("libadwaita", "1.8.0", 6_100),
    Package("pygobject", "3.56.2", 1_200),
    Package("gstreamer", "1.26.0", 18_400),
    Package("cairo", "1.18.4", 3_300),
]


def text_column(title: str, attribute: str, expand: bool = False,
                numeric: bool = False) -> Gtk.ColumnViewColumn:
    """A column that shows one string property of the item."""

    def setup(_factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem) -> None:
        label = Gtk.Label(xalign=1 if numeric else 0)
        list_item.set_child(label)

    def bind(_factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem) -> None:
        value = list_item.get_item().get_property(attribute)
        text = f"{value:,} kB" if numeric else str(value)
        list_item.get_child().set_text(text)

    factory = Gtk.SignalListItemFactory()
    factory.connect("setup", setup)
    factory.connect("bind", bind)

    column = Gtk.ColumnViewColumn(title=title, factory=factory)
    column.set_expand(expand)

    # A sorter reads the property through an expression, so sorting happens in C
    # over the model rather than in Python over the rows.
    expression = Gtk.PropertyExpression.new(Package, None, attribute)
    if numeric:
        column.set_sorter(Gtk.NumericSorter(expression=expression))
    else:
        column.set_sorter(Gtk.StringSorter(expression=expression))
    return column


def on_activate(app: Gtk.Application) -> None:
    window = Gtk.ApplicationWindow(application=app, title="Column View")
    window.set_default_size(520, 320)

    store = Gio.ListStore(item_type=Package)
    for package in PACKAGES:
        store.append(package)

    # store -> filter -> sort -> selection -> view
    text_filter = Gtk.StringFilter(
        expression=Gtk.PropertyExpression.new(Package, None, "name"),
        match_mode=Gtk.StringFilterMatchMode.SUBSTRING,
    )
    filtered = Gtk.FilterListModel(model=store, filter=text_filter)
    sorted_model = Gtk.SortListModel(model=filtered)
    selection = Gtk.SingleSelection(model=sorted_model)

    view = Gtk.ColumnView(model=selection)
    view.append_column(text_column("Name", "name", expand=True))
    view.append_column(text_column("Version", "version"))
    view.append_column(text_column("Size", "size", numeric=True))

    # The view owns a sorter that reflects which column header was clicked.
    sorted_model.set_sorter(view.get_sorter())

    search = Gtk.SearchEntry(placeholder_text="Filter by name")
    search.connect("search-changed", lambda e: text_filter.set_search(e.get_text()))

    scroller = Gtk.ScrolledWindow(vexpand=True)
    scroller.set_child(view)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    box.append(search)
    box.append(scroller)
    window.set_child(box)
    window.present()


app = Gtk.Application(application_id="com.example.ColumnView")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
