#!/usr/bin/env python3
"""Asynchronous I/O without a thread in sight.

For file and network work, do not start a thread. Gio already has an asynchronous
version of nearly everything, and it is better than a thread: no locking, no
marshalling back to the main loop, and cancellation that actually stops the work
rather than setting a flag the work has to notice.

Every one of these follows the same shape as the dialogs in earlier chapters:
  thing.do_something_async(..., cancellable, callback)
  thing.do_something_finish(result)  ->  raises GLib.Error on failure
"""

import pathlib
import sys
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib, Gtk

HERE = pathlib.Path(__file__).parent


class Window(Adw.ApplicationWindow):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.set_title("Asynchronous I/O")
        self.set_default_size(520, 400)

        # One cancellable per operation. Cancelling it makes the pending
        # *_finish() raise, which is where you handle it.
        self.cancellable = None

        self.status = Gtk.Label(xalign=0, wrap=True)
        self.view = Gtk.TextView(editable=False, monospace=True,
                                 wrap_mode=Gtk.WrapMode.WORD_CHAR)
        scroller = Gtk.ScrolledWindow(vexpand=True)
        scroller.set_child(self.view)

        read = Gtk.Button(label="Read this file asynchronously")
        read.connect("clicked", self.on_read)

        listing = Gtk.Button(label="List this directory asynchronously")
        listing.connect("clicked", self.on_list)

        cancel = Gtk.Button(label="Cancel whatever is running")
        cancel.connect("clicked", self.on_cancel)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        for widget in (read, listing, cancel, self.status, scroller):
            box.append(widget)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar())
        toolbar.set_content(box)
        self.set_content(toolbar)

    def show(self, text: str) -> None:
        self.view.get_buffer().set_text(text)

    def on_cancel(self, _button: Gtk.Button) -> None:
        if self.cancellable is not None:
            self.cancellable.cancel()

    # -- reading a file ---------------------------------------------------------

    def on_read(self, _button: Gtk.Button) -> None:
        self.cancellable = Gio.Cancellable()
        self.status.set_text("reading…")

        file = Gio.File.new_for_path(str(HERE / "gio-async.py"))
        file.load_contents_async(self.cancellable, self.on_read_done)

    def on_read_done(self, file: Gio.File, result: Gio.AsyncResult,
                     _data: object = None) -> None:
        try:
            ok, contents, _etag = file.load_contents_finish(result)
        except GLib.Error as error:
            # A cancelled operation arrives here too, as G_IO_ERROR_CANCELLED.
            if error.matches(Gio.io_error_quark(), Gio.IOErrorEnum.CANCELLED):
                self.status.set_text("read cancelled")
            else:
                self.status.set_text(f"read failed: {error.message}")
            return

        text = contents.decode("utf-8", "replace") if ok else ""
        self.status.set_text(f"read {len(text)} characters from {file.get_basename()}")
        self.show(text[:2000])

    # -- listing a directory ----------------------------------------------------

    def on_list(self, _button: Gtk.Button) -> None:
        self.cancellable = Gio.Cancellable()
        self.status.set_text("listing…")

        folder = Gio.File.new_for_path(str(HERE))
        folder.enumerate_children_async(
            "standard::name,standard::size,standard::type",
            Gio.FileQueryInfoFlags.NONE,
            GLib.PRIORITY_DEFAULT,
            self.cancellable,
            self.on_enumerate_done,
        )

    def on_enumerate_done(self, folder: Gio.File, result: Gio.AsyncResult,
                          _data: object = None) -> None:
        try:
            enumerator = folder.enumerate_children_finish(result)
        except GLib.Error as error:
            self.status.set_text(f"listing failed: {error.message}")
            return
        # Enumerating is itself asynchronous, a batch at a time.
        enumerator.next_files_async(50, GLib.PRIORITY_DEFAULT,
                                    self.cancellable, self.on_files_done)

    def on_files_done(self, enumerator: Gio.FileEnumerator, result: Gio.AsyncResult,
                      _data: object = None) -> None:
        try:
            infos = enumerator.next_files_finish(result)
        except GLib.Error as error:
            self.status.set_text(f"listing failed: {error.message}")
            return

        lines = [f"{info.get_size():>9}  {info.get_name()}" for info in infos]
        self.status.set_text(f"{len(lines)} entries")
        self.show("\n".join(sorted(lines)))


def on_activate(app: Adw.Application) -> None:
    Window(application=app).present()


app = Adw.Application(application_id="com.example.GioAsync")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
