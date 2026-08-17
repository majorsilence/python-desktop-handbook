#!/usr/bin/env python3
"""The logic half of the example application: a list of tasks, and no widgets.

Nothing in this file imports Gtk. That is the point, and it is the single
decision that makes an application testable: rules live somewhere a test can
reach without opening a window.

It is still GObject, because the interface layer wants properties to bind to and
signals to listen for -- so the tests here are also testing that the properties
notify when they should, which is a real bug you can otherwise only find by
watching a label fail to update.
"""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GObject


class Task(GObject.Object):
    __gtype_name__ = "Task"

    title = GObject.Property(type=str, default="")
    done = GObject.Property(type=bool, default=False)

    def __init__(self, title: str) -> None:
        super().__init__()
        self.title = title


class TaskList(GObject.Object):
    """A Gio.ListStore of tasks, plus the rules about what may go in it."""

    __gtype_name__ = "TaskList"

    def __init__(self) -> None:
        super().__init__()
        self.store = Gio.ListStore.new(Task)

    @GObject.Property(type=int, default=0)
    def remaining(self) -> int:
        """How many tasks are not done.

        A computed property. The trap it exists to demonstrate: nothing notifies
        it automatically, so every method that could change the answer has to say
        so. Forget one and a bound label silently stops updating -- which looks
        like a display bug and is actually this.
        """
        return sum(1 for task in self.store if not task.done)

    def add(self, title: str) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("a task needs a title")
        if any(task.title == title for task in self.store):
            raise ValueError(f"{title!r} is already on the list")

        task = Task(title)
        # Toggling a task changes the answer to `remaining`, and the task itself
        # cannot know that, so the list watches its own children.
        task.connect("notify::done", lambda *_: self.notify("remaining"))
        self.store.append(task)
        self.notify("remaining")
        return task

    def remove(self, task: Task) -> None:
        found, position = self.store.find(task)
        if not found:
            raise LookupError("that task is not on this list")
        self.store.remove(position)
        self.notify("remaining")

    def clear_done(self) -> int:
        """Remove every finished task. Returns how many went."""
        doomed = [task for task in self.store if task.done]
        for task in doomed:
            found, position = self.store.find(task)
            if found:
                self.store.remove(position)
        if doomed:
            self.notify("remaining")
        return len(doomed)

    def titles(self) -> list[str]:
        return [task.title for task in self.store]
