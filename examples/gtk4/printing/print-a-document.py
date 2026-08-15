#!/usr/bin/env python3
"""A real print job: paginate some text, then print, preview or export it.

The page count is not known until the paper size is: it depends on how many lines
fit. That is what begin-print is for -- it runs after the user has chosen a
printer and a page setup, and it is where you work out how long the document is.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
# get_cairo_context() needs PyGObject's cairo support (python3-gi-cairo on
# Debian). Without it the failure happens inside the draw handler, not here.
gi.require_foreign("cairo")
from gi.repository import Gtk, Pango, PangoCairo

TEXT = (
    """A print job in GTK runs in three acts.

First begin-print: the printer and the page setup are settled, so the print
context can tell you how wide and how tall a page is. Measure the document
against that and call set_n_pages().

Then draw-page, once for each page, in order. You are handed the same kind of
Cairo context the screen chapter used, already translated so that (0, 0) is the
top left of the printable area and already scaled so that one unit is whatever
unit you asked for.

Finally end-print, where you let go of whatever begin-print set up.

The pagination below is deliberately simple: fixed line height, count the lines
that fit, slice the text. Real documents need to measure each paragraph, keep
headings with the text under them, and avoid leaving one line of a paragraph
alone at the bottom of a page. None of that changes the shape of the job.

Because the same code draws to a printer, to a preview and to a PDF, the
quickest way to develop it is to export a PDF and look at the file. Nothing
about the drawing changes when a real printer is involved.
""" * 3
).splitlines()

FONT = Pango.FontDescription("Serif 11")
HEADER_FONT = Pango.FontDescription("Sans Bold 10")


class Document:
    def __init__(self):
        self.lines_per_page = 0
        self.line_height = 0

    def on_begin_print(self, operation, context):
        """Work out how many pages there are, now that the paper size is known."""
        layout = context.create_pango_layout()
        layout.set_font_description(FONT)
        layout.set_text("Ag", -1)
        _, self.line_height = layout.get_pixel_size()

        usable = context.get_height() - self.line_height * 3   # header and footer
        self.lines_per_page = max(1, int(usable // self.line_height))

        pages = -(-len(TEXT) // self.lines_per_page)           # ceiling division
        operation.set_n_pages(pages)

    def on_draw_page(self, operation, context, page_number):
        cr = context.get_cairo_context()
        width = context.get_width()
        height = context.get_height()
        cr.set_source_rgb(0, 0, 0)

        header = context.create_pango_layout()
        header.set_font_description(HEADER_FONT)
        header.set_width(int(width * Pango.SCALE))
        header.set_text("How printing works", -1)
        cr.move_to(0, 0)
        PangoCairo.show_layout(cr, header)

        cr.set_line_width(0.5)
        cr.move_to(0, self.line_height * 1.4)
        cr.line_to(width, self.line_height * 1.4)
        cr.stroke()

        start = page_number * self.lines_per_page
        body = context.create_pango_layout()
        body.set_font_description(FONT)
        body.set_width(int(width * Pango.SCALE))
        body.set_text("\n".join(TEXT[start:start + self.lines_per_page]), -1)
        cr.move_to(0, self.line_height * 2)
        PangoCairo.show_layout(cr, body)

        footer = context.create_pango_layout()
        footer.set_font_description(HEADER_FONT)
        footer.set_width(int(width * Pango.SCALE))
        footer.set_alignment(Pango.Alignment.CENTER)
        footer.set_text(f"{page_number + 1} of {operation.get_property('n-pages')}", -1)
        cr.move_to(0, height - self.line_height)
        PangoCairo.show_layout(cr, footer)

    def on_end_print(self, _operation, _context):
        self.lines_per_page = 0


class PrintWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Printing")
        self.set_default_size(380, 220)

        # Settings and page setup are kept between jobs so the second print
        # remembers what the first one chose.
        self.settings = Gtk.PrintSettings()
        self.page_setup = Gtk.PageSetup()

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        for label, action in (
            ("Page setup…", self.on_page_setup),
            ("Print…", lambda _b: self.run(Gtk.PrintOperationAction.PRINT_DIALOG)),
            ("Preview", lambda _b: self.run(Gtk.PrintOperationAction.PREVIEW)),
            ("Export a PDF", lambda _b: self.run(Gtk.PrintOperationAction.EXPORT)),
        ):
            button = Gtk.Button(label=label)
            button.connect("clicked", action)
            box.append(button)

        self.status = Gtk.Label(label="")
        box.append(self.status)
        self.set_child(box)

    def on_page_setup(self, _button):
        # Blocks until the dialog is answered, and hands back a new page setup.
        self.page_setup = Gtk.print_run_page_setup_dialog(
            self, self.page_setup, self.settings
        )
        paper = self.page_setup.get_paper_size()
        self.status.set_text(f"Paper: {paper.get_display_name()}")

    def run(self, action):
        document = Document()

        operation = Gtk.PrintOperation()
        operation.set_job_name("How printing works")
        operation.set_unit(Gtk.Unit.POINTS)
        operation.set_print_settings(self.settings)
        operation.set_default_page_setup(self.page_setup)
        operation.set_embed_page_setup(True)
        operation.set_export_filename("print-a-document.pdf")

        operation.connect("begin-print", document.on_begin_print)
        operation.connect("draw-page", document.on_draw_page)
        operation.connect("end-print", document.on_end_print)

        result = operation.run(action, self)

        if result == Gtk.PrintOperationResult.ERROR:
            self.status.set_text("The print job failed.")
        elif result == Gtk.PrintOperationResult.APPLY:
            # Keep what the user chose for next time.
            self.settings = operation.get_print_settings()
            self.status.set_text("Printed.")
        else:
            self.status.set_text("Cancelled.")


def on_activate(app):
    PrintWindow(application=app).present()


app = Gtk.Application(application_id="com.example.Printing")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
