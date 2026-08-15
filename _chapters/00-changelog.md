---
layout: chapter
title: "Changelog"
number: 0
unnumbered: true
---

## Version 1.0 — in progress

The book is being rewritten. The previous edition taught PyGTK and GTK 2, a stack
that has had no release since 2011; this one teaches GTK 4 with PyGObject in Part I
and Qt 6 with PySide6 in Part II.

Three things changed about how the book is made, as well as what is in it:

- The source moved from LyX to Markdown. The site is built with Jekyll and the PDF
  with pandoc, from the same files.
- Every listing is a file under `examples/`, and every example is started and shut
  down again on each build. Code that stops working fails the build.
- Figures that can be generated are generated, by running the example that draws
  them, rather than being screenshots that slowly stop matching the text.

Rewritten so far:

- **[Getting Started with GTK 4](01-getting-started.html)** — replaces *PyGTK
  Introduction*. `Gtk.Application`, boxes without packing arguments, grouped check
  buttons in place of radio buttons, `Gtk.DropDown`, menus as models plus actions,
  asynchronous dialogs, and an introduction to libadwaita.
- **[More GTK 4](02-more-gtk4.html)** — replaces *More PyGTK*. List and column
  views over `Gio.ListStore`, `Gtk.FileDialog`, drag and drop through controllers,
  `Gtk.Picture`, `Gtk.Template` over `.ui` files, and notifications.
- **[Drawing with Cairo](03-drawing-with-cairo.html)** — replaces *Cairo*. Cairo
  through `Gtk.DrawingArea`, Pango for text, and `GtkSnapshot` for widget drawing.
- **[Migrating from PyGTK](92-migrating-from-pygtk.html)** — new. A translation
  table from the idioms of the previous edition.

Chapters not yet rewritten still carry their GTK 2 text and say so at the top.

Dropped, because the technology was retired rather than replaced: the IronPython
and Gtk# chapter, the PyGTK-on-Windows appendix, and the unfinished Telepathy,
Geoclue and custom-widget chapters.

## Earlier editions

Versions 0.03 to 0.13, from December 2008 to October 2012, covered PyGTK and GTK 2:
widgets and layout, Glade and libglade, Cairo, printing, GConf and desktop
integration, GStreamer, D-Bus, Clutter, embedded Mozilla and Internet Explorer,
internationalization, and IronPython with Gtk#.

That edition is preserved in the git history of this repository, and the last PDF
built from the LyX source is
[pygtk-notebook-latest-0.13.pdf](http://files.majorsilence.com/pygtkbook/pygtk-notebook-latest-0.13.pdf).
