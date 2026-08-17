"""The application itself. Everything it needs is loaded from installed data.

This is a module of an installed application, not a script: the template below
is loaded from a GResource that the generated launcher registers first. Run the
installed ``example-app`` instead.

smoke-test: skip
"""

import gettext
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, Gtk

APP_ID = "com.example.ExampleApp"
_ = gettext.gettext


@Gtk.Template(resource_path="/com/example/ExampleApp/window.ui")
class Window(Adw.ApplicationWindow):
    __gtype_name__ = "ExampleAppWindow"

    greeting = Gtk.Template.Child()
    count_button = Gtk.Template.Child()

    def __init__(self, settings, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.settings = settings
        self.count = settings.get_int("count")
        self.update()

    @Gtk.Template.Callback()
    def on_count_clicked(self, _button: Gtk.Button) -> None:
        self.count += 1
        self.settings.set_int("count", self.count)
        self.update()

    def update(self) -> None:
        self.greeting.set_text(
            gettext.ngettext("Counted once.", "Counted {n} times.", self.count)
            .format(n=self.count)
        )


class Application(Adw.Application):
    def __init__(self, version: str) -> None:
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.version = version
        self.settings = Gio.Settings.new(APP_ID)

        for name, callback, accels in (
            ("quit", lambda *_: self.quit(), ["<Control>q"]),
            ("about", self.on_about, []),
        ):
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            self.add_action(action)
            if accels:
                self.set_accels_for_action(f"app.{name}", accels)

    def do_activate(self) -> None:
        window = self.props.active_window or Window(self.settings, application=self)
        window.present()

    def on_about(self, *_args: object) -> None:
        Adw.AboutDialog(
            application_name=_("Example App"),
            application_icon=APP_ID,
            version=self.version,
            license_type=Gtk.License.MIT_X11,
        ).present(self.props.active_window)


def main(version: str) -> int:
    return Application(version).run(None)
