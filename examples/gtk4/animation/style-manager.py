#!/usr/bin/env python3
"""Dark mode, accent colour and high contrast, via AdwStyleManager.

These are the user's settings, not yours. The desktop already knows whether the
user wants a dark interface, which accent colour they picked and whether they
need higher contrast; libadwaita applies all three to its widgets for you. Your
job is a narrow one: notice when they change, and make sure anything you drew
yourself changes with them.

The three things to get right:

  * Follow the system by default. ADW_COLOR_SCHEME_DEFAULT is the correct value
    and an application that hardcodes dark is an application that ignores the
    user.
  * If you offer a preference, offer three states -- system, light, dark -- with
    system as the default, and store it in GSettings.
  * Never hardcode a colour that should have come from the theme. Use the named
    CSS colours, or read them back and repaint when they change.

Accent colour needs libadwaita 1.6.
"""

import sys

import cairo
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk

# Adw.ColorScheme.DEFAULT means "whatever the desktop says". The two PREFER_
# values are requests the desktop may decline; the two FORCE_ values are not.
SCHEMES = {
    "Follow the system": Adw.ColorScheme.DEFAULT,
    "Light": Adw.ColorScheme.FORCE_LIGHT,
    "Dark": Adw.ColorScheme.FORCE_DARK,
}


class Window(Adw.ApplicationWindow):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.set_title("Style")
        self.set_default_size(460, 420)

        self.style = Adw.StyleManager.get_default()

        page = Adw.PreferencesPage()
        group = Adw.PreferencesGroup(title="Appearance")

        # A drop-down over the three states, which is the shape a colour scheme
        # preference should have. Storing the choice is GSettings' job; see the
        # desktop integration chapter.
        self.chooser = Adw.ComboRow(title="Colour scheme",
                                    model=Gtk.StringList.new(list(SCHEMES)))
        self.chooser.connect("notify::selected", self.on_scheme_chosen)
        group.add(self.chooser)
        page.add(group)

        state = Adw.PreferencesGroup(title="What the desktop is telling us")
        self.dark_row = Adw.ActionRow(title="Dark")
        self.accent_row = Adw.ActionRow(title="Accent colour")
        self.contrast_row = Adw.ActionRow(title="High contrast")
        self.supported_row = Adw.ActionRow(title="Desktop supports colour schemes")
        for row in (self.dark_row, self.accent_row, self.contrast_row,
                    self.supported_row):
            state.add(row)
        page.add(state)

        # A swatch drawn by hand, standing in for anything you render yourself:
        # a chart, a canvas, a custom widget. This is the code that has to be
        # told when the theme changes, because the stylesheet cannot reach it.
        self.swatch = Gtk.DrawingArea(content_height=80)
        self.swatch.set_draw_func(self.draw_swatch)
        swatch_group = Adw.PreferencesGroup(
            title="Something drawn by hand",
            description="Redrawn whenever the accent colour or dark state changes")
        swatch_group.add(self.swatch)
        page.add(swatch_group)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar())
        toolbar.set_content(page)
        self.set_content(toolbar)

        # Three properties to watch. Connecting to them is the whole of
        # "responding to the theme"; there is no polling and no timer.
        for property_name in ("dark", "accent-color", "high-contrast"):
            self.style.connect(f"notify::{property_name}", self.on_style_changed)
        self.refresh()

    def on_scheme_chosen(self, row: Adw.ComboRow, _pspec: object) -> None:
        name = list(SCHEMES)[row.get_selected()]
        self.style.set_color_scheme(SCHEMES[name])

    def on_style_changed(self, _style: Adw.StyleManager, _pspec: object) -> None:
        self.refresh()

    def refresh(self) -> None:
        self.dark_row.set_subtitle("yes" if self.style.get_dark() else "no")
        self.accent_row.set_subtitle(self.style.get_accent_color().to_standalone_rgba().to_string())
        self.contrast_row.set_subtitle("yes" if self.style.get_high_contrast() else "no")
        self.supported_row.set_subtitle(
            "yes" if self.style.get_system_supports_color_schemes() else "no")
        self.swatch.queue_draw()

    def draw_swatch(self, _area: Gtk.DrawingArea, cr: cairo.Context,
                    width: int, height: int) -> None:
        # to_standalone_rgba() gives the accent adjusted for the current light or
        # dark background, which is what you want for something you are painting
        # yourself. get_accent_color() alone is the unadjusted brand colour.
        rgba = self.style.get_accent_color().to_standalone_rgba()
        cr.set_source_rgba(rgba.red, rgba.green, rgba.blue, rgba.alpha)
        cr.rectangle(0, 0, width, height)
        cr.fill()


def on_activate(app: Adw.Application) -> None:
    Window(application=app).present()


app = Adw.Application(application_id="com.example.StyleManager")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
