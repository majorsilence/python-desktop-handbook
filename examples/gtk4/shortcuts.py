#!/usr/bin/env python3
"""Keyboard shortcuts: accelerators on actions, controllers on widgets.

There are two mechanisms and they are for different things.

  * An **accelerator** is a key combination bound to an action, application
    wide. This is what you want almost every time. The action already exists,
    the menu item already refers to it, and the accelerator is one more line.
  * A **shortcut controller** is attached to a widget and only fires while that
    widget's part of the window has focus. Use it for keys that mean something
    local, and for anything not worth an action.

Then there is a third job, which people skip: telling the user the keys exist.
AdwShortcutsDialog (libadwaita 1.8) is the standard window for that.
"""

import sys

from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, Gtk

# Action name, accelerator, what it does, and how the shortcuts window
# describes it. Keeping them in one table is what stops the menu, the
# accelerator and the help window from drifting apart.
ACTIONS = [
    ("new", ["<Control>n"], "New document"),
    ("open", ["<Control>o"], "Open a document"),
    ("save", ["<Control>s"], "Save"),
    ("quit", ["<Control>q"], "Quit"),
]


class Window(Adw.ApplicationWindow):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.set_title("Shortcuts")
        self.set_default_size(480, 300)

        self.log = Gtk.Label(label="Press a shortcut.", xalign=0, wrap=True)
        self.lines: list[str] = []

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.append(Gtk.Label(label="Try Ctrl+N, Ctrl+S, Ctrl+D or Ctrl+question."))
        box.append(self.log)

        header = Adw.HeaderBar()
        menu = Gio.Menu()
        for name, _accel, label in ACTIONS:
            menu.append(label, f"app.{name}")
        header.pack_end(Gtk.MenuButton(icon_name="open-menu-symbolic",
                                       menu_model=menu))

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(header)
        toolbar.set_content(box)
        self.set_content(toolbar)

        self.add_local_shortcut()

    def add_local_shortcut(self) -> None:
        """Ctrl+D, handled by this window rather than by the application.

        A Gtk.Shortcut is a trigger plus an action. Gtk.CallbackAction is the
        escape hatch that runs a Python function; the callback must return True
        to say it handled the key, or the shortcut keeps propagating.
        """
        controller = Gtk.ShortcutController()
        controller.set_scope(Gtk.ShortcutScope.LOCAL)
        controller.add_shortcut(Gtk.Shortcut(
            trigger=Gtk.ShortcutTrigger.parse_string("<Control>d"),
            action=Gtk.CallbackAction.new(self.on_duplicate)))
        self.add_controller(controller)

    def on_duplicate(self, _widget: Gtk.Widget, _args: object) -> bool:
        self.note("Ctrl+D — duplicate (window-local shortcut)")
        return True

    def note(self, text: str) -> None:
        self.lines.append(text)
        self.log.set_text("\n".join(self.lines[-8:]))


def build_shortcuts_dialog() -> Adw.ShortcutsDialog:
    """The window the user opens to find out what the keys are."""
    dialog = Adw.ShortcutsDialog()

    general = Adw.ShortcutsSection(title="General")
    for name, accels, label in ACTIONS:
        general.add(Adw.ShortcutsItem(title=label, accelerator=accels[0]))
    dialog.add(general)

    editing = Adw.ShortcutsSection(title="Editing")
    editing.add(Adw.ShortcutsItem(title="Duplicate", accelerator="<Control>d"))
    dialog.add(editing)

    return dialog


def on_activate(app: Adw.Application) -> None:
    window = Window(application=app)

    for name, _accels, label in ACTIONS:
        action = Gio.SimpleAction.new(name, None)
        if name == "quit":
            action.connect("activate", lambda _a, _p: app.quit())
        else:
            action.connect("activate",
                           lambda _a, _p, label=label: window.note(f"{label} (action)"))
        app.add_action(action)

    # The binding itself. Note the plural: an action can have several, which is
    # how you support both Ctrl+? and F1 for the same thing.
    for name, accels, _label in ACTIONS:
        app.set_accels_for_action(f"app.{name}", accels)

    help_action = Gio.SimpleAction.new("shortcuts", None)
    help_action.connect("activate",
                        lambda _a, _p: build_shortcuts_dialog().present(window))
    app.add_action(help_action)
    # <Control>question is the desktop-wide convention for "what are the keys?".
    app.set_accels_for_action("app.shortcuts", ["<Control>question", "F1"])

    window.present()


app = Adw.Application(application_id="com.example.Shortcuts")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
