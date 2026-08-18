# Modernization plan

Where the book stands after the GNOME 50 pass, and what is left to do. This is a
working document — update it as items land.

## Shipped

Part I now targets the **GNOME 50 stack**: GTK 4.22, libadwaita 1.9,
PyGObject 3.56, Python 3.12+, Wayland only.

| Area | What changed |
| --- | --- |
| Version baseline | New *What this book targets* and *This book assumes Wayland* sections in ch. 1. Flatpak runtime 48 → 50. |
| Adaptive layout | `Adw.Breakpoint`, `Adw.OverlaySplitView`, the `sp` unit and the 600sp divide. New example `adaptive-window.py`. |
| Dialogs | `Adw.Dialog` / `Adw.AlertDialog` — string responses, no raise on dismissal, bottom sheet at phone width. New example `widgets/adw-dialogs.py`. |
| Keyboard shortcuts | Accelerators on actions, `Gtk.ShortcutController` for local keys, `Adw.ShortcutsDialog` for discoverability. New example `shortcuts.py`. |
| Clipboard | `Gdk.Clipboard`, async reads, the primary selection. New example `clipboard.py`, in ch. 3 beside drag and drop. |
| Theme | `Adw.StyleManager`: colour scheme, accent colour, high contrast, and what they mean for anything you drew yourself. New example `animation/style-manager.py`. |
| Video | `Gtk.GraphicsOffload` in the player and a new section in ch. 9. |
| asyncio | Rewritten around `gi.events.GLibEventLoop`: awaitable Gio methods, coroutines that may touch widgets, task-reference and task-creation traps. New example `threads/asyncio-await.py`; the worker-thread bridge is kept as the pre-3.50 fallback. |
| Type hints | Every function in `examples/` is annotated — 0 before, all of them now. |
| Testing | New **chapter 14**, with a three-file example application and 18 passing tests. Packaging moved to chapter 15. `make test` and a CI step. |
| CI stack | The examples job runs on `ubuntu-26.04`, not `ubuntu-latest`. `ubuntu-latest` is still 24.04 — libadwaita 1.5, PyGObject 3.48 — so it cannot run the material above, and a smoke test two releases behind the book proves nothing about the book. |

## To do

### 1. Part II — Qt 6 with PySide6

The title, subtitle, `_config.yml`, `index.md` and the last line of ch. 15 all
promise it. Until it exists the book advertises something it does not deliver,
which is a credibility problem before it is a content problem.

Two acceptable resolutions, in order of preference:

1. **Write it.** The same ground as Part I, with the toolkit comparison as the
   payoff. Qt 6.10 / PySide6 is the target.
2. **Retitle**, and demote Qt to a *Choosing a toolkit* appendix.

Do not leave it as it is. If Part II is going to take a while, do (2) now and
revisit.

### 2. The missing chapters

Roughly in order of return.

**Debugging and diagnostics.** GtkInspector has four scattered mentions and no
home. `GTK_DEBUG=interactive`, `G_DEBUG=fatal-warnings`, `GDK_DEBUG=offload`,
GLib structured logging against Python's `logging`, sysprof, and the
PyGObject-specific hazard of reference cycles between Python objects and
GObjects. The "an exception in a signal handler is printed and swallowed" point
currently lives in ch. 14 and belongs here too.

**Application architecture and state.** Chapter 2 builds properties, signals and
bindings, and nothing then says what to build *with* them. Where state lives,
persistence (SQLite/JSON), `Gio.ListModel` as the model layer, and how to split
an application past one file. Chapter 14's `tasklist.py` / `window.py` / `app.py`
split is the seed of this chapter.

**Environments and dependency management.** `venv`, `uv`, and the
system-PyGObject-versus-virtualenv collision that stops every beginner. Chapter
14 covers `--system-site-packages` in one paragraph; it deserves more, and it may
belong in ch. 1 rather than as its own chapter.

**Accessibility.** One mention today, in custom widgets. Roles and properties,
labelling, focus order, testing with Orca and Accerciser. Chapter 11's new
high-contrast material and ch. 14's AT-SPI note both point at this hole.

### 3. Enhancements to existing chapters

**Packaging (ch. 15)** is the weakest relative to its importance.
- Windows and macOS get one paragraph, in a book with "Qt 6" on the cover.
- No account of how users get **updates**.
- No Flathub submission or review process, which is the actual work.
- Missing: AppImage, macOS signing and notarization.

**Desktop integration (ch. 8).** Background and autostart portals, the global
shortcuts portal, notifications with action buttons.

**Getting started (ch. 1).** Lead with `Adw.Application` rather than building up
to libadwaita at the end. State a minimum Python version in the text as well as
in the new targets table.

**Audio and video (ch. 9).** Hardware decode paths, now that offload is covered.

**Web content (ch. 12).** CSP, and the honest "should you just build a web UI"
section that the chapter sets up but never has.

### 4. Cross-cutting topics with no home

- **Performance and startup time.** Lazy loading, large `Gio.ListModel`s, why
  `Gtk.ListView` recycling matters, the GPU renderer.
- **Fractional scaling, HDR and colour management.** One HiDPI mention today;
  GNOME 50 improved all three.
- **Crash reporting.** Nothing at present.

### 5. Type checking and lint policy

Type hints are in place; the policy is not. Current state, measured with mypy
and `pygobject-stubs` (`config=Gtk4,Gdk4`):

- `examples/gtk4/testing/` is **clean** — it is the example ch. 14 teaches from.
- The other examples produce ~105 errors, nearly all of them the documented
  PyGObject friction: Optional returns needing narrowing, `GObject.Property`
  being opaque to checkers, and Gst factories returning `Element | None`.

Decide between two positions and write it down:

1. **Leave them.** Chasing zero adds `assert isinstance` noise to teaching code.
   Document the friction, which ch. 14 already does.
2. **Clean them and gate CI**, accepting the noise for the guarantee.

Either way, add **ruff** for unused imports and import order, and run it in CI.

### 6. The Python floor is no longer tested

Chapter 1 says Python 3.12 is the floor. That used to be checked for free, because
CI ran on Ubuntu 24.04 and 24.04 is 3.12; moving to 26.04 for the GNOME 50 stack
means CI now only ever runs 3.14.

The difference is not cosmetic. Under PEP 649 (3.14) annotations are lazy, so an
annotation naming a class that does not exist is invisible until something asks
for it; under 3.12 the same annotation is evaluated at import and raises. That is
exactly how `WebKit.JavascriptResult` — a WebKit 4.x class that the 6.0 API
dropped — reached main annotated on a method and passing locally.

Pick one:

1. **Test both.** A second job on `ubuntu-24.04` running only the examples that
   do not need GNOME 50 APIs. Real coverage, and a list to maintain.
2. **Raise the floor** to whatever the GNOME 50 distributions ship, and say so in
   the version table. Nothing to maintain, and it narrows the audience on paper
   more than in practice.

### 7. Meta

- A *what this book assumes you know* section.
- A reader-facing errata and versioning story; the changelog covers editions, not
  corrections.

## Known local gaps

Six examples cannot run on a machine without the relevant system packages, and
fail the smoke test there rather than in CI:

| Examples | Needs |
| --- | --- |
| `cairo/text-with-pango.py`, `printing/*` | `python3-gi-cairo` (foreign cairo) |
| `multimedia/discover.py` | `gir1.2-gst-plugins-base-1.0` |
| `web/*` | `gir1.2-webkit-6.0` |

CI installs all three, so this is a local-setup note rather than a defect.
