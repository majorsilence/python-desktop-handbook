#!/usr/bin/env python3
"""Start each example, let it settle, then shut it down again.

Every listing in this book is a real file under ``examples/``, and the fastest way
for them to rot is for nobody to run them.  This harness runs an example the way a
reader would, but replaces the blocking main loop with one that quits after a short
delay, so a whole directory can be checked in a few seconds.

It catches what matters: import errors, wrong constructor arguments, methods that no
longer exist, signals that no longer exist, and anything that raises while the first
window is being built.  It does not check that the program looks right.

Usage::

    python3 tools/smoke-test.py examples/gtk4                 # every .py below a path
    python3 tools/smoke-test.py examples/gtk4/hello-world.py  # or named files

Needs a display, and a session bus for the examples that own a name on one.
Under CI, or on a headless machine, wrap it::

    dbus-run-session -- xvfb-run -a python3 tools/smoke-test.py examples/gtk4
"""

from __future__ import annotations

import argparse
import os
import pathlib
import runpy
import subprocess
import sys
import traceback

# How long a window is allowed to sit on screen before we close it.
LINGER_MS = 300

# Examples that are batch jobs rather than windows -- a transcode, a pipeline --
# run a bare GLib.MainLoop and finish when the work does, so they cannot be cut
# short after LINGER_MS. This is the safety net that stops a stalled one hanging
# the whole run, not the normal path: an example that hits it has failed.
WATCHDOG_SECONDS = int(os.environ.get("SMOKE_TEST_WATCHDOG", "120"))

# The in-process watchdog should always fire first, so that a hang is reported
# against the example that hung rather than killing the harness.
SUBPROCESS_TIMEOUT = WATCHDOG_SECONDS + 60

SKIP_MARKER = "smoke-test: skip"
WATCHDOG_MARKER = "smoke-test: watchdog fired"


def patch_gtk() -> bool:
    """Make Gtk/Gio Application.run() quit shortly after it starts."""
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        from gi.repository import GLib, Gio
    except (ImportError, ValueError):
        return False

    original = Gio.Application.run

    def run(self, argv=None):
        def stop():
            self.quit()
            return GLib.SOURCE_REMOVE

        GLib.timeout_add(LINGER_MS, stop)
        return original(self, argv)

    Gio.Application.run = run
    return True


def patch_main_loop() -> bool:
    """Put a watchdog on any bare GLib.MainLoop, so a stall fails instead of hangs."""
    try:
        from gi.repository import GLib
    except ImportError:
        return False

    original = GLib.MainLoop.run

    def run(self):
        def give_up():
            print(f"{WATCHDOG_MARKER} after {WATCHDOG_SECONDS}s", file=sys.stderr)
            self.quit()
            return GLib.SOURCE_REMOVE

        GLib.timeout_add_seconds(WATCHDOG_SECONDS, give_up)
        return original(self)

    GLib.MainLoop.run = run
    return True


def patch_qt() -> bool:
    """Make QApplication.exec() quit shortly after it starts."""
    try:
        from PySide6.QtCore import QCoreApplication, QTimer
    except ImportError:
        return False

    original = QCoreApplication.exec

    def exec_(self=None):
        app = self if self is not None else QCoreApplication.instance()
        QTimer.singleShot(LINGER_MS, app.quit)
        return original(app)

    QCoreApplication.exec = exec_
    QCoreApplication.exec_ = exec_
    return True


def run_one(path: pathlib.Path) -> tuple[bool, str]:
    # Examples are run from their own directory so relative data files resolve;
    # that means the script path itself has to stop being relative first.
    path = path.resolve()
    source = path.read_text(encoding="utf-8", errors="replace")
    if SKIP_MARKER in source:
        return True, "skipped on request"

    patch_gtk()
    patch_main_loop()
    patch_qt()

    argv, cwd, path_ = sys.argv[:], os.getcwd(), sys.path[:]
    sys.argv = [str(path)]
    # `python3 example.py` puts the script's directory on sys.path; runpy does not,
    # so examples that import a helper beside them would fail here but not for a reader.
    sys.path.insert(0, str(path.parent))
    os.chdir(path.parent)
    try:
        runpy.run_path(str(path), run_name="__main__")
        return True, ""
    except SystemExit as exit_:
        code = exit_.code
        if code in (None, 0):
            return True, ""
        return False, f"exited with status {code}"
    except Exception:
        return False, traceback.format_exc()
    finally:
        sys.argv, sys.path = argv, path_
        os.chdir(cwd)


def collect(targets: list[str]) -> list[pathlib.Path]:
    found: list[pathlib.Path] = []
    for target in targets:
        path = pathlib.Path(target)
        if path.is_dir():
            found.extend(sorted(path.rglob("*.py")))
        else:
            found.append(path)
    return found


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("targets", nargs="+", help="example files or directories")
    parser.add_argument("--one", action="store_true",
                        help=argparse.SUPPRESS)  # internal: run a single file in-process
    args = parser.parse_args(argv)

    if args.one:
        ok, detail = run_one(pathlib.Path(args.targets[0]))
        if detail:
            print(detail, file=sys.stderr)
        return 0 if ok else 1

    # Each example gets its own interpreter: they install signal handlers, create
    # singleton applications and generally do not expect to share a process.
    failures = []
    paths = collect(args.targets)
    for path in paths:
        try:
            result = subprocess.run(
                [sys.executable, __file__, "--one", str(path)],
                capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            # The in-process watchdog should have caught this. Report it against
            # the example and keep going -- one hang must not lose every result
            # after it.
            failures.append(path)
            print(f"FAIL  {path}  (no output for {SUBPROCESS_TIMEOUT}s; killed)")
            continue

        # An exception raised inside a GTK signal handler is printed and swallowed:
        # the process still exits 0. Treat any traceback on stderr as a failure,
        # and likewise an example that only finished because the watchdog fired.
        crashed = "Traceback (most recent call last)" in result.stderr
        stalled = WATCHDOG_MARKER in result.stderr

        if result.returncode == 0 and not crashed and not stalled:
            print(f"PASS  {path}")
        else:
            failures.append(path)
            reason = ("  (exception in a callback)" if crashed else
                      f"  (still running after {WATCHDOG_SECONDS}s)" if stalled else "")
            print(f"FAIL  {path}{reason}")
            for line in (result.stderr or result.stdout).strip().splitlines()[-12:]:
                print(f"      {line}")

    print(f"\n{len(paths) - len(failures)}/{len(paths)} examples started cleanly")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
