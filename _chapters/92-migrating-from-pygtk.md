---
layout: chapter
title: "Migrating from PyGTK"
number: 92
appendix: true
---

Earlier editions of this book taught PyGTK: GTK 2 through the `pygtk` bindings.
That stack is gone. PyGTK has had no release since 2011, GTK 2 stopped getting
fixes, and the bindings do not exist for Python 3 in any supported form.

This appendix is a translation table. It will not port a program for you, but it
will tell you what each idiom you remember is called now, and which of them have no
replacement because the pattern itself was dropped.

Everything below assumes the modern imports:

```python
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib, Gtk
```

## The shape of a program

PyGTK
: You built a `gtk.Window`, packed it, called `show_all()`, then `gtk.main()`, and
  connected `destroy` to `gtk.main_quit`.

GTK 4
: You build a `Gtk.Application`, create a `Gtk.ApplicationWindow` in its `activate`
  handler, call `present()`, and let `app.run()` return when the last window closes.

The application object is not optional ceremony. It gives you the single-instance
check, actions, keyboard accelerators, the menu bar, D-Bus activation and session
integration — all of which PyGTK programs had to arrange by hand or do without.

```python
# then
win = gtk.Window()
win.connect("destroy", gtk.main_quit)
win.show_all()
gtk.main()

# now
def on_activate(app):
    Gtk.ApplicationWindow(application=app).present()

app = Gtk.Application(application_id="com.example.App")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
```

## Imports and versions

`import pygtk; pygtk.require("2.0"); import gtk` becomes
`import gi; gi.require_version("Gtk", "4.0"); from gi.repository import Gtk`.

The `require_version` call has to come before the import, not after, and it is
needed for every library with more than one version installed. Skipping it does not
fail cleanly — it picks a version, warns, and crashes later.

Names lost their lowercase module: `gtk.Window` is `Gtk.Window`, `gtk.HBox` is
`Gtk.Box`, `gobject` is `GObject`, and the parts of GLib that PyGTK exposed as
`gobject.timeout_add` are now `GLib.timeout_add`.

## Containers and visibility

`show_all()` is gone
: Widgets are visible when created. Hide what you do not want with
  `set_visible(False)`.

`container.add(child)` is gone
: A widget that holds one child has `set_child()`. `Gtk.Window`, `Gtk.Button`,
  `Gtk.ScrolledWindow`, `Gtk.Frame` all work this way.

`box.pack_start(child, expand, fill, padding)` is gone
: Use `box.append(child)` or `box.prepend(child)`, and move the three arguments
  onto the child: `child.set_hexpand(True)`, `child.set_halign(...)`,
  `child.set_margin_start(...)`.

`gtk.HBox` / `gtk.VBox` are gone
: One class with an orientation:
  `Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)`.

`gtk.Table` is gone
: `Gtk.Grid`, with `attach(child, column, row, width, height)`.

`widget.destroy()` on a child is gone
: Remove it from its parent instead — `box.remove(child)` or
  `parent.set_child(None)`. Windows still have `close()`.

## Widgets that were renamed or replaced

| PyGTK | GTK 4 |
| --- | --- |
| `gtk.RadioButton` | `Gtk.CheckButton` joined with `set_group()` |
| `gtk.ComboBox`, `gtk.ComboBoxText` | `Gtk.DropDown` |
| `gtk.TreeView` + `gtk.ListStore` | `Gtk.ColumnView` / `Gtk.ListView` + `Gio.ListStore` |
| `gtk.MessageDialog` | `Gtk.AlertDialog` |
| `gtk.FileChooserDialog` | `Gtk.FileDialog` |
| `gtk.ColorSelectionDialog` | `Gtk.ColorDialog` |
| `gtk.FontSelectionDialog` | `Gtk.FontDialog` |
| `gtk.Statusbar` | `Adw.Toast`, or a label in the header bar |
| `gtk.Table` | `Gtk.Grid` |
| `gtk.Alignment` | `halign` / `valign` / margins on the child |
| `gtk.EventBox` | event controllers, added to any widget |
| `gtk.Arrow`, `gtk.HSeparator` | `Gtk.Image` with an icon name, `Gtk.Separator` |
| `gtk.STOCK_*` | icon names — see [Icon Names](94-icon-names.html) |
| `gtk.UIManager`, `gtk.ActionGroup` | `Gio.Menu` + `Gio.SimpleAction` |
| `gtk.Builder` (glade files) | `Gtk.Builder` (`.ui` files), or Blueprint |

## Dialogs stopped blocking

PyGTK dialogs ran a nested main loop:

```python
response = dialog.run()
dialog.destroy()
if response == gtk.RESPONSE_OK:
    ...
```

GTK 4 dialogs are asynchronous. You pass a callback and return immediately:

```python
dialog = Gtk.AlertDialog()
dialog.set_buttons(["Cancel", "Delete"])
dialog.choose(window, None, on_choice)

def on_choice(dialog, result, _data=None):
    try:
        index = dialog.choose_finish(result)
    except GLib.Error:
        return          # dismissed, not answered
```

This is the single most invasive change when porting. Code shaped like "ask a
question in the middle of a function and carry on with the answer" has to be split
in two at the question. There is no supported way to run a nested loop and wait.

The upside is that the nested-loop bugs go with it: no more reentrant signal
handlers, no more dialogs that outlive the window that opened them, no more
`destroy()` you forgot.

## Signals

`connect()` works the same, and extra arguments are still passed through to the
callback. Two differences:

Some `toggled`-style signals became property notifications. `Gtk.Switch` has no
`toggled`; watch `notify::active` instead. The handler takes an extra `GParamSpec`
argument you will ignore.

Input handling moved to **event controllers**. There is no
`widget.connect("button-press-event", ...)` and no `gtk.EventBox` to wrap a widget
that cannot receive events. Instead you attach a controller to any widget:

```python
click = Gtk.GestureClick()
click.connect("pressed", on_pressed)   # (gesture, n_press, x, y)
label.add_controller(click)

keys = Gtk.EventControllerKey()
keys.connect("key-pressed", on_key)    # (controller, keyval, keycode, state)
window.add_controller(keys)

motion = Gtk.EventControllerMotion()
motion.connect("motion", on_motion)    # (controller, x, y)
widget.add_controller(motion)
```

## Drawing

`expose-event` and `widget.window` are gone, along with the GDK drawing API.

```python
area = Gtk.DrawingArea()
area.set_draw_func(on_draw)            # (area, cairo_context, width, height)
```

Cairo is still Cairo, so the body of an old `expose-event` handler usually
transplants unchanged once you take the context from the argument list instead of
calling `widget.window.cairo_create()`. See
[Drawing with Cairo](03-drawing-with-cairo.html).

## Threads

`gtk.gdk.threads_init()`, `threads_enter()` and `threads_leave()` are gone and have
no replacement. GTK 4 is not thread-safe and never pretends to be: touch widgets
only from the main thread.

To get a result from a worker thread back into the interface, hand it to the main
loop:

```python
GLib.idle_add(update_the_label, result)
```

`GLib.idle_add` and `GLib.timeout_add` are safe to call from any thread, and the
callback runs on the main thread. A callback returning `GLib.SOURCE_CONTINUE`
(`True`) is called again; returning `GLib.SOURCE_REMOVE` (`False`) stops it.

## Things with no replacement

Some of what the previous edition covered has no modern equivalent, because the
technology behind it was retired rather than replaced:

- **libglade** — use `Gtk.Builder` with `.ui` files; `gtk-builder-convert` is long gone.
- **Glade the designer** — no longer supports GTK 4. Write `.ui` files by hand,
  use Blueprint, or use Cambalache.
- **GConf** — use `GSettings`. See [Desktop Integration](05-desktop-integration.html).
- **Clutter** — folded into GTK; use GTK 4's own animation API. See
  [Animation and Transitions](08-animation.html).
- **gtkmozembed and the Internet Explorer control** — use WebKitGTK. See
  [Embedding Web Content](09-web-content.html).
- **IronPython with Gtk#** — not a supported way to write GTK applications.
- **Empathy and Geoclue chapters** — Empathy is unmaintained; Geoclue is reached
  through portals now.
