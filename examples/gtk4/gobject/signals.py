#!/usr/bin/env python3
"""Signals: how one object tells others that something happened.

GTK's own widgets emit signals, and so can yours. A custom signal is the right
tool when a component needs to report something without knowing who is listening
-- which is most of the time, and is what keeps a window from having to hold a
reference to every other window.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject, Gtk


class Download(GObject.Object):
    __gtype_name__ = "Download"

    # The decorator form: the method body is the signal's *default handler*.
    # With no flags it is RUN_FIRST, so it runs BEFORE anything connected with
    # connect(). Pass RUN_LAST if the default should be a fallback instead.
    @GObject.Signal(arg_types=(str,))
    def started(self, url):
        print(f"  [default handler, runs first] started {url}")

    # A signal with no arguments and no default handler.
    finished = GObject.Signal()

    # RUN_LAST puts the default handler after the connected ones, which is what
    # you want when the default is a fallback. The accumulator makes the emission
    # stop at the first handler returning True, whose value becomes the result --
    # so any listener can veto, and with no listeners the default False stands.
    @GObject.Signal(return_type=bool, arg_types=(str,),
                    flags=GObject.SignalFlags.RUN_LAST,
                    accumulator=GObject.signal_accumulator_true_handled)
    def confirm_overwrite(self, filename):
        return False        # nobody objected

    def run(self, url, filename):
        self.emit("started", url)

        if self.emit("confirm_overwrite", filename):
            print(f"  overwrite of {filename} was refused")
            return

        print(f"  writing {filename}")
        self.emit("finished")


def on_activate(app):
    window = Gtk.ApplicationWindow(application=app, title="Signals")
    window.set_default_size(420, 260)

    log = Gtk.Label(xalign=0, wrap=True)
    lines = []

    def note(text):
        lines.append(text)
        log.set_text("\n".join(lines[-8:]))

    download = Download()

    # Ordinary listeners. The first argument is always the emitting object.
    download.connect("started", lambda _d, url: note(f"started {url}"))
    download.connect("finished", lambda _d: note("finished"))

    # A veto handler: returning True stops the emission and becomes the result.
    protect = Gtk.CheckButton(label="Refuse to overwrite important.txt")
    download.connect(
        "confirm-overwrite",
        lambda _d, filename: protect.get_active() and filename == "important.txt",
    )

    # Signal names use hyphens on the C side: "confirm_overwrite" declared in
    # Python is "confirm-overwrite" to connect(). Both spellings are accepted;
    # hyphens are what the documentation uses.

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)
    box.append(protect)

    for filename in ("notes.txt", "important.txt"):
        button = Gtk.Button(label=f"Download {filename}")
        button.connect(
            "clicked",
            lambda _b, f=filename: download.run(f"https://example.com/{f}", f),
        )
        box.append(button)

    # connect() returns a handler id. Keep it if the handler ever has to go away:
    # a handler holding a reference to a widget keeps that widget alive.
    handler = download.connect("finished", lambda _d: note("(temporary listener)"))
    download.disconnect(handler)

    box.append(log)
    window.set_child(box)
    window.present()


app = Gtk.Application(application_id="com.example.Signals")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
