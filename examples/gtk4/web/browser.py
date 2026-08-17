#!/usr/bin/env python3
"""A small browser: WebKitGTK in a GTK 4 window.

gtkmozembed and the Internet Explorer control the previous edition covered are
both long gone. WebKitGTK is what remains, it is a real modern engine, and for
GTK 4 the namespace is WebKit 6.0 -- not WebKit2 4.x, which is the GTK 3 build.
"""

import sys
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("WebKit", "6.0")
from gi.repository import Adw, GLib, GObject, Gtk, WebKit

HOME = "https://gnome.org/"


class Browser(Adw.ApplicationWindow):
    def __init__(self, uri, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.set_title("Browser")
        self.set_default_size(900, 640)

        self.view = WebKit.WebView()
        self.view.set_vexpand(True)

        settings = self.view.get_settings()
        settings.set_enable_developer_extras(True)
        settings.set_enable_write_console_messages_to_stdout(True)

        self.address = Gtk.Entry(hexpand=True)
        self.address.connect("activate", self.on_address_activated)

        back = Gtk.Button(icon_name="go-previous-symbolic")
        back.connect("clicked", lambda _b: self.view.go_back())
        forward = Gtk.Button(icon_name="go-next-symbolic")
        forward.connect("clicked", lambda _b: self.view.go_forward())
        reload_ = Gtk.Button(icon_name="view-refresh-symbolic")
        reload_.connect("clicked", lambda _b: self.view.reload())

        header = Adw.HeaderBar()
        header.pack_start(back)
        header.pack_start(forward)
        header.pack_start(reload_)
        header.set_title_widget(self.address)

        self.progress = Gtk.ProgressBar()
        self.progress.add_css_class("osd")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(self.progress)
        box.append(self.view)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(header)
        toolbar.set_content(box)
        self.set_content(toolbar)

        # State arrives as properties, not signals.
        self.back, self.forward = back, forward
        self.view.connect("notify::uri", self.on_uri_changed)
        self.view.connect("notify::estimated-load-progress", self.on_progress)
        # can_go_back() is a method, not a property, so there is nothing to bind
        # to -- history state is refreshed when a load changes state instead.
        self.view.connect("load-changed", self.on_load_changed)

        self.view.connect("load-failed", self.on_load_failed)
        self.view.connect("decide-policy", self.on_decide_policy)

        self.view.load_uri(uri)

    def on_address_activated(self, entry: Gtk.Entry) -> None:
        text = entry.get_text().strip()
        if not text:
            return
        # A bare "gnome.org" is not a URI; load_uri would reject it.
        if "://" not in text:
            text = "https://" + text
        self.view.load_uri(text)

    def on_uri_changed(self, view: Gtk.Widget, _pspec: GObject.ParamSpec) -> None:
        self.address.set_text(view.get_uri() or "")

    def on_load_changed(self, view: WebKit.WebView, event: WebKit.LoadEvent) -> None:
        self.back.set_sensitive(view.can_go_back())
        self.forward.set_sensitive(view.can_go_forward())
        if event == WebKit.LoadEvent.FINISHED:
            self.progress.set_visible(False)

    def on_progress(self, view: Gtk.Widget, _pspec: GObject.ParamSpec) -> None:
        fraction = view.get_estimated_load_progress()
        self.progress.set_fraction(fraction)
        self.progress.set_visible(0 < fraction < 1)

    def on_load_failed(self, _view: WebKit.WebView, _event: WebKit.LoadEvent,
                       uri: str, error: GLib.Error) -> bool:
        # Returning True says "I have shown the user something"; returning False
        # lets WebKit display its own error page.
        self.address.set_text(f"{uri} — {error.message}")
        return False

    def on_decide_policy(self, _view: WebKit.WebView, decision: WebKit.PolicyDecision,
                         decision_type: WebKit.PolicyDecisionType) -> bool:
        """Called before anything is navigated to, opened or downloaded."""
        if decision_type == WebKit.PolicyDecisionType.NAVIGATION_ACTION:
            action = decision.get_navigation_action()
            uri = action.get_request().get_uri()
            # A real application would decide here whether to allow it, open it
            # in the user's browser instead, or block it.
            print("navigating to", uri)
        decision.use()
        return True


def on_activate(app: Adw.Application) -> None:
    uri = sys.argv[1] if len(sys.argv) > 1 else HOME
    Browser(uri, application=app).present()


app = Adw.Application(application_id="com.example.Browser")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
