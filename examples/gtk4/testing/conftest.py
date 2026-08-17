"""Fixtures shared by the tests beside it.

smoke-test: skip -- this is pytest's, not a program to run.
"""

import pathlib
import sys

import pytest

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gtk

# The example is a directory of plain modules rather than an installed package,
# so put it on the path the way running app.py would.
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from tasklist import TaskList  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def gtk_initialised() -> None:
    """Initialise GTK once for the whole session.

    Gtk.init() is not optional before building a widget, and it is not safe to
    call per test -- so it is session-scoped and automatic. It needs a display;
    see the chapter for how to give it one in CI.
    """
    Adw.init()


@pytest.fixture
def tasks() -> TaskList:
    return TaskList()


@pytest.fixture
def pump() -> object:
    """Run the main loop until it has nothing left to do.

    Tests do not call app.run(), so nothing turns the main loop and anything
    deferred to an idle callback never happens. This turns it by hand, and the
    iteration count is a guard: a test that would otherwise hang fails instead.
    """

    def run(iterations: int = 200) -> int:
        context = GLib.MainContext.default()
        turned = 0
        while context.pending() and turned < iterations:
            context.iteration(False)
            turned += 1
        return turned

    return run
