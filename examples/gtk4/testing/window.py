#!/usr/bin/env python3
"""The interface half: widgets over the TaskList, and as little logic as possible.

Every method here is a translation between a widget and the model. When one of
them starts making a decision -- what counts as a duplicate, what to do about an
empty title -- that decision belongs in tasklist.py instead, where a test can
reach it without a display.
"""
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GObject, Gtk

from tasklist import Task, TaskList


class Window(Adw.ApplicationWindow):
    __gtype_name__ = "TestingWindow"

    def __init__(self, tasks: TaskList | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.tasks = tasks if tasks is not None else TaskList()
        self.set_title("Tasks")
        self.set_default_size(420, 480)

        self.entry = Gtk.Entry(placeholder_text="What needs doing?", hexpand=True)
        self.entry.connect("activate", self.on_add)

        add = Gtk.Button(icon_name="list-add-symbolic")
        add.connect("clicked", self.on_add)

        entry_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        entry_row.append(self.entry)
        entry_row.append(add)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.on_setup)
        factory.connect("bind", self.on_bind)

        self.list_view = Gtk.ListView(
            model=Gtk.NoSelection.new(self.tasks.store), factory=factory)
        scroller = Gtk.ScrolledWindow(vexpand=True, child=self.list_view)

        self.status = Gtk.Label(xalign=0)
        self.tasks.connect("notify::remaining", self.on_remaining_changed)
        self.on_remaining_changed()

        clear = Gtk.Button(label="Clear finished")
        clear.connect("clicked", self.on_clear)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        for widget in (entry_row, scroller, self.status, clear):
            box.append(widget)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar())
        toolbar.set_content(box)
        self.set_content(toolbar)

    # -- factory ------------------------------------------------------------------

    def on_setup(self, _factory: Gtk.SignalListItemFactory,
                 item: Gtk.ListItem) -> None:
        item.set_child(Gtk.CheckButton())

    def on_bind(self, _factory: Gtk.SignalListItemFactory,
                item: Gtk.ListItem) -> None:
        check = item.get_child()
        task = item.get_item()
        # get_child() and get_item() are typed as Optional, because a list item
        # is not always bound. Narrowing here rather than ignoring the warning
        # is what makes the checker useful on the next line instead of noisy.
        assert isinstance(check, Gtk.CheckButton)
        assert isinstance(task, Task)

        check.set_label(task.title)
        check.set_active(task.done)
        # Bidirectional, so the checkbox and the model cannot disagree -- and so
        # a test can set `task.done` and see the widget follow.
        task.bind_property(
            "done", check, "active",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)

    # -- handlers -----------------------------------------------------------------

    def on_add(self, _widget: Gtk.Widget) -> None:
        try:
            self.tasks.add(self.entry.get_text())
        except ValueError as error:
            # The rule lives in the model; the window only reports it.
            self.status.set_text(str(error))
            return
        self.entry.set_text("")

    def on_clear(self, _button: Gtk.Button) -> None:
        gone = self.tasks.clear_done()
        self.status.set_text(f"Removed {gone}.")

    def on_remaining_changed(self, *_args: object) -> None:
        remaining = self.tasks.remaining
        self.status.set_text(f"{remaining} left" if remaining else "Nothing left.")
