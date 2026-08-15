---
layout: chapter
title: "Packaging and Distribution"
number: 11
part: 1
---

> The example in this chapter is a complete, installable application under
> `examples/gtk4/packaging/`. It is built, validated, installed and run on each
> build of this book, so the layout described here is one that works.

## Introduction

A Python GTK application is not one file. By the time it is finished it is code,
`.ui` files, an icon, a desktop file, a settings schema, translations and a piece
of AppStream metadata — and every one of those has a place it must be installed to
before it works. The desktop file has to be in `applications`, the schema has to be
compiled, the `.mo` files have to be in `<lang>/LC_MESSAGES`, and the icon has to be
named after the application id.

That is what this chapter is about: what has to be installed where, the build system
that does it, and the two ways applications actually reach users.

The previous edition had a chapter here on IronPython and Gtk#. It is gone: it was
never a supported way to write GTK applications, and the projects behind it have
moved on.

## What has to be installed {#what-installs}

For the application id `com.example.ExampleApp`, under a prefix of `/usr` or
`~/.local`:

| What | Where |
| --- | --- |
| The launcher | `bin/example-app` |
| The Python modules | `share/example-app/exampleapp/` |
| The compiled resources | `share/example-app/example-app.gresource` |
| The desktop file | `share/applications/com.example.ExampleApp.desktop` |
| The icon | `share/icons/hicolor/scalable/apps/com.example.ExampleApp.svg` |
| The settings schema | `share/glib-2.0/schemas/com.example.ExampleApp.gschema.xml` |
| The AppStream metadata | `share/metainfo/com.example.ExampleApp.metainfo.xml` |
| The translations | `share/locale/<lang>/LC_MESSAGES/example-app.mo` |

Plus three caches that have to be regenerated afterwards, or the desktop does not
notice any of it: `glib-compile-schemas`, `gtk-update-icon-cache` and
`update-desktop-database`.

Notice how much of that is the application id repeated. That is the point of
picking it carefully in [Desktop Integration](05-desktop-integration.html).

## Meson {#meson}

GNOME builds with **Meson**, and so should a Python application that wants to fit
in — not because Python needs compiling, but because Meson already knows all of the
above.

```meson
project('example-app', version: '1.0.0', meson_version: '>= 1.0.0')

app_id = 'com.example.ExampleApp'

python = import('python').find_installation('python3')
gnome = import('gnome')
i18n = import('i18n')

prefix = get_option('prefix')
bindir = prefix / get_option('bindir')
datadir = prefix / get_option('datadir')
localedir = prefix / get_option('localedir')
pkgdatadir = datadir / meson.project_name()

subdir('src')
subdir('data')
subdir('po')

gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)
```

`gnome.post_install()` is the three cache updates, and it is one line rather than a
post-install script everyone forgets to write.

Make those paths **absolute** — `prefix / get_option('datadir')`, not
`get_option('datadir')`. The relative form works fine as an install directory and
then quietly breaks the launcher, which ends up looking for
`share/example-app/example-app.gresource` relative to whatever directory the user
happened to be in. Meson still honours `DESTDIR` when installing to an absolute
path, so nothing is lost.

### The generated launcher {#launcher}

The one file that has to know where things went is generated at build time:

```meson
configure_file(
  input: 'example-app.in',
  output: 'example-app',
  configuration: {
    'PYTHON': python.full_path(),
    'VERSION': meson.project_version(),
    'localedir': localedir,
    'pkgdatadir': pkgdatadir,
  },
  install: true,
  install_dir: bindir,
  install_mode: 'rwxr-xr-x',
)
```

```python
#!@PYTHON@
pkgdatadir = '@pkgdatadir@'
localedir = '@localedir@'

sys.path.insert(1, pkgdatadir)

resource = Gio.Resource.load(os.path.join(pkgdatadir, 'example-app.gresource'))
resource._register()

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain('example-app', localedir)
gettext.textdomain('example-app')
locale.bindtextdomain('example-app', localedir)     # for the .ui files
locale.textdomain('example-app')

from exampleapp import application
sys.exit(application.main(VERSION))
```

Everything the application needs to find is settled here, once, from values the
build system knows. Nothing downstream guesses a path from `__file__`.

The double `bindtextdomain` is the one from
[Internationalization](10-internationalization.html), and this is where it belongs.

### GResource {#gresource}

`.ui` files, CSS, icons and any other data are compiled into a single resource
bundle:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<gresources>
  <gresource prefix="/com/example/ExampleApp">
    <file preprocess="xml-stripblanks">window.ui</file>
  </gresource>
</gresources>
```

```meson
gnome.compile_resources(
  'example-app', 'example-app.gresource.xml',
  gresource_bundle: true, install: true, install_dir: pkgdatadir,
)
```

Once the bundle is registered, everything in it is addressed by URI:

```python
@Gtk.Template(resource_path="/com/example/ExampleApp/window.ui")
class Window(Adw.ApplicationWindow):
    __gtype_name__ = "ExampleAppWindow"
```

One file to install instead of a directory of them, no path lookups at runtime, and
`Gio.File.new_for_uri("resource:///com/example/ExampleApp/style.css")` works for
anything else you put in there.

### Validate at build time {#validate}

The mistakes in this chapter's file formats are all caught by a validator, and a
validator you have to remember to run is one you will not run:

```meson
test('validate-desktop', desktop_file_validate, args: [desktop_file])
test('validate-metainfo', appstreamcli, args: ['validate', '--no-net', metainfo_file])
test('validate-schema', glib_compile_schemas, args: ['--strict', '--dry-run', dir])
```

`meson test` now checks all three. Finding out that your AppStream metadata is
invalid from a rejected Flathub submission is a slower way to learn the same thing.

## AppStream metadata {#appstream}

The `.metainfo.xml` is what a software centre shows: name, summary, description,
screenshots, release notes, content rating. Flathub will not accept an application
without it, and GNOME Software will not show one.

```xml
<component type="desktop-application">
  <id>com.example.ExampleApp</id>
  <name>Example App</name>
  <summary>An application that installs itself properly</summary>

  <metadata_license>CC0-1.0</metadata_license>
  <project_license>MIT</project_license>

  <description>
    <p>A minimal GTK 4 application, packaged the way GNOME applications are.</p>
  </description>

  <launchable type="desktop-id">com.example.ExampleApp.desktop</launchable>
  <content_rating type="oars-1.1"/>

  <releases>
    <release version="1.0.0" date="2026-01-15">
      <description><p>First release.</p></description>
    </release>
  </releases>
</component>
```

The `<id>` must match the application id and the `<launchable>` must match the
desktop file, or the store shows an application that cannot be launched.
`<content_rating>` is required even when the answer is "nothing to declare" — an
empty `oars-1.1` element means exactly that. The `<summary>` is one line, no full
stop, and must not repeat the name.

The summary and description are translated the same way everything else is:
`i18n.merge_file()` merges the `.po` translations into the installed file.

## Flatpak {#flatpak}

For a Python GTK application, Flatpak is the way to reach users directly. It ships
the GNOME runtime with it, so you are not at the mercy of which GTK version a
distribution has, and it sandboxes the result.

```json
{
    "id": "com.example.ExampleApp",
    "runtime": "org.gnome.Platform",
    "runtime-version": "48",
    "sdk": "org.gnome.Sdk",
    "command": "example-app",

    "finish-args": [
        "--share=ipc",
        "--socket=wayland",
        "--socket=fallback-x11",
        "--device=dri"
    ],

    "modules": [
        {
            "name": "example-app",
            "buildsystem": "meson",
            "sources": [{ "type": "dir", "path": "." }]
        }
    ]
}
```

```bash
flatpak install flathub org.gnome.Platform//48 org.gnome.Sdk//48
flatpak-builder --user --install --force-clean build com.example.ExampleApp.json
flatpak run com.example.ExampleApp
```

The GNOME runtime already contains Python, PyGObject, GTK 4, libadwaita, GStreamer
and WebKitGTK, which is most of this book — so a plain GTK application often needs
no extra modules at all. Dependencies from PyPI go in as their own modules;
`flatpak-pip-generator` writes those for you.

`finish-args` is the sandbox's permissions, and the interesting thing is how few
you need. There is no `--filesystem=home` in the list above, and there should not
be: the file dialog goes through the portal, so the user granting access to a file
*is* the permission. Every `finish-args` line you add is a warning triangle on your
Flathub page, and most of them are avoidable by using the APIs in the desktop
integration chapter rather than going around them.

## The other routes {#other-routes}

**Distribution packaging.** A `.deb` or an RPM built from the same Meson project.
Best integration, most work, and you are unlikely to do it yourself — if your
application is worth packaging, a distribution maintainer will usually do it,
provided your build is a normal one. That is another argument for Meson.

**A wheel on PyPI.** Fine for a library, awkward for an application. `pip install`
does not install desktop files, icons or schemas, and it cannot install PyGObject's
dependency on GTK — that has to come from the system. Reasonable for a developer
tool; not for something with an icon in the launcher.

**Windows and macOS.** Possible, not pleasant. On Windows the practical route is
MSYS2, which packages GTK 4 and PyGObject, with `cx_Freeze` or PyInstaller for the
bundle and Inno Setup for the installer. On macOS it is Homebrew or `jhbuild`, plus
`py2app`. In both cases you are shipping the whole GTK stack yourself, native file
dialogs are GTK's rather than the platform's, and the result does not look at home.
If cross-platform look and feel is a requirement, that is a real argument for Qt — which is what Part II is about.

## Try it {#try-it}

```bash
cd examples/gtk4/packaging
meson setup builddir --prefix=$HOME/.local
meson compile -C builddir
meson test -C builddir
meson install -C builddir
example-app
```

Installing to `~/.local` needs no root and puts everything where the desktop
already looks. To see the translations, use a real locale rather than only
`LANGUAGE`:

```bash
LC_ALL=de_DE.UTF-8 LANGUAGE=de example-app
```

## Summary

- An application is code plus a desktop file, icon, schema, resources, translations
  and AppStream metadata, each with a required location.
- Meson knows all of them. `gnome.post_install()` regenerates the three caches.
- Make the paths absolute in `meson.build`, or the generated launcher looks for its
  resources relative to the current directory.
- Compile `.ui` files and other data into a GResource and address them by URI.
- Validate the desktop file, the metadata and the schema as part of `meson test`.
- AppStream metadata is not optional for a software centre, and its ids must match.
- Flatpak against the GNOME runtime is the direct route to users; keep
  `finish-args` short by using portals instead of filesystem access.

That is the end of Part I. Part II covers the same ground again with Qt 6 and
PySide6.
