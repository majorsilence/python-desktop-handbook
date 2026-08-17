---
layout: chapter
title: "Testing"
number: 14
part: 1
---

> Every listing in this chapter is a file under `examples/gtk4/testing/`. The
> tests in it run on each build, along with the tests of this book's own examples.

## Introduction

Desktop applications have a reputation for being untestable, and it is mostly
deserved — but the reason is not that widgets are hard to drive. It is that the
interesting logic has usually been written *inside* the widgets, where nothing can
reach it without a display, a main loop and a synthetic mouse.

So this chapter is less about testing frameworks than about one structural
decision, made early, which is what everything else depends on:

**Keep your rules out of your widgets.**

Once that is true, most of your tests are ordinary Python tests with no GTK in
them at all, and the small number that genuinely need a window are testing wiring
rather than behaviour. Get this wrong and no amount of test tooling rescues you;
get it right and you barely need any.

The example is a to-do list in three files:

`tasklist.py`
: A `TaskList` and a `Task`. GObject, so the interface can bind to it — but it
  imports `Gio` and `GObject`, never `Gtk`. This is where every rule lives: what
  a valid title is, what counts as a duplicate, how many tasks are left.

`window.py`
: The widgets. Every method is a translation between a widget and the model, and
  none of them decides anything.

`app.py`
: The `Adw.Application`. Small on purpose, because a test wants to build a
  `Window` without an application wrapped around it.

## Setting up {#setup}

The awkward part of testing PyGObject is not pytest. It is that PyGObject comes
from your distribution and pytest comes from PyPI, and a virtual environment does
not contain the former:

```bash
python3 -m venv --system-site-packages venv
./venv/bin/pip install pytest
```

**`--system-site-packages` is the whole trick.** Without it the environment cannot
see `gi`, `import gi` fails, and the usual reaction is to `pip install PyGObject`,
which tries to compile a binding against your system GTK and fails differently.
The same flag is what you want with `uv venv --system-site-packages` if that is
your tool.

Then run them the way you would run any tests:

```bash
cd examples/gtk4/testing
../../../venv/bin/python -m pytest
```

## Testing the logic {#logic-tests}

With the rules in `tasklist.py`, this is just pytest:

```python
def test_a_blank_title_is_refused(tasks):
    with pytest.raises(ValueError):
        tasks.add("   ")
    assert tasks.titles() == []


def test_duplicates_are_refused(tasks):
    tasks.add("Write the tests")
    with pytest.raises(ValueError, match="already on the list"):
        tasks.add("Write the tests")
    assert len(tasks.titles()) == 1
```

No display, no main loop, no fixtures beyond a fresh `TaskList`. These run in
milliseconds and they are where most of your tests should be.

### Testing that a property notifies {#testing-notify}

There is one thing worth testing here that is specific to GObject, and it catches
a bug that is otherwise very hard to find.

`TaskList.remaining` is a computed property — it counts the unfinished tasks. GObject
does not know that, so nothing emits `notify::remaining` on its own; every method
that could change the answer has to say so. Miss one and the property still returns
the right number whenever anyone asks, but the label bound to it stops updating.
That presents as a display bug, and you will look for it in the wrong file.

Record the notifications and assert on them:

```python
def notifications_of(source, property_name):
    seen = []
    source.connect(f"notify::{property_name}",
                   lambda obj, _pspec: seen.append(obj.get_property(property_name)))
    return seen


def test_remaining_notifies_when_a_task_is_finished(tasks):
    task = tasks.add("one")
    seen = notifications_of(tasks, "remaining")

    task.done = True
    assert seen == [0]
```

That test fails unless `TaskList` is listening to its own children:

```python
task.connect("notify::done", lambda *_: self.notify("remaining"))
```

Delete that one line from `tasklist.py` and exactly two tests fail — this one, and
the window test that checks the status label. Every other test still passes, which
is a fair picture of how much of the suite a missing notification touches, and why
you want the test rather than the luck.

The same technique works for your own signals: connect, do the thing, assert on
what was recorded. Assert on the *count* as well as the values — a property that
notifies twice per change is a property that will make something flicker.

## Testing widgets {#widget-tests}

Some things only exist in the interface: that pressing Enter reaches the model,
that a binding is connected, that a refused entry keeps its text. Those need
widgets.

Two pieces of setup make it possible.

**Initialise GTK once.** `Adw.init()` (or `Gtk.init()`) has to happen before any
widget is constructed, and it is not safe to call per test. A session-scoped
autouse fixture is the right shape:

```python
@pytest.fixture(scope="session", autouse=True)
def gtk_initialised():
    Adw.init()
```

**Have a way to turn the main loop.** Tests never call `app.run()`, so nothing
iterates the main loop and anything deferred to an idle callback never happens.
Turn it by hand, with a limit so that a test which would otherwise hang fails
instead:

```python
def run(iterations=200):
    context = GLib.MainContext.default()
    turned = 0
    while context.pending() and turned < iterations:
        context.iteration(False)
        turned += 1
    return turned
```

`context.iteration(False)` is the important half: `False` means *do not block*. With
`True` a test with nothing pending waits forever.

### Pressing things {#emitting-signals}

You do not need synthetic input events. Emit the signal the input would have
caused:

```python
def test_typing_and_activating_adds_a_task():
    tasks = TaskList()
    window = Window(tasks=tasks)

    window.entry.set_text("Write the tests")
    window.entry.emit("activate")        # what pressing Enter does

    assert tasks.titles() == ["Write the tests"]
    assert window.entry.get_text() == ""
```

`emit("activate")` runs the same handler a keypress would, synchronously, with no
display interaction at all. `button.emit("clicked")` is the same idea, and
`action.activate(None)` is how you exercise something bound to a menu item without
opening the menu.

Note what that test asserts: that the model got the task, and that the entry
cleared. It does not re-test that blank titles are refused — that lives next door
in `test_tasklist.py`, where it costs nothing to run.

### Lists build their rows lazily {#testing-list-views}

`Gtk.ListView` does not create a row per item. It creates the rows it needs during
a layout pass and recycles them, which means a freshly constructed list view
contains no rows at all and a test that walks its children finds nothing.

Force a layout:

```python
window.present()
window.list_view.allocate(400, 400, -1, None)
pump()
```

Then the children exist and can be walked with `get_first_child()` and
`get_next_sibling()`. This is the point where widget tests start costing more than
they return, so use them for the binding rather than for the contents:

```python
task.done = True
assert check.get_active() is True     # the model moved the widget

check.set_active(False)
assert task.done is False             # and the widget moved the model
```

## Running without a display {#headless}

Widget tests need a display, and CI does not have one. There are two answers and
the second is better.

**Xvfb**, a fake X server, is the traditional one, and it is what this book's own
build uses because a couple of its examples want a real compositor's worth of
behaviour:

```bash
xvfb-run -a python3 -m pytest
```

**The broadway backend** needs no X at all — GTK renders to HTML over a socket, and
for a test that never looks at pixels that is enough. It needs its daemon running
first, which is the part that catches people out; set only the environment
variables and every widget test fails with `RuntimeError: Gtk couldn't be
initialized`:

```bash
gtk4-broadwayd :5 &
GDK_BACKEND=broadway BROADWAY_DISPLAY=:5 python3 -m pytest
```

It is lighter than Xvfb and it is one package rather than an X server.

Since GNOME 50 there is no X11 session at all, so `xvfb-run` is XWayland
compatibility rather than a representative environment. It is fine for tests; do
not conclude anything from it about how your application behaves on a real
desktop. If you need that, run a headless compositor —
`weston --backend=headless-backend.so` or `mutter --headless` — which is what
GNOME's own integration tests do.

Whichever you pick, a session bus is worth having too, or anything that owns a
name or talks to a portal fails in ways that have nothing to do with your test:

```bash
dbus-run-session -- xvfb-run -a python3 -m pytest
```

## Smoke tests {#smoke-tests}

There is a cheaper test than any of the above, and for a book — or any project with
a lot of example code — it catches more per line than everything else combined:
**start the program and shut it down again.**

That is what `tools/smoke-test.py` in this repository does to every listing in this
book. It replaces the blocking main loop with one that quits after 300 ms, runs each
example in its own interpreter, and reports anything that raised on the way up.

It finds import errors, constructor arguments that were renamed, methods that no
longer exist, signals that no longer exist, and anything that throws while the first
window is built. That is most of what breaks when a toolkit moves underneath you,
and none of it needs a single assertion.

One detail in it is worth stealing, because without it the whole thing quietly
reports success:

```python
crashed = "Traceback (most recent call last)" in result.stderr
if result.returncode == 0 and not crashed:
    ...
```

**An exception inside a GTK signal handler does not propagate.** GTK prints the
traceback and carries on, and the process still exits 0. If you check only the exit
status, a program whose every button handler raises looks perfectly healthy. Treat
a traceback on stderr as a failure.

## Driving the whole application {#integration}

Between "call a handler" and "test nothing" there is a middle option: run the real
application and drive it from a timeout.

```python
def on_started():
    window = app.get_active_window()
    window.entry.set_text("something")
    window.entry.emit("activate")
    assert window.tasks.titles() == ["something"]
    app.quit()
    return GLib.SOURCE_REMOVE


GLib.timeout_add(100, on_started)
app.run([])
```

Everything is real: the application, the activate handler, the window. Keep a small
number of these for the paths that matter, and remember that an assertion which
fails inside that callback is an assertion inside a GTK callback — swallowed, per
the previous section. Record the failure and re-raise it after `run()` returns.

For genuinely external testing — driving the application through the accessibility
bus the way a screen reader does — the tool is **dogtail**, which talks AT-SPI.
It tests the real thing including the accessibility layer, which is a useful side
effect, and it is slow and brittle enough that it should be a handful of tests
rather than a suite.

## Types and static checks {#type-checking}

A type checker is the test you do not have to write, and PyGObject's reputation for
being uncheckable is out of date.

The introspected modules are generated at import time, so a checker cannot see into
them on its own. Install the stubs:

```bash
pip install pygobject-stubs --no-cache-dir --config-settings=config=Gtk4,Gdk4,Soup3
```

The `config` setting picks which GTK version's stubs to generate; without it you may
get GTK 3 signatures and a great deal of confident nonsense. Then mypy or pyright
will catch a renamed method, a missing argument and a `set_child()` on a widget that
does not have one, before you run anything.

Annotate your own code — this book's examples are annotated throughout:

```python
def on_bind(self, _factory: Gtk.SignalListItemFactory,
            item: Gtk.ListItem) -> None:
```

Two rough edges are worth knowing before you turn it on, because both produce a
wall of errors on correct code the first time.

**Optional returns need narrowing.** A great many GTK getters are typed as
returning `None` as well as the thing you asked for, and they are right to be:

```python
check = item.get_child()      # Widget | None
task = item.get_item()        # GObject.Object | None
check.set_label(task.title)   # error: Item "None" has no attribute "set_label"
```

Narrow it rather than silencing it. An `assert isinstance()` documents what you
already know, and turns the rest of the method from unchecked to checked:

```python
assert isinstance(check, Gtk.CheckButton)
assert isinstance(task, Task)
```

**`**kwargs: object` does not survive contact with a GObject constructor.** The
pass-through `**kwargs` that every widget subclass in this book uses has to be
typed `Any`; `object` makes the checker try every property of the parent class
against it and reject all of them.

Then two things stay unchecked whatever you do. Signal handler signatures are not
verified, because `connect()` takes a string and a callable — a handler with the
wrong parameters is still a runtime error. And `GObject.Property` is opaque to
type checkers, so `task.done` is not known to be a `bool`. Neither is a reason to
skip the rest.

Add **ruff** for the things a type checker does not cover — unused imports, unused
variables, import order — and run all of it in CI beside the tests.

## What to test {#what-to-test}

A rough order of return, best first:

1. **The rules, with no GTK involved.** Cheap, fast, and where the bugs that matter
   live.
2. **Property notification and signals.** Specific to GObject, easy to get wrong,
   invisible until something stops updating.
3. **Smoke tests.** Enormous coverage per line of test code.
4. **Wiring, in widget tests.** That handlers reach the model and bindings are
   connected.
5. **A few whole-application paths**, driven from a timeout.
6. **AT-SPI tests**, if the application is big enough to warrant them.

And what not to bother with: that GTK works. A test asserting that
`Gtk.Label.set_text()` changed the label's text is testing someone else's library.
Test the code you wrote.

## Summary

- The decision that makes an application testable is keeping the rules out of the
  widgets. Everything else is technique.
- `python3 -m venv --system-site-packages` — PyGObject comes from the
  distribution and a plain venv cannot see it.
- Test that computed properties *notify*, not only that they compute. A missed
  `self.notify()` is a display bug you will look for in the wrong file.
- `Adw.init()` once, session-scoped, before any widget exists.
- Turn the main loop by hand with `context.iteration(False)` and an iteration limit,
  so a stuck test fails rather than hangs.
- Emit signals instead of synthesising input: `entry.emit("activate")`.
- `Gtk.ListView` builds rows during layout, so allocate and pump before looking for
  them.
- Headless means Xvfb or `GDK_BACKEND=broadway`; since GNOME 50 neither is a real
  desktop, so do not draw conclusions from them beyond "it ran".
- An exception in a GTK callback is printed and swallowed, and the process still
  exits 0. Treat a traceback on stderr as a failure.
- `pygobject-stubs` with `config=Gtk4` makes mypy and pyright useful; signal
  handler signatures and `GObject.Property` types stay unchecked.

[Packaging and Distribution](15-packaging.html) is next, and it is the last chapter
of Part I.
