#!/usr/bin/env python3
"""What antialiasing does, and what turning it off costs.

Antialiasing softens the stair-stepping you get when a curve is approximated by
square pixels. It is on by default and you almost never want it off; the one real
use is drawing something that must be pixel-exact.
"""

import math

import cairo

WIDTH, HEIGHT = 420, 220

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
cr = cairo.Context(surface)
cr.set_source_rgb(1, 1, 1)
cr.paint()

cr.select_font_face("sans-serif")
cr.set_font_size(13)

for index, (mode, name) in enumerate((
    (cairo.ANTIALIAS_DEFAULT, "ANTIALIAS_DEFAULT"),
    (cairo.ANTIALIAS_NONE, "ANTIALIAS_NONE"),
)):
    x = 110 + index * 200

    cr.set_antialias(mode)
    cr.set_source_rgb(0.2, 0.4, 0.8)
    cr.arc(x, 100, 60, 0, 2 * math.pi)
    cr.fill()

    cr.set_line_width(3)
    cr.set_source_rgb(0.8, 0.3, 0.2)
    cr.move_to(x - 70, 170)
    cr.line_to(x + 70, 140)
    cr.stroke()

    # The label itself is drawn with antialiasing back on, so both stay readable.
    cr.set_antialias(cairo.ANTIALIAS_DEFAULT)
    cr.set_source_rgb(0.3, 0.3, 0.3)
    extents = cr.text_extents(name)
    cr.move_to(x - extents.width / 2, 205)
    cr.show_text(name)

surface.write_to_png("antialias.png")
print("wrote antialias.png")
