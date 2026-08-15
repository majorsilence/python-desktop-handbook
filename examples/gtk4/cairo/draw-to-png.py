#!/usr/bin/env python3
"""Cairo on its own: draw to an image surface and write a PNG.

No GTK involved. A surface is what you draw on, a context is what you draw with.
"""

import cairo

WIDTH, HEIGHT = 400, 300

# ARGB32 is the usual choice: 8 bits each of alpha, red, green and blue.
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
context = cairo.Context(surface)

# Fill the background. set_source_rgb takes 0..1, not 0..255.
context.set_source_rgb(1, 1, 1)
context.paint()

context.set_line_width(15)
context.set_line_cap(cairo.LINE_CAP_ROUND)

context.set_source_rgb(0.2, 0.3, 0.7)
context.move_to(50, 50)
context.line_to(350, 100)
context.stroke()

context.set_source_rgb(0.8, 0.3, 0.2)
context.move_to(50, 150)
context.line_to(350, 250)
context.stroke()

surface.write_to_png("draw-to-png.png")
print("wrote draw-to-png.png")
