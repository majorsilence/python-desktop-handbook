---
layout: chapter
title: "Source Code License"
number: 91
appendix: true
---

Every example in this book — everything under `examples/` in the repository, and
every listing reproduced in the text — is released under the MIT license. Copy it,
change it, and use it in your own programs, commercial or not. You do not have to
credit this book, though it is appreciated.

The book's **text** is under a different, more restrictive licence; see
[Book Text Licenses](90-book-text-licenses.html).

> **Note on the previous edition.** Editions up to 0.13 released their sample code
> under the LGPL v3. Those examples targeted PyGTK and GTK 2 and have been removed;
> they remain available under the LGPL in this repository's git history. All the
> code in this edition is new and is MIT.

## The MIT License

Copyright (c) 2008–2026 Peter Gill

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## What this does not cover

The libraries the examples use have their own licences, and they are not MIT:

GTK 4, GLib, GObject, Pango, GdkPixbuf
: LGPL v2.1 or later. Linking to them from your own program — which is what
  PyGObject does — does not require your program to be free software, but
  modifying the libraries themselves does.

libadwaita
: LGPL v2.1 or later.

Cairo
: LGPL v2.1 or the Mozilla Public License 1.1, your choice.

GStreamer
: LGPL v2.1 or later for the framework. **Individual plugins vary**, and some
  encoders and decoders carry patent considerations in some jurisdictions. Check
  the licence of the specific plugins you ship, particularly if you are
  distributing a bundle rather than depending on system packages.

WebKitGTK
: LGPL v2.1 and BSD.

PySide6, used in Part II
: LGPL v3 or a commercial Qt licence. The LGPL option has real conditions attached
  when you bundle Qt into an application rather than linking against a system copy
  — read them before you ship one.

If you are shipping a Flatpak, the runtime carries most of this for you and
`flatpak-builder` records the licences of what it built.
