#!/usr/bin/env python3
"""A translated application.

Three things have to line up for translation to work, and getting two of them
right produces an untranslated program with no error message:

  1. strings are marked in the source, and extracted into a .po file
  2. the compiled .mo file is installed where gettext looks for it
  3. the program binds its text domain *and* tells GLib's C side about it,
     so that strings inside .ui files are translated too

The third is the one that is specific to GTK, and the one people miss.
"""

import gettext
import locale
import os
import pathlib
import sys
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

APP_ID = "com.example.Greeter"
DOMAIN = "greeter"
HERE = pathlib.Path(__file__).parent

# Installed programs use /usr/share/locale. This looks beside the script first so
# the example runs from a checkout.
LOCALE_DIR = HERE / "locale" if (HERE / "locale").exists() else pathlib.Path("/usr/share/locale")


def set_up_translation() -> None:
    # setlocale() reads LC_ALL / LC_MESSAGES / LANG from the environment. Without
    # it the C library stays in the "C" locale and nothing is translated, however
    # correct the rest of your setup is.
    try:
        locale.setlocale(locale.LC_ALL, "")
    except locale.Error:
        pass                      # an unsupported locale is not worth dying over

    # For Python's own _() calls.
    gettext.bindtextdomain(DOMAIN, str(LOCALE_DIR))
    gettext.textdomain(DOMAIN)

    # And for GtkBuilder, which translates <property translatable="yes"> strings
    # from C. These are the same two calls, but through the C library, and they
    # are what the pure-Python versions above do *not* do.
    try:
        locale.bindtextdomain(DOMAIN, str(LOCALE_DIR))
        locale.textdomain(DOMAIN)
    except AttributeError:
        # Not available on every platform; on Windows use ctypes to call
        # libintl-8.dll's bindtextdomain directly.
        pass

    gettext.install(DOMAIN, str(LOCALE_DIR))


set_up_translation()

_ = gettext.gettext
ngettext = gettext.ngettext


def pgettext(context: str, message: str) -> str:
    """Disambiguate a word by context. "Open" the verb is not "Open" the state."""
    lookup = f"{context}\x04{message}"
    translated = gettext.gettext(lookup)
    return message if translated == lookup else translated


class Window(Gtk.ApplicationWindow):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # Translators: this is the window title.
        self.set_title(_("Greeter"))
        self.set_default_size(420, 260)

        self.count = 0

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        self.name = Gtk.Entry(placeholder_text=_("Your name"))
        box.append(self.name)

        greet = Gtk.Button(label=pgettext("verb", "Greet"))
        greet.connect("clicked", self.on_greet)
        box.append(greet)

        self.output = Gtk.Label(wrap=True)
        box.append(self.output)

        self.tally = Gtk.Label(wrap=True)
        self.update_tally()
        box.append(self.tally)

        box.append(Gtk.Label(label=_("Language: %s") % (locale.setlocale(locale.LC_MESSAGES),)))

        self.set_child(box)

    def on_greet(self, _button: Gtk.Button) -> None:
        name = self.name.get_text().strip() or _("stranger")
        # Use named or positional formatting, never concatenation: word order
        # differs between languages and a translator has to be able to move the
        # parts around.
        self.output.set_text(_("Hello, {name}!").format(name=name))
        self.count += 1
        self.update_tally()

    def update_tally(self) -> None:
        # ngettext picks the right plural form. Some languages have one form,
        # some have two, some have six; the .po file's Plural-Forms header says
        # which, and the code does not need to know.
        self.tally.set_text(
            ngettext("You have said hello once.",
                     "You have said hello {count} times.",
                     self.count).format(count=self.count)
        )


def on_activate(app: Gtk.Application) -> None:
    Window(application=app).present()


app = Gtk.Application(application_id=APP_ID)
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
