#!/usr/bin/env python3
"""Desktop notifications, which replaced the status icon.

GtkStatusIcon is gone and system trays are not part of the GNOME desktop.  For
"something happened while you were elsewhere", send a GNotification: the desktop
shows it, keeps it in its notification list, and routes any button back to your
application as an action.

For the notification to appear at all, an installed .desktop file whose basename
matches the application id has to exist -- see the desktop integration chapter.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, Gtk

APP_ID = "com.example.Notification"


def send(app):
    notification = Gio.Notification.new("Export finished")
    notification.set_body("holiday-photos.zip is ready in your Downloads folder.")
    notification.set_icon(Gio.ThemedIcon.new("document-save-symbolic"))
    notification.set_priority(Gio.NotificationPriority.NORMAL)

    # Buttons name actions, exactly like menu items do.
    notification.add_button("Show it", "app.reveal")
    notification.set_default_action("app.reveal")

    # The id lets you replace or withdraw this notification later.
    app.send_notification("export-done", notification)


def on_startup(app):
    action = Gio.SimpleAction.new("reveal", None)
    action.connect("activate", lambda *_: print("reveal the file"))
    app.add_action(action)


def on_activate(app):
    window = Gtk.ApplicationWindow(application=app, title="Notifications")
    window.set_default_size(360, 140)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    send_button = Gtk.Button(label="Send a notification")
    send_button.connect("clicked", lambda _b: send(app))

    withdraw = Gtk.Button(label="Withdraw it")
    withdraw.connect("clicked", lambda _b: app.withdraw_notification("export-done"))

    box.append(send_button)
    box.append(withdraw)
    window.set_child(box)
    window.present()


app = Gtk.Application(application_id=APP_ID)
app.connect("startup", on_startup)
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
