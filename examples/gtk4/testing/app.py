#!/usr/bin/env python3
"""The application, which is the third and smallest piece.

Splitting it out is not ceremony. A test wants to build a Window without an
Adw.Application wrapped around it, and an application that constructs its own
window inside its own activate handler makes that awkward. Keep the entry point
to the part that is genuinely about being a program.

    python3 app.py                    # run it
    pytest                            # test it
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw

from tasklist import TaskList
from window import Window

STARTING_TASKS = ["Write the tests", "Run the tests", "Fix the tests"]


def build_task_list() -> TaskList:
    tasks = TaskList()
    for title in STARTING_TASKS:
        tasks.add(title)
    return tasks


def on_activate(app: Adw.Application) -> None:
    Window(tasks=build_task_list(), application=app).present()


def main() -> int:
    app = Adw.Application(application_id="com.example.Tasks")
    app.connect("activate", on_activate)
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
