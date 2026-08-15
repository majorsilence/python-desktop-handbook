#!/usr/bin/env python3
"""A libadwaita window: header bar, toolbar view, and toasts for feedback.

GtkStatusbar is deprecated in GTK 4.  Transient feedback now goes in an
AdwToast, which slides in over the content and disappears on its own.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk


class Window(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Adwaita Window")
        self.set_default_size(420, 260)

        self.toasts = Adw.ToastOverlay()

        page = Adw.PreferencesPage()
        group = Adw.PreferencesGroup(title="Settings", description="Rows lay themselves out")

        self.switch_row = Adw.SwitchRow(title="Enabled", subtitle="Flip me")
        self.switch_row.connect("notify::active", self.on_switch)
        group.add(self.switch_row)

        entry_row = Adw.EntryRow(title="Your name")
        group.add(entry_row)

        button = Gtk.Button(label="Save")
        button.add_css_class("suggested-action")
        button.set_halign(Gtk.Align.CENTER)
        button.connect("clicked", self.on_save)
        group.add(button)

        page.add(group)
        self.toasts.set_child(page)

        # AdwToolbarView keeps the header bar pinned above scrolling content.
        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar())
        toolbar.set_content(self.toasts)

        self.set_content(toolbar)

    def on_switch(self, row, _pspec):
        state = "on" if row.get_active() else "off"
        self.toasts.add_toast(Adw.Toast.new(f"Switched {state}"))

    def on_save(self, _button):
        toast = Adw.Toast.new("Saved")
        toast.set_button_label("Undo")
        toast.connect("button-clicked", lambda _t: print("undo"))
        self.toasts.add_toast(toast)


def on_activate(app):
    Window(application=app).present()


app = Adw.Application(application_id="com.example.AdwaitaWindow")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
