---
layout: chapter
title: "Further Reading"
number: 99
backmatter: true
unnumbered: true
---

The previous edition's bibliography was a list of tutorials from 2006 to 2009.
Almost every one of them is now either offline or describes a library that no
longer exists, so it has been replaced with the places worth reading today.

The single most useful habit: when something in this book disagrees with the API
reference, the API reference is right and this book is out of date.

## Reference documentation

The API references
: <https://docs.gtk.org/> — GTK 4, GDK, GSK, Gio, GLib, GObject and Pango, all
  generated from the same sources as the C documentation and kept current.

PyGObject
: <https://pygobject.gnome.org/> — the binding itself: how introspection maps C
  onto Python, what `gi.require_version` does, and the awkward corners
  (`GObject.Property`, closures, threading).

libadwaita
: <https://gnome.pages.gitlab.gnome.org/libadwaita/doc/> — every `Adw` widget used
  in Part I, with pictures.

The freedesktop specifications
: <https://specifications.freedesktop.org/> — the desktop entry format, the icon
  naming specification, the base directory specification and the menu
  specification. Dry, short, and the authority when something will not appear in
  a launcher.

## Guidance rather than API

The GNOME Human Interface Guidelines
: <https://developer.gnome.org/hig/> — when to use a switch and when a check
  button, how a dialog should be worded, what a header bar is for. Worth reading
  once end to end; it explains a lot of why GTK 4 removed things.

The GNOME Developer Documentation
: <https://developer.gnome.org/documentation/> — tutorials and "how do I" material
  above the level of the API reference, including the parts of application
  development this book covers in Part I.

## Things to read the source of

GTK 4 Demo and GTK 4 Widget Factory
: Installed with the GTK development packages as `gtk4-demo` and
  `gtk4-widget-factory`. `gtk4-demo` shows its own source for every example, which
  makes it the fastest answer to "how is this widget actually used". `gtk4-demo`
  is C, but the API is the same API.

Adwaita Demo
: `adwaita-1-demo`, the same idea for libadwaita.

GNOME applications in Python
: Reading a finished application teaches the parts a book leaves out — how a real
  project lays out its Meson build, its resources and its state. Most GNOME
  applications are hosted at <https://gitlab.gnome.org/GNOME/>.

## Tools worth having installed

`gtk4-icon-browser`
: Searchable index of every icon in the theme. See [Icon Names](94-icon-names.html).

The GTK Inspector
: `GTK_DEBUG=interactive python3 app.py`. A live widget tree, a CSS editor that
  applies as you type, and a way to see which widget is actually receiving your
  events.

`gdbus`, `busctl`, D-Spy
: For looking at the session bus before writing anything against it. See
  [D-Bus](10-dbus.html).

`gst-launch-1.0`, `gst-inspect-1.0`
: For prototyping a pipeline in seconds rather than minutes. See
  [Audio and Video with GStreamer](09-multimedia-gstreamer.html).

`flatpak-builder`
: For building the manifest in
  [Packaging and Distribution](15-packaging.html).

## Where the previous edition went

This book began as *PyGTK Notebook*, covering PyGTK and GTK 2 between 2008 and
2012. That material is preserved in the git history of this repository, and the
last PDF built from the original LyX source is at
<http://files.majorsilence.com/pygtkbook/pygtk-notebook-latest-0.13.pdf>.

If you are porting something written against it, start with
[Migrating from PyGTK](92-migrating-from-pygtk.html).
