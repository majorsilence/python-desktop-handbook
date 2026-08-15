#!/usr/bin/env python3
"""Using asyncio libraries from a GTK application.

GTK runs a GLib main loop; asyncio runs its own. They are two event loops and
only one of them can own the main thread, so something has to give.

The approach here needs no extra dependency: run the asyncio loop on a worker
thread for its whole life, submit coroutines to it from the main thread, and
marshal results back with GLib.idle_add. Your async library gets a real asyncio
loop, GTK keeps the main thread, and neither knows about the other.

The alternative is a library that teaches asyncio to run *on* the GLib loop --
gbulb, or asyncio-glib. Those are neater when they work, at the cost of a
dependency whose maintenance you are relying on.
"""

import asyncio
import sys
import threading

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gtk


class AsyncioThread:
    """An asyncio event loop living on its own thread."""

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def submit(self, coro, on_done):
        """Run a coroutine on the asyncio loop; call on_done(result, error)
        back on the GTK main thread."""

        def finished(future):
            try:
                GLib.idle_add(on_done, future.result(), None)
            except Exception as error:               # noqa: BLE001 - reported, not swallowed
                GLib.idle_add(on_done, None, error)

        # run_coroutine_threadsafe is the only asyncio call that is safe to make
        # from another thread.
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        future.add_done_callback(finished)
        return future

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)


async def pretend_to_fetch(name, seconds):
    """Stand-in for an async library call -- httpx, aiohttp, asyncpg."""
    await asyncio.sleep(seconds)
    if name == "broken":
        raise RuntimeError("the server said no")
    return f"{name}: {seconds}s"


async def fetch_several():
    """Concurrency is the reason to do any of this: three requests in the time of
    the slowest, on one thread.

    Note that this is a coroutine wrapping the gather, not a bare
    asyncio.gather(...) call. gather() needs a running loop, and off the asyncio
    thread there is not one -- calling it here would return a future, and
    run_coroutine_threadsafe only accepts a coroutine.
    """
    return await asyncio.gather(
        pretend_to_fetch("a", 0.3),
        pretend_to_fetch("b", 0.2),
        pretend_to_fetch("c", 0.1),
    )


class Window(Adw.ApplicationWindow):
    def __init__(self, runner, **kwargs):
        super().__init__(**kwargs)
        self.runner = runner
        self.set_title("asyncio bridge")
        self.set_default_size(420, 300)

        self.status = Gtk.Label(xalign=0, wrap=True)
        self.lines = []

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.append(Gtk.Spinner(spinning=True))

        for label, name, delay in (
            ("Fetch one", "one", 0.3),
            ("Fetch three at once", "many", 0.0),
            ("Fetch something broken", "broken", 0.1),
        ):
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_fetch, name, delay)
            box.append(button)

        box.append(self.status)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar())
        toolbar.set_content(box)
        self.set_content(toolbar)

    def note(self, text):
        self.lines.append(text)
        self.status.set_text("\n".join(self.lines[-6:]))

    def on_fetch(self, _button, name, delay):
        if name == "many":
            coro = fetch_several()
        else:
            coro = pretend_to_fetch(name, delay)

        self.note(f"started {name}…")
        self.runner.submit(coro, self.on_done)

    def on_done(self, result, error):
        """Back on the GTK main thread, so touching widgets is allowed again."""
        if error is not None:
            self.note(f"failed: {error}")
        else:
            self.note(f"got {result}")
        return GLib.SOURCE_REMOVE


def on_activate(app):
    Window(app.runner, application=app).present()


app = Adw.Application(application_id="com.example.AsyncioBridge")
app.runner = AsyncioThread()
app.connect("activate", on_activate)
app.connect("shutdown", lambda a: a.runner.stop())
sys.exit(app.run(sys.argv))
