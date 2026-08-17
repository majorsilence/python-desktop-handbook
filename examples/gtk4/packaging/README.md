# Packaging example

A minimal GTK 4 application, laid out the way a GNOME application is laid out. It
exists to be read alongside the packaging chapter rather than to do anything
useful.

```text
meson.build                             the build
src/                                    the code, the .ui file and the resource bundle
data/                                   desktop file, icon, settings schema, AppStream metadata
po/                                     translations
com.example.ExampleApp.json             the Flatpak manifest
```

## Build and install it

```sh
meson setup builddir --prefix=$HOME/.local
meson compile -C builddir
meson test -C builddir          # validates the desktop file, metadata and schema
meson install -C builddir
example-app
```

Installing to `$HOME/.local` needs no root, and puts everything where the desktop
already looks: `~/.local/bin`, `~/.local/share/applications`,
`~/.local/share/glib-2.0/schemas` and so on.

## Build it as a Flatpak

```sh
flatpak install flathub org.gnome.Platform//50 org.gnome.Sdk//50
flatpak-builder --user --install --force-clean build-flatpak com.example.ExampleApp.json
flatpak run com.example.ExampleApp
```
