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

Part I — GTK 4 with PyGObject — is complete:

- **[Getting Started with GTK 4](01-getting-started.html)** — `Gtk.Application`,
  boxes without packing arguments, grouped check buttons in place of radio
  buttons, `Gtk.DropDown`, menus as models plus actions, asynchronous dialogs,
  and libadwaita.
- **[GObject](02-gobject.html)** — new. Properties, signals and bindings: the
  layer the rest of Part I is built on and the previous edition never explained.
- **[More GTK 4](03-more-gtk4.html)** — list and column views over
  `Gio.ListStore`, `Gtk.FileDialog`, drag and drop through controllers,
  `Gtk.Picture`, `Gtk.Template`, notifications.
- **[Threads and Asynchronous Work](04-threads-and-async.html)** — new. Gio's
  async APIs, worker threads, cancellation and asyncio. `gdk_threads_enter()` is
  gone and has no replacement.
- **[Drawing with Cairo](05-drawing-with-cairo.html)** — Cairo through
  `Gtk.DrawingArea`, Pango for text, `GtkSnapshot` for widget drawing.
- **[Custom Widgets](06-custom-widgets.html)** — new, and finally written: the
  previous edition's chapter of this name contained one line. Composition,
  measure and allocate, and layout managers.
- **[Printing](07-printing.html)** — `Gtk.PrintOperation`, pagination, and
  exporting a PDF so printing is testable without a printer.
- **[Desktop Integration](08-desktop-integration.html)** — GSettings in place of
  GConf, desktop files, libsecret in place of the gnome-keyring API, portals.
- **[Audio and Video with GStreamer](09-multimedia-gstreamer.html)** — GStreamer
  1.0, `Gtk.MediaFile`, pipelines and the bus, discovery, transcoding.
- **[D-Bus](10-dbus.html)** — GDBus in place of dbus-python, proxies, signals,
  and exporting a service.
- **[Animation and Transitions](11-animation.html)** — replaces Clutter with
  container transitions, CSS, `Adw.Animation` and the frame clock.
- **[Embedding Web Content](12-web-content.html)** — WebKitGTK 6.0 in place of
  gtkmozembed, and the JavaScript bridge.
- **[Internationalization](13-internationalization.html)** — gettext without
  intltool, and the two text-domain bindings GTK needs.
- **[Packaging and Distribution](14-packaging.html)** — replaces IronPython and
  Gtk#. Meson, GResource, AppStream metadata and Flatpak.
- **[Migrating from PyGTK](92-migrating-from-pygtk.html)** — a translation table
  from the previous edition's idioms.

The appendices were rewritten too: *Icon Names* is now a stock-item to icon-name
mapping rather than the GTK 2 stock list, and the bibliography is now *Further
Reading*, pointing at documentation that still exists.

Part II — Qt 6 with PySide6 — is not written yet.

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
