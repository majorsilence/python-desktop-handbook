#!/usr/bin/env python3
"""A real custom container: children wrapped onto as many rows as they need.

Three methods make a widget that lays out children:

  do_measure(orientation, for_size)  how big would you like to be?
  do_size_allocate(w, h, baseline)   here is what you got; place your children
  do_snapshot(snapshot)              draw yourself

GTK asks for a size, gives you one that may be different, and then asks you to
draw. The contract is that do_measure must not lie: a widget that asks for less
than it needs gets clipped, and one that asks for more leaves holes.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Graphene, Gsk, Gtk


class WrapBox(Gtk.Widget):
    """Lays children out left to right, wrapping to a new row when out of width."""

    __gtype_name__ = "WrapBox"

    def __init__(self, spacing=6, **kwargs):
        super().__init__(**kwargs)
        self.spacing = spacing

    # -- adding and removing ----------------------------------------------------
    #
    # GTK 4 has no GtkContainer. A child is added by parenting it to you, and the
    # widget itself keeps the list -- get_first_child()/get_next_sibling().

    def append(self, child):
        child.set_parent(self)

    def remove(self, child):
        child.unparent()

    def children(self):
        child = self.get_first_child()
        while child is not None:
            yield child
            child = child.get_next_sibling()

    def do_dispose(self):
        # Every child must be unparented before the widget is finalised, or GTK
        # prints "Finalizing GtkWidget, but it still has children left".
        child = self.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            child.unparent()
            child = next_child
        Gtk.Widget.do_dispose(self)

    # -- measuring --------------------------------------------------------------

    def do_get_request_mode(self):
        """Our height depends on our width, and GTK has to be told.

        The default is CONSTANT_SIZE, which means "height does not depend on
        width" -- so GTK never bothers passing a real width to do_measure() and
        for_size is always -1. The widget then measures as one row tall however
        narrow it gets, and the bottom rows are clipped away. Nothing warns.
        """
        return Gtk.SizeRequestMode.HEIGHT_FOR_WIDTH

    def do_measure(self, orientation, for_size):
        visible = [c for c in self.children() if c.get_visible()]
        if not visible:
            return 0, 0, -1, -1

        if orientation == Gtk.Orientation.HORIZONTAL:
            # Narrowest we can be is the widest single child; naturally we would
            # like everything on one row.
            widths = [c.measure(orientation, -1)[1] for c in visible]
            minimum = max(widths)
            natural = sum(widths) + self.spacing * (len(visible) - 1)
            return minimum, natural, -1, -1

        # Vertical. for_size is the width we have been offered; -1 means "you
        # decide", in which case measure against our natural width.
        width = for_size
        if width < 0:
            width = self.measure(Gtk.Orientation.HORIZONTAL, -1)[1]
        height = self._layout(visible, width)
        return height, height, -1, -1

    # -- allocating -------------------------------------------------------------

    def do_size_allocate(self, width, height, baseline):
        visible = [c for c in self.children() if c.get_visible()]
        self._layout(visible, width, allocate=True)

    def _layout(self, visible, width, allocate=False):
        """Place children into rows; return the total height needed.

        The same walk both measures and allocates, so the two cannot disagree --
        which is the usual source of layout bugs in a custom container.
        """
        x = y = 0
        row_height = 0
        total = 0

        for child in visible:
            child_width = child.measure(Gtk.Orientation.HORIZONTAL, -1)[1]
            child_height = child.measure(Gtk.Orientation.VERTICAL, child_width)[1]

            if x > 0 and x + child_width > width:
                x = 0
                y += row_height + self.spacing
                row_height = 0

            if allocate:
                # A child is positioned by a transform, not by an x/y pair.
                transform = Gsk.Transform().translate(Graphene.Point().init(x, y))
                child.allocate(child_width, child_height, -1, transform)

            x += child_width + self.spacing
            row_height = max(row_height, child_height)
            total = y + row_height

        return total

    # -- drawing ----------------------------------------------------------------

    def do_snapshot(self, snapshot):
        # A container usually only needs to draw its children. The default
        # implementation does exactly that, so chaining up is enough.
        Gtk.Widget.do_snapshot(self, snapshot)


def on_activate(app):
    window = Adw.ApplicationWindow(application=app, title="Custom container")
    window.set_default_size(460, 320)

    wrap = WrapBox(spacing=8)
    wrap.set_hexpand(True)
    for word in ("gtk", "libadwaita", "pygobject", "cairo", "pango", "gstreamer",
                 "gio", "glib", "gsk", "gdk", "webkit", "meson", "flatpak"):
        button = Gtk.Button(label=word)
        button.connect("clicked", lambda b: print("clicked", b.get_label()))
        wrap.append(button)

    hint = Gtk.Label(
        label="Resize the window: the buttons rewrap.", xalign=0, wrap=True
    )

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)
    box.append(hint)
    box.append(wrap)

    toolbar = Adw.ToolbarView()
    toolbar.add_top_bar(Adw.HeaderBar())
    toolbar.set_content(box)
    window.set_content(toolbar)
    window.present()


app = Adw.Application(application_id="com.example.WrapBox")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
