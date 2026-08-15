#!/usr/bin/env python3
"""Screenshot the examples, so the pictures in the book cannot drift from the code.

A screenshot taken by hand is out of date the first time the example changes and
nobody notices for a year. This runs each example the way ``smoke-test.py`` does,
waits for its window to settle, optionally puts it into a more interesting state,
and renders it to a PNG.

The capture is done from inside GTK -- the window's own GskRenderer is asked to
render the widget to a texture -- so it needs no window manager, no compositor and
no external tool. Under Xvfb that matters: there is no window manager to draw
decorations or to map the window where a screen-grabber could find it.

Usage::

    python3 tools/make-screenshots.py                 # everything in the manifest
    python3 tools/make-screenshots.py hello-world     # just the ones matching

Needs a display; on a headless machine wrap it::

    xvfb-run -a python3 tools/make-screenshots.py
"""

from __future__ import annotations

import argparse
import os
import pathlib
import runpy
import subprocess
import sys
import traceback

REPO = pathlib.Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO / "images" / "screenshots"

# How long to let a window settle before capturing, unless an entry says otherwise.
DEFAULT_SETTLE_MS = 700


# --------------------------------------------------------------------------------
# Preparing a window
#
# A screenshot of an empty form is not worth taking. These run on the example's own
# window, just before the capture, to put something in it. Each takes the window
# and may return a number of extra milliseconds to wait afterwards.
# --------------------------------------------------------------------------------


def find(widget, predicate):
    """Depth-first search of a widget tree. Handy for reaching into an example
    without the example having to expose anything."""
    if widget is None:
        return None
    if predicate(widget):
        return widget
    child = widget.get_first_child()
    while child is not None:
        found = find(child, predicate)
        if found is not None:
            return found
        child = child.get_next_sibling()
    return None


def of_type(type_name):
    return lambda w: type(w).__name__ == type_name


def type_into_entries(window, *values):
    """Fill the first N entries with text."""
    from gi.repository import Gtk

    entries, child = [], window
    def walk(widget):
        c = widget.get_first_child()
        while c is not None:
            if isinstance(c, Gtk.Editable) and not isinstance(c, Gtk.SpinButton):
                entries.append(c)
            walk(c)
            c = c.get_next_sibling()
    walk(window)
    for entry, value in zip(entries, values):
        entry.set_text(value)


def click_buttons(window, *labels):
    """Press named buttons, so the screenshot shows a result rather than a form."""
    from gi.repository import Gtk

    found = []
    def walk(widget):
        c = widget.get_first_child()
        while c is not None:
            if isinstance(c, Gtk.Button) and c.get_label() in labels:
                found.append(c)
            walk(c)
            c = c.get_next_sibling()
    walk(window)
    for button in found:
        button.emit("clicked")


def prepare_composed(window):
    type_into_entries(window, "libadwaita")
    click_buttons(window, "Search")


def prepare_toggles(window):
    from gi.repository import Gtk

    toggle = find(window, of_type("ToggleButton"))
    if toggle is not None:
        toggle.set_active(True)
    switch = find(window, of_type("Switch"))
    if switch is not None:
        switch.set_active(True)


def prepare_entries(window):
    type_into_entries(window, "Ada Lovelace", "hunter2", "note")


def prepare_worker(window):
    click_buttons(window, "Start")
    return 700          # let the progress bar get somewhere


def prepare_greeter(window):
    type_into_entries(window, "Ada")
    click_buttons(window, "Greet", "Begrüßen")


def prepare_css(window):
    click_buttons(window, "Round it")


# --------------------------------------------------------------------------------
# What to shoot
# --------------------------------------------------------------------------------

Manifest = dict[str, dict]

SHOTS: Manifest = {
    "examples/gtk4/hello-world.py": {"out": "hello-world.png"},
    "examples/gtk4/boxes.py": {"out": "boxes.png"},
    "examples/gtk4/adwaita-window.py": {"out": "adwaita-window.png"},
    "examples/gtk4/widgets/buttons.py": {"out": "buttons.png"},
    "examples/gtk4/widgets/toggle-and-check.py": {
        "out": "toggle-and-check.png", "prepare": prepare_toggles,
    },
    "examples/gtk4/widgets/entries.py": {
        "out": "entries.png", "prepare": prepare_entries,
    },
    "examples/gtk4/widgets/numbers-and-choices.py": {"out": "numbers-and-choices.png"},
    "examples/gtk4/widgets/menus.py": {"out": "menus.png"},
    "examples/gtk4/list-view.py": {"out": "list-view.png"},
    "examples/gtk4/column-view.py": {"out": "column-view.png"},
    "examples/gtk4/drag-and-drop.py": {"out": "drag-and-drop.png"},
    "examples/gtk4/images.py": {"out": "images.png"},
    "examples/gtk4/builder/builder-app.py": {"out": "builder-app.png"},
    "examples/gtk4/custom-widgets/composed-widget.py": {
        "out": "composed-widget.png", "prepare": prepare_composed,
    },
    "examples/gtk4/custom-widgets/flow-box-widget.py": {"out": "flow-box-widget.png"},
    "examples/gtk4/cairo/drawing-area.py": {"out": "drawing-area.png"},
    "examples/gtk4/cairo/snapshot-widget.py": {"out": "snapshot-widget.png"},
    "examples/gtk4/animation/transitions.py": {"out": "transitions.png"},
    "examples/gtk4/animation/css-animation.py": {
        "out": "css-animation.png", "prepare": prepare_css, "settle": 1200,
    },
    "examples/gtk4/threads/worker-thread.py": {
        "out": "worker-thread.png", "prepare": prepare_worker,
    },
    "examples/gtk4/desktop/settings.py": {"out": "settings.png"},
    "examples/gtk4/i18n/greeter.py": {
        "out": "greeter.png", "prepare": prepare_greeter,
        "setup": "./update-translations.sh",
    },
    # The same window again in German. greeter.py builds its widgets in Python,
    # so LANGUAGE alone is enough here -- see the chapter for when it is not.
    "examples/gtk4/i18n/greeter.py#de": {
        "source": "examples/gtk4/i18n/greeter.py",
        "out": "greeter-de.png", "prepare": prepare_greeter,
        "setup": "./update-translations.sh",
        "env": {"LANGUAGE": "de"},
    },
    "examples/gtk4/multimedia/video-player.py": {
        "out": "video-player.png", "settle": 1500,
    },
    "examples/gtk4/web/javascript-bridge.py": {
        "out": "javascript-bridge.png", "settle": 2500,
    },
}


# --------------------------------------------------------------------------------
# Capture
# --------------------------------------------------------------------------------


def capture(widget, path) -> str:
    """Render a mapped widget to a PNG using its own renderer."""
    from gi.repository import Graphene, Gtk

    native = widget.get_native()
    if native is None:
        return "the window is not attached to a surface"

    renderer = native.get_renderer()
    if renderer is None:
        return "the surface has no renderer yet"

    width, height = widget.get_width(), widget.get_height()
    if width <= 0 or height <= 0:
        return f"the window has no size yet ({width}x{height})"

    snapshot = Gtk.Snapshot()
    Gtk.WidgetPaintable.new(widget).snapshot(snapshot, width, height)

    node = snapshot.to_node()
    if node is None:
        return "nothing was drawn"

    texture = renderer.render_texture(node, Graphene.Rect().init(0, 0, width, height))
    texture.save_to_png(str(path))
    return ""


def shoot_one(source: str) -> tuple[bool, str]:
    """Run one example, capture its window, and quit it."""
    entry = SHOTS[source]
    path = (REPO / entry.get("source", source)).resolve()
    output = OUTPUT_DIR / entry["out"]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    setup = entry.get("setup")
    if setup is not None:
        done = subprocess.run(setup, shell=True, cwd=path.parent,
                              capture_output=True, text=True)
        if done.returncode != 0:
            return False, f"setup failed: {done.stderr.strip()[-400:]}"

    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import GLib, Gio

    state = {"error": "the application never presented a window"}
    original_run = Gio.Application.run

    def run(self, argv=None):
        def settled():
            window = self.props.active_window
            if window is None:
                state["error"] = "no active window"
                self.quit()
                return GLib.SOURCE_REMOVE

            extra = 0
            prepare = entry.get("prepare")
            if prepare is not None:
                try:
                    extra = prepare(window) or 0
                except Exception:
                    state["error"] = traceback.format_exc()
                    self.quit()
                    return GLib.SOURCE_REMOVE

            def take():
                state["error"] = capture(window, output)
                self.quit()
                return GLib.SOURCE_REMOVE

            # A second pass through the loop, so anything prepare() changed has
            # been laid out and drawn before the shutter opens.
            GLib.timeout_add(max(extra, 120), take)
            return GLib.SOURCE_REMOVE

        GLib.timeout_add(entry.get("settle", DEFAULT_SETTLE_MS), settled)
        GLib.timeout_add_seconds(30, self.quit)      # never hang
        return original_run(self, argv)

    Gio.Application.run = run

    argv, cwd, syspath = sys.argv[:], os.getcwd(), sys.path[:]
    sys.argv = [str(path)]
    sys.path.insert(0, str(path.parent))
    os.chdir(path.parent)
    try:
        runpy.run_path(str(path), run_name="__main__")
    except SystemExit:
        pass
    except Exception:
        return False, traceback.format_exc()
    finally:
        sys.argv, sys.path = argv, syspath
        os.chdir(cwd)

    return (not state["error"]), state["error"]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("patterns", nargs="*",
                        help="only shoot examples whose path contains one of these")
    parser.add_argument("--one", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.one:
        ok, detail = shoot_one(args.one)
        if detail:
            print(detail, file=sys.stderr)
        return 0 if ok else 1

    sources = [s for s in SHOTS
               if not args.patterns or any(p in s for p in args.patterns)]
    if not sources:
        print("nothing matched", file=sys.stderr)
        return 1

    failures = []
    for source in sources:
        environment = dict(os.environ, **SHOTS[source].get("env", {}))
        result = subprocess.run(
            [sys.executable, __file__, "--one", source],
            capture_output=True, text=True, timeout=120, cwd=REPO,
            env=environment,
        )
        target = OUTPUT_DIR / SHOTS[source]["out"]
        if result.returncode == 0 and target.exists():
            print(f"shot  {target.relative_to(REPO)}  ({target.stat().st_size:,} bytes)")
        else:
            failures.append(source)
            print(f"FAIL  {source}")
            for line in (result.stderr or result.stdout).strip().splitlines()[-8:]:
                print(f"      {line}")

    print(f"\n{len(sources) - len(failures)}/{len(sources)} screenshots taken")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
