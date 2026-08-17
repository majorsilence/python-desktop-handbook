#!/usr/bin/env python3
"""The same drawing, sent to four different surfaces.

Cairo draws the same way whatever it is drawing onto. Only the surface changes,
which is why the printing chapter can reuse code written for the screen.
"""

import cairo

WIDTH, HEIGHT = 300, 200


def draw(context: cairo.Context) -> None:
    context.set_source_rgb(1, 1, 1)
    context.paint()

    context.set_source_rgb(0.1, 0.5, 0.3)
    context.rectangle(40, 40, 220, 120)
    context.fill_preserve()      # fill, but keep the path

    context.set_source_rgb(0, 0, 0)
    context.set_line_width(4)
    context.stroke()             # ...so it can be stroked too


# A raster image, in memory.
png = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
draw(cairo.Context(png))
png.write_to_png("surfaces.png")

# Vector output. Sizes here are in points, not pixels: 72 points to the inch.
for surface, name in (
    (cairo.PDFSurface("surfaces.pdf", WIDTH, HEIGHT), "surfaces.pdf"),
    (cairo.SVGSurface("surfaces.svg", WIDTH, HEIGHT), "surfaces.svg"),
    (cairo.PSSurface("surfaces.ps", WIDTH, HEIGHT), "surfaces.ps"),
):
    draw(cairo.Context(surface))
    surface.finish()             # flush and close the file
    print("wrote", name)

print("wrote surfaces.png")
