#!/usr/bin/env python3
"""Printing without a printer: export straight to PDF.

GtkPrintOperation drives the whole job -- it asks how many pages there are, then
asks you to draw each one onto a Cairo context. Sending the result to a file
instead of a printer changes one enum, which makes this the easiest way to
develop and test printing code.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
# get_cairo_context() needs PyGObject's cairo support (python3-gi-cairo on
# Debian). Without it the failure happens inside the draw handler, not here.
gi.require_foreign("cairo")
from gi.repository import Gtk, Pango, PangoCairo

PAGES = 3

BODY = (
    "The print context measures in points by default, and it has already "
    "subtracted the margins, so the width and height you are given are the "
    "printable area. Drawing at (0, 0) puts you at the top left of that area "
    "rather than at the corner of the paper."
)


def on_draw_page(_operation: Gtk.PrintOperation, context: Gtk.PrintContext,
                 page_number: int) -> None:
    """Draw one page. Called once per page, in order."""
    cr = context.get_cairo_context()
    width = context.get_width()
    height = context.get_height()

    cr.set_source_rgb(0, 0, 0)

    # create_pango_layout() gives a layout already set to the printer's resolution.
    title = context.create_pango_layout()
    title.set_font_description(Pango.FontDescription("Sans Bold 14"))
    title.set_text(f"Quarterly report — page {page_number + 1}", -1)
    cr.move_to(0, 0)
    PangoCairo.show_layout(cr, title)

    _, title_height = title.get_pixel_size()
    cr.set_line_width(0.75)
    cr.move_to(0, title_height + 6)
    cr.line_to(width, title_height + 6)
    cr.stroke()

    body = context.create_pango_layout()
    body.set_font_description(Pango.FontDescription("Serif 11"))
    body.set_width(int(width * Pango.SCALE))     # wrap to the printable width
    body.set_wrap(Pango.WrapMode.WORD)
    body.set_text(BODY, -1)
    cr.move_to(0, title_height + 20)
    PangoCairo.show_layout(cr, body)

    # A footer, positioned from the bottom of the page.
    footer = context.create_pango_layout()
    footer.set_font_description(Pango.FontDescription("Sans 8"))
    footer.set_text(f"{page_number + 1} of {PAGES}", -1)
    _, footer_height = footer.get_pixel_size()
    cr.move_to(0, height - footer_height)
    PangoCairo.show_layout(cr, footer)


operation = Gtk.PrintOperation()
operation.set_n_pages(PAGES)
operation.set_job_name("print-to-pdf example")
operation.set_unit(Gtk.Unit.POINTS)
operation.set_export_filename("print-to-pdf.pdf")
operation.connect("draw-page", on_draw_page)

result = operation.run(Gtk.PrintOperationAction.EXPORT, None)
if result == Gtk.PrintOperationResult.ERROR:
    raise SystemExit("the print job failed")
print("wrote print-to-pdf.pdf")
