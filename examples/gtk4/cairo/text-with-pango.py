#!/usr/bin/env python3
"""Text on a Cairo surface, the way an application should do it.

Cairo has show_text(), and it is documented as a "toy" API: no line breaking, no
bidirectional text, no shaping, one font at a time. Pango does all of that, and
PangoCairo renders a Pango layout onto a Cairo context.
"""

import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")

import cairo
from gi.repository import Pango, PangoCairo

WIDTH, HEIGHT = 520, 260

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
cr = cairo.Context(surface)
cr.set_source_rgb(1, 1, 1)
cr.paint()

# --- Cairo's own text API: fine for a label on a chart -------------------------
cr.set_source_rgb(0.4, 0.4, 0.4)
cr.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
cr.set_font_size(13)
cr.move_to(20, 30)
cr.show_text("cairo show_text: one line, one font, no wrapping")

# Measuring, so you can centre or right-align.
text = "centred"
extents = cr.text_extents(text)
cr.move_to(WIDTH / 2 - extents.width / 2, 55)
cr.show_text(text)

# --- Pango: everything else ----------------------------------------------------
layout = PangoCairo.create_layout(cr)
layout.set_width(480 * Pango.SCALE)      # Pango works in 1/1024ths of a point
layout.set_wrap(Pango.WrapMode.WORD)
layout.set_justify(True)
layout.set_font_description(Pango.FontDescription("Serif 11"))
layout.set_markup(
    "<b>Pango</b> wraps text to a width, understands <i>markup</i>, and lays out "
    "scripts that Cairo's own text API cannot: Arabic, Devanagari, anything that "
    "needs shaping or a right-to-left run. It also measures what it drew, so you "
    "can place the next thing under it."
)

cr.set_source_rgb(0.1, 0.1, 0.1)
cr.move_to(20, 80)
PangoCairo.show_layout(cr, layout)

# get_pixel_size() reports the space the layout actually took.
_, height = layout.get_pixel_size()

cr.move_to(20, 80 + height + 12)
under = PangoCairo.create_layout(cr)
under.set_font_description(Pango.FontDescription("Monospace 10"))
under.set_text(f"the paragraph above is {height} pixels tall", -1)
cr.set_source_rgb(0.5, 0.2, 0.2)
PangoCairo.show_layout(cr, under)

surface.write_to_png("text-with-pango.png")
print("wrote text-with-pango.png")
