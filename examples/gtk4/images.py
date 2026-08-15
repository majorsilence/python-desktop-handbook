#!/usr/bin/env python3
"""Icons with GtkImage, photographs with GtkPicture.

GtkImage is sized by the icon theme and is for small symbolic icons.  GtkPicture
scales to fit the space it is given and is for content.  Using the wrong one is
why an image sometimes refuses to grow past 16 pixels.
"""

import pathlib
import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gtk

HERE = pathlib.Path(__file__).parent
SAMPLE = HERE / "sample.jpg"


def on_activate(app):
    window = Gtk.ApplicationWindow(application=app, title="Images")
    window.set_default_size(480, 400)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    # An icon from the theme, at a named size.
    icon = Gtk.Image.new_from_icon_name("dialog-information-symbolic")
    icon.set_pixel_size(48)
    box.append(icon)

    if SAMPLE.exists():
        # A texture is decoded once and lives on the GPU; a picture displays it.
        texture = Gdk.Texture.new_from_filename(str(SAMPLE))
        picture = Gtk.Picture.new_for_paintable(texture)
        picture.set_content_fit(Gtk.ContentFit.CONTAIN)
        picture.set_vexpand(True)
        box.append(picture)

        size = f"{texture.get_width()}x{texture.get_height()}"
        box.append(Gtk.Label(label=f"{SAMPLE.name} is {size}"))
    else:
        box.append(Gtk.Label(label=f"No sample image at {SAMPLE}"))

    window.set_child(box)
    window.present()


app = Gtk.Application(application_id="com.example.Images")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
