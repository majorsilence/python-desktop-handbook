#!/usr/bin/env python3
"""Slow work on a thread, with progress and cancellation.

The rule that governs this whole chapter: GTK is not thread-safe, and widgets
belong to the main thread. A worker thread may compute, read, parse and download
as much as it likes; when it wants to change something on screen it hands the job
back to the main loop with GLib.idle_add.

There is no threads_enter/threads_leave any more. There is no lock you can take.
GLib.idle_add is the entire interface between a worker and the interface.
"""

import sys
import threading
import time
from typing import Any

from collections.abc import Callable
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gtk

STEPS = 40


def slow_work(cancel: threading.Event,
              report: Callable[[int, int], None]) -> int | None:
    """Runs on a worker thread. Touches no widgets, only `report`."""
    total = 0
    for step in range(STEPS):
        if cancel.is_set():
            return None                 # asked to stop; drop everything
        time.sleep(0.05)                # stand-in for real work
        total += step
        report(step + 1, STEPS)
    return total


class Window(Adw.ApplicationWindow):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.set_title("Worker thread")
        self.set_default_size(420, 260)

        self.thread = None
        self.cancel = None

        self.progress = Gtk.ProgressBar(show_text=True, text="idle")
        self.status = Gtk.Label(xalign=0, wrap=True)

        self.start_button = Gtk.Button(label="Start")
        self.start_button.add_css_class("suggested-action")
        self.start_button.connect("clicked", self.on_start)

        self.stop_button = Gtk.Button(label="Cancel", sensitive=False)
        self.stop_button.connect("clicked", self.on_cancel)

        # A spinner is a good check that the main loop is still running: if it
        # stops, something is blocking the main thread.
        self.spinner = Gtk.Spinner(spinning=True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        for widget in (self.spinner, self.progress, self.start_button,
                       self.stop_button, self.status):
            box.append(widget)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar())
        toolbar.set_content(box)
        self.set_content(toolbar)

    # -- main thread ------------------------------------------------------------

    def on_start(self, _button: Gtk.Button) -> None:
        if self.thread is not None:
            return

        self.cancel = threading.Event()
        self.start_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)
        self.status.set_text("working…")

        # daemon=True so a half-finished worker cannot keep the process alive.
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def on_cancel(self, _button: Gtk.Button) -> None:
        if self.cancel is not None:
            self.cancel.set()
            self.status.set_text("cancelling…")

    # -- worker thread ----------------------------------------------------------

    def run(self) -> None:
        """Everything in here is off the main thread. No widget access."""
        result = slow_work(self.cancel, self.report_progress)

        # Hand the result back. idle_add is safe to call from any thread, and the
        # callback runs on the main thread.
        GLib.idle_add(self.on_finished, result)

    def report_progress(self, done: int, total: int) -> None:
        GLib.idle_add(self.on_progress, done, total)

    # -- main thread again, via idle_add ----------------------------------------

    def on_progress(self, done: int, total: int) -> bool:
        self.progress.set_fraction(done / total)
        self.progress.set_text(f"{done} of {total}")
        return GLib.SOURCE_REMOVE       # run once, not every idle

    def on_finished(self, result: int | None) -> bool:
        self.thread = None
        self.cancel = None
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)

        if result is None:
            self.status.set_text("cancelled")
            self.progress.set_fraction(0)
            self.progress.set_text("idle")
        else:
            self.status.set_text(f"finished: {result}")
        return GLib.SOURCE_REMOVE


def on_activate(app: Adw.Application) -> None:
    Window(application=app).present()


app = Adw.Application(application_id="com.example.WorkerThread")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
