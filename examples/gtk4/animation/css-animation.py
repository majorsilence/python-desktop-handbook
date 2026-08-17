#!/usr/bin/env python3
"""Animation without any animation code, using GTK's CSS.

GTK styles widgets with a subset of CSS, and that subset includes transitions and
keyframe animations. For anything that is really a style change -- a hover
colour, a pulsing indicator, a spinner -- this is less code than an AdwAnimation
and it runs entirely inside GTK.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gtk

CSS = b"""
/* A transition animates a property when its value changes, however it changes
   -- adding a class, hovering, or getting focus. */
.swatch {
    background: #3584e4;
    border-radius: 12px;
    min-width: 120px;
    min-height: 120px;
    transition: background 400ms ease-in-out,
                border-radius 400ms ease-in-out;
}

.swatch:hover {
    background: #813d9c;
}

.swatch.round {
    background: #2ec27e;
    border-radius: 60px;
}

/* A keyframe animation runs on its own, for as long as the class is applied. */
@keyframes pulse {
    from { opacity: 1;   }
    50%  { opacity: 0.35; }
    to   { opacity: 1;   }
}

.pulsing {
    animation: pulse 1.2s ease-in-out infinite;
}

/* GTK understands the same reduced-motion query browsers do, and the desktop
   sets it from the accessibility preference. */
@media (prefers-reduced-motion: reduce) {
    .swatch  { transition: none; }
    .pulsing { animation: none; }
}
"""


def on_activate(app: Gtk.Application) -> None:
    # A CSS provider is loaded once and added to the display, not to a widget.
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )

    window = Gtk.ApplicationWindow(application=app, title="CSS animation")
    window.set_default_size(420, 300)

    swatch = Gtk.Box()
    swatch.add_css_class("swatch")
    swatch.set_halign(Gtk.Align.CENTER)

    # Toggling a class is all it takes: the transition in the CSS does the rest.
    round_toggle = Gtk.ToggleButton(label="Round it")
    round_toggle.connect(
        "toggled",
        lambda b: (swatch.add_css_class("round") if b.get_active()
                   else swatch.remove_css_class("round")),
    )

    pulse_toggle = Gtk.ToggleButton(label="Pulse")
    pulse_toggle.connect(
        "toggled",
        lambda b: (swatch.add_css_class("pulsing") if b.get_active()
                   else swatch.remove_css_class("pulsing")),
    )

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(18)
    box.set_margin_bottom(18)
    box.set_margin_start(18)
    box.set_margin_end(18)
    box.append(swatch)
    box.append(Gtk.Label(label="Hover the square, or use the buttons."))
    box.append(round_toggle)
    box.append(pulse_toggle)

    window.set_child(box)
    window.present()


app = Gtk.Application(application_id="com.example.CssAnimation")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
