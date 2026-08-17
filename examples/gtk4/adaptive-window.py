#!/usr/bin/env python3
"""One window that works at desk width and at phone width, via AdwBreakpoint.

A breakpoint is a condition plus a list of properties to set while it holds.
There is no resize handler here and no layout arithmetic: the window is told
what "narrow" means and what to change, and libadwaita does the rest.

Needs libadwaita 1.4 for AdwBreakpoint and 1.4 for AdwOverlaySplitView.
"""

import sys

from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GObject, Gtk

# Below this width the sidebar stops sitting beside the content and starts
# overlaying it. 600sp is the conventional phone/desktop divide; "sp" is a
# scalable pixel, so the breakpoint moves with the user's text scaling instead
# of firing at the wrong size on a scaled display.
NARROW = "max-width: 600sp"

PAGES = [
    ("Inbox", "mail-unread-symbolic", "Nothing new."),
    ("Drafts", "document-edit-symbolic", "Two drafts, both terrible."),
    ("Sent", "mail-send-symbolic", "Everything you have regretted."),
]


class Window(Adw.ApplicationWindow):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.set_title("Adaptive Window")
        self.set_default_size(760, 480)

        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE)
        sidebar_list = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        sidebar_list.add_css_class("navigation-sidebar")

        for title, icon, body in PAGES:
            self.stack.add_named(self._page(title, body), title)
            sidebar_list.append(Adw.ActionRow(title=title, icon_name=icon))

        sidebar_list.connect("row-selected", self.on_row_selected)

        # The split view is the thing that actually adapts. Collapsed, the
        # sidebar becomes an overlay that slides over the content; expanded, it
        # is a pane beside it. Both states are the same widget tree.
        self.split = Adw.OverlaySplitView(sidebar=self._sidebar(sidebar_list),
                                          content=self._content())
        self.set_content(self.split)

        # A breakpoint is declarative: this condition, these property settings.
        # add_setter() takes the object, the property name and the value to use
        # while the condition holds -- and libadwaita puts the old value back
        # when it stops holding, which is the part you would get wrong by hand.
        narrow = Adw.Breakpoint.new(Adw.BreakpointCondition.parse(NARROW))
        narrow.add_setter(self.split, "collapsed", True)
        narrow.add_setter(self.show_sidebar_button, "visible", True)
        self.add_breakpoint(narrow)

        # Selecting the first row fires "row-selected", whose handler reaches
        # for self.split -- so it has to happen after the split view exists.
        sidebar_list.select_row(sidebar_list.get_row_at_index(0))

    def _sidebar(self, listbox: Gtk.ListBox) -> Gtk.Widget:
        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar(show_end_title_buttons=False))
        toolbar.set_content(listbox)
        return toolbar

    def _content(self) -> Gtk.Widget:
        # Hidden until the breakpoint reveals it: with the sidebar beside the
        # content there is nothing for it to toggle.
        self.show_sidebar_button = Gtk.ToggleButton(icon_name="sidebar-show-symbolic",
                                                    visible=False)
        self.show_sidebar_button.set_tooltip_text("Show sidebar")

        header = Adw.HeaderBar()
        header.pack_start(self.show_sidebar_button)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(header)
        toolbar.set_content(self.stack)
        return toolbar

    def _page(self, title: str, body: str) -> Gtk.Widget:
        status = Adw.StatusPage(title=title, description=body)
        status.set_icon_name("view-list-symbolic")
        return status

    def on_row_selected(self, _listbox: Gtk.ListBox, row: Gtk.ListBoxRow | None) -> None:
        if row is None:
            return
        self.stack.set_visible_child_name(row.get_title())
        # Selecting a page on a phone should get the sidebar out of the way.
        if self.split.get_collapsed():
            self.split.set_show_sidebar(False)


def on_activate(app: Adw.Application) -> None:
    window = Window(application=app)
    # Bind after construction: the toggle drives the split view, and the split
    # view drives the toggle back when the breakpoint or a click changes it.
    window.show_sidebar_button.bind_property(
        "active", window.split, "show-sidebar",
        GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
    window.present()


app = Adw.Application(application_id="com.example.AdaptiveWindow")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
