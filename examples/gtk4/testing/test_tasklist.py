"""Tests for the logic. No widgets, no display, no main loop.

smoke-test: skip -- this is pytest's, not a program to run.

These are the tests that matter most, and they are ordinary Python tests. That
is the return on keeping tasklist.py free of Gtk: the interesting rules are
reachable without any of the machinery the next file needs.
"""

import pytest

from tasklist import TaskList


def test_adding_a_task(tasks: TaskList) -> None:
    task = tasks.add("Write the tests")
    assert tasks.titles() == ["Write the tests"]
    assert task.done is False


def test_titles_are_stripped(tasks: TaskList) -> None:
    tasks.add("  padded  ")
    assert tasks.titles() == ["padded"]


@pytest.mark.parametrize("title", ["", "   ", "\t\n"])
def test_a_blank_title_is_refused(tasks: TaskList, title: str) -> None:
    with pytest.raises(ValueError):
        tasks.add(title)
    assert tasks.titles() == []


def test_duplicates_are_refused(tasks: TaskList) -> None:
    tasks.add("Write the tests")
    with pytest.raises(ValueError, match="already on the list"):
        tasks.add("Write the tests")
    assert len(tasks.titles()) == 1


def test_removing_something_absent_is_an_error(tasks: TaskList) -> None:
    stray = TaskList().add("elsewhere")
    with pytest.raises(LookupError):
        tasks.remove(stray)


def test_clear_done_removes_only_finished_tasks(tasks: TaskList) -> None:
    first = tasks.add("done already")
    tasks.add("still to do")
    first.done = True

    assert tasks.clear_done() == 1
    assert tasks.titles() == ["still to do"]


# -- the computed property, which is where the bugs are ------------------------


def test_remaining_counts_unfinished_tasks(tasks: TaskList) -> None:
    first = tasks.add("one")
    tasks.add("two")
    assert tasks.remaining == 2

    first.done = True
    assert tasks.remaining == 1


def notifications_of(source: TaskList, property_name: str) -> list[int]:
    """Record the value of a property every time it says it changed."""
    seen: list[int] = []
    source.connect(f"notify::{property_name}",
                   lambda obj, _pspec: seen.append(obj.get_property(property_name)))
    return seen


def test_remaining_notifies_when_a_task_is_added(tasks: TaskList) -> None:
    seen = notifications_of(tasks, "remaining")
    tasks.add("one")
    assert seen == [1]


def test_remaining_notifies_when_a_task_is_finished(tasks: TaskList) -> None:
    """The one that catches the real bug.

    `remaining` is computed, so nothing notifies it on its own. A task being
    ticked happens on the Task, not on the TaskList -- if the list is not
    listening to its children, this test fails while every other test passes,
    and in the running application a label silently stops updating.
    """
    task = tasks.add("one")
    seen = notifications_of(tasks, "remaining")

    task.done = True
    assert seen == [0]


def test_remaining_notifies_on_clear(tasks: TaskList) -> None:
    task = tasks.add("one")
    task.done = True
    seen = notifications_of(tasks, "remaining")

    tasks.clear_done()
    assert seen == [0]


def test_clear_with_nothing_to_clear_does_not_notify(tasks: TaskList) -> None:
    tasks.add("one")
    seen = notifications_of(tasks, "remaining")

    assert tasks.clear_done() == 0
    assert seen == []
