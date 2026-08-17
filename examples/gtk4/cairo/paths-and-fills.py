#!/usr/bin/env python3
"""Paths, strokes, fills, gradients and transformations.

Everything Cairo draws is a path. You build one with move_to/line_to/curve_to/arc,
then either stroke it (draw the outline) or fill it (colour the inside). Both
consume the path unless you use the _preserve variants.
"""

import math

import cairo

WIDTH, HEIGHT = 640, 480

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
cr = cairo.Context(surface)

cr.set_source_rgb(1, 1, 1)
cr.paint()


def panel(x: float, y: float, title: str) -> None:
    """Move the origin to a cell of a 2x2 grid and label it."""
    cr.save()                    # push the current transform and state
    cr.translate(x, y)
    cr.set_source_rgb(0.4, 0.4, 0.4)
    cr.select_font_face("sans-serif")
    cr.set_font_size(13)
    cr.move_to(0, -8)
    cr.show_text(title)


def end_panel() -> None:
    cr.restore()                 # pop it again


# --- lines and joins -----------------------------------------------------------
panel(40, 40, "Lines: caps and joins")
cr.set_line_width(12)
for i, cap in enumerate((cairo.LINE_CAP_BUTT, cairo.LINE_CAP_ROUND,
                         cairo.LINE_CAP_SQUARE)):
    cr.set_line_cap(cap)
    cr.set_source_rgb(0.2, 0.3, 0.7)
    cr.move_to(0, 20 + i * 30)
    cr.line_to(180, 20 + i * 30)
    cr.stroke()

cr.set_line_join(cairo.LINE_JOIN_ROUND)
cr.set_source_rgb(0.8, 0.4, 0.1)
cr.move_to(0, 130)
cr.line_to(60, 170)
cr.line_to(120, 130)
cr.line_to(180, 170)
cr.stroke()
end_panel()

# --- curves and arcs -----------------------------------------------------------
panel(360, 40, "Curves and arcs")
cr.set_line_width(4)
cr.set_source_rgb(0.1, 0.5, 0.3)
cr.move_to(0, 60)
# curve_to takes two control points and an end point.
cr.curve_to(60, 0, 120, 120, 180, 60)
cr.stroke()

# arc goes clockwise; arc_negative goes the other way. Angles are radians, and
# zero points right, not up.
cr.set_source_rgb(0.7, 0.2, 0.4)
cr.arc(60, 140, 40, 0, math.radians(270))
cr.stroke()

# The same sweep the other way round, closed into a wedge.
cr.arc_negative(150, 140, 30, math.radians(300), math.radians(60))
cr.close_path()                  # back to where the path started
cr.stroke()
end_panel()

# --- fills, and the difference the rule makes ---------------------------------
panel(40, 280, "Fill rules")
cr.set_source_rgb(0.3, 0.4, 0.9)
cr.arc(60, 60, 50, 0, 2 * math.pi)
cr.new_sub_path()                # or the next arc joins on with a straight line
cr.arc(60, 60, 25, 0, 2 * math.pi)
cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
cr.fill()                        # the inner circle is punched out

cr.set_source_rgb(0.9, 0.5, 0.2)
cr.arc(200, 60, 50, 0, 2 * math.pi)
cr.new_sub_path()
cr.arc(200, 60, 25, 0, 2 * math.pi)
cr.set_fill_rule(cairo.FILL_RULE_WINDING)
cr.fill()                        # ...and here it is not
end_panel()

# --- gradients and transforms --------------------------------------------------
panel(360, 280, "Gradients and transforms")
gradient = cairo.LinearGradient(0, 0, 180, 0)
gradient.add_color_stop_rgb(0.0, 0.9, 0.3, 0.2)
gradient.add_color_stop_rgb(1.0, 0.2, 0.3, 0.9)
cr.set_source(gradient)
cr.rectangle(0, 0, 180, 50)
cr.fill()

radial = cairo.RadialGradient(60, 130, 5, 60, 130, 45)
radial.add_color_stop_rgba(0, 1, 1, 1, 1)
radial.add_color_stop_rgba(1, 0.2, 0.4, 0.8, 0)
cr.set_source(radial)
cr.arc(60, 130, 45, 0, 2 * math.pi)
cr.fill()

cr.save()
cr.translate(150, 130)
cr.rotate(math.radians(20))
cr.set_source_rgba(0.1, 0.6, 0.4, 0.8)
cr.rectangle(-30, -30, 60, 60)
cr.fill()
cr.restore()
end_panel()

surface.write_to_png("paths-and-fills.png")
print("wrote paths-and-fills.png")
