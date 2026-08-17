"""Tests for the interface. These need a display.

smoke-test: skip -- this is pytest's, not a program to run.

Widget tests are worth fewer than the ones in test_tasklist.py and cost more to
write, so test the wiring rather than the rules: that a handler reaches the
model, that a binding is connected, that an error is reported somewhere. The
rules themselves are already covered next door.
"""

from tasklist import TaskList
from window import Window


def test_typing_and_activating_adds_a_task() -> None:
    tasks = TaskList()
    window = Window(tasks=tasks)

    window.entry.set_text("Write the tests")
    # Emitting the signal is how you press Enter without an input device. It runs
    # the same handler a keypress would, synchronously.
    window.entry.emit("activate")

    assert tasks.titles() == ["Write the tests"]
    assert window.entry.get_text() == "", "the entry should clear after adding"


def test_a_rejected_task_is_reported_and_not_added() -> None:
    tasks = TaskList()
    window = Window(tasks=tasks)
    tasks.add("Write the tests")

    window.entry.set_text("Write the tests")
    window.entry.emit("activate")

    assert len(tasks.titles()) == 1
    assert "already on the list" in window.status.get_text()
    assert window.entry.get_text() == "Write the tests", \
        "a refused entry should keep its text so the user can fix it"


def test_the_status_label_follows_the_model() -> None:
    tasks = TaskList()
    window = Window(tasks=tasks)
    assert window.status.get_text() == "Nothing left."

    first = tasks.add("one")
    tasks.add("two")
    assert window.status.get_text() == "2 left"

    # This is the assertion that fails if TaskList forgets to notify. The label
    # is only ever updated from notify::remaining, so the test is really asking
    # whether the signal arrived.
    first.done = True
    assert window.status.get_text() == "1 left"


def test_rows_are_built_for_each_task(pump: object) -> None:
    tasks = TaskList()
    for title in ("one", "two", "three"):
        tasks.add(title)
    window = Window(tasks=tasks)

    # A GtkListView builds rows lazily, during a layout pass. Without a mapped
    # window there is no layout pass, so ask for one and turn the loop until it
    # has happened -- this is what `pump` is for.
    window.present()
    window.list_view.allocate(400, 400, -1, None)
    pump()

    labels = []
    child = window.list_view.get_first_child()
    while child is not None:
        check = child.get_first_child()
        if check is not None and hasattr(check, "get_label"):
            labels.append(check.get_label())
        child = child.get_next_sibling()

    assert labels == ["one", "two", "three"]
    window.destroy()


def test_the_checkbox_is_bound_to_the_task(pump: object) -> None:
    tasks = TaskList()
    task = tasks.add("one")
    window = Window(tasks=tasks)

    window.present()
    window.list_view.allocate(400, 400, -1, None)
    pump()

    row = window.list_view.get_first_child()
    check = row.get_first_child()
    assert check.get_active() is False

    # The binding is bidirectional, so the model moving should move the widget.
    task.done = True
    assert check.get_active() is True

    # ...and the widget moving should move the model.
    check.set_active(False)
    assert task.done is False
    window.destroy()
