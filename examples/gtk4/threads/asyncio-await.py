#!/usr/bin/env python3
"""asyncio and GTK on one main loop, with async/await.

PyGObject ships an asyncio event loop that *is* the GLib main loop. Install it
and the two-event-loop problem disappears: there is one loop, GTK drives it,
and `async def` code runs on it. Two consequences worth having:

  * Gio's asynchronous methods become awaitable. Omit the callback argument and
    you get an awaitable back, so `*_async`/`*_finish` callback pairs collapse
    into one `await`.
  * A coroutine runs on the main thread, so it may touch widgets freely. No
    GLib.idle_add, no locking, no marshalling. This is the main reason to
    prefer it over the worker thread in asyncio-bridge.py.

Needs PyGObject 3.50 or later.
"""

import asyncio
import pathlib
import sys

from collections.abc import Coroutine
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib, Gtk

from gi.events import GLibEventLoop

HERE = pathlib.Path(__file__).parent


async def slow_work(seconds: float, fail: bool = False) -> str:
    """Stand-in for an async library call -- httpx, aiohttp, asyncpg."""
    await asyncio.sleep(seconds)
    if fail:
        raise RuntimeError("the server said no")
    return f"waited {seconds}s"


class Window(Adw.ApplicationWindow):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.set_title("async / await")
        self.set_default_size(520, 420)

        # asyncio keeps only a *weak* reference to a running task. Drop your
        # own reference and the task can be garbage collected mid-await, which
        # looks like work that silently never finishes. Hold them, and discard
        # each one when it completes.
        self.tasks: set[asyncio.Task[None]] = set()

        self.status = Gtk.Label(xalign=0, wrap=True)
        self.view = Gtk.TextView(editable=False, monospace=True,
                                 wrap_mode=Gtk.WrapMode.WORD_CHAR)
        scroller = Gtk.ScrolledWindow(vexpand=True)
        scroller.set_child(self.view)

        self.spinner = Adw.Spinner()
        self.spinner.set_visible(False)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        for label, handler in (
            ("Read a file", self.on_read),
            ("List a directory", self.on_list),
            ("Three things at once", self.on_gather),
            ("Something that fails", self.on_fail),
        ):
            button = Gtk.Button(label=label)
            button.connect("clicked", handler)
            box.append(button)

        cancel = Gtk.Button(label="Cancel everything running")
        cancel.connect("clicked", self.on_cancel)
        box.append(cancel)
        box.append(self.spinner)
        box.append(self.status)
        box.append(scroller)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar())
        toolbar.set_content(box)
        self.set_content(toolbar)

    # -- running coroutines -----------------------------------------------------

    def spawn(self, coro: Coroutine[Any, Any, None]) -> asyncio.Task[None]:
        """Start a coroutine and keep it alive until it finishes."""
        task = asyncio.ensure_future(coro)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        task.add_done_callback(lambda _t: self.spinner.set_visible(bool(self.tasks)))
        self.spinner.set_visible(True)
        return task

    def on_cancel(self, _button: Gtk.Button) -> None:
        for task in list(self.tasks):
            task.cancel()

    # -- the coroutines themselves ----------------------------------------------
    #
    # Every one of these sets self.status directly. That is the point: this code
    # runs on the main loop, so a widget assignment here is as safe as one in a
    # clicked handler.

    def on_read(self, _button: Gtk.Button) -> None:
        self.spawn(self.read_file())

    async def read_file(self) -> None:
        self.status.set_text("reading…")
        file = Gio.File.new_for_path(str(HERE / "asyncio-await.py"))
        try:
            # No callback argument, so this returns an awaitable. Compare with
            # gio-async.py, where the same call needs a separate *_finish
            # method in a separate function.
            ok, contents, _etag = await file.load_contents_async()
        except asyncio.CancelledError:
            self.status.set_text("read cancelled")
            raise
        except GLib.Error as error:
            self.status.set_text(f"read failed: {error.message}")
            return

        text = contents.decode("utf-8", "replace") if ok else ""
        self.status.set_text(f"read {len(text)} characters")
        self.view.get_buffer().set_text(text[:2000])

    def on_list(self, _button: Gtk.Button) -> None:
        self.spawn(self.list_directory())

    async def list_directory(self) -> None:
        self.status.set_text("listing…")
        folder = Gio.File.new_for_path(str(HERE))
        try:
            enumerator = await folder.enumerate_children_async(
                "standard::name,standard::size", Gio.FileQueryInfoFlags.NONE,
                GLib.PRIORITY_DEFAULT)
        except GLib.Error as error:
            self.status.set_text(f"listing failed: {error.message}")
            return

        lines = [f"{info.get_size():>9}  {info.get_name()}" for info in enumerator]
        self.status.set_text(f"{len(lines)} entries")
        self.view.get_buffer().set_text("\n".join(sorted(lines)))

    def on_gather(self, _button: Gtk.Button) -> None:
        self.spawn(self.gather())

    async def gather(self) -> None:
        """Concurrency without threads: three waits in the time of the longest.

        asyncio.gather works normally here -- there is a running loop, because
        the running loop is the one GTK is already turning.
        """
        self.status.set_text("three at once…")
        results = await asyncio.gather(slow_work(0.3), slow_work(0.2), slow_work(0.1))
        self.status.set_text(" / ".join(results))

    def on_fail(self, _button: Gtk.Button) -> None:
        self.spawn(self.failing())

    async def failing(self) -> None:
        """Failure is an exception at the point of the await, not an error
        argument in a callback three functions away."""
        self.status.set_text("about to fail…")
        try:
            await slow_work(0.1, fail=True)
        except RuntimeError as error:
            self.status.set_text(f"failed: {error}")


def on_activate(app: Adw.Application) -> None:
    Window(application=app).present()


app = Adw.Application(application_id="com.example.AsyncioAwait")
app.connect("activate", on_activate)

# Wrapping app.run() in the event loop is what makes all of the above work:
# inside this block asyncio's running loop *is* the GLib main context that GTK
# is turning, so coroutines are dispatched between frames like any other main
# loop source.
#
# You will also see this written as asyncio.set_event_loop_policy(
# GLibEventLoopPolicy()), which is what the PyGObject documentation shows and
# what older code does. It works, but event loop policies are deprecated in
# Python 3.14 and removed in 3.16; the context manager is the form that keeps
# working.
with GLibEventLoop(None):
    sys.exit(app.run(sys.argv))
