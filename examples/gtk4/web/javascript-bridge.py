#!/usr/bin/env python3
"""Talking to the page: running JavaScript, and letting the page call back.

Two directions:

  Python -> page   evaluate_javascript(), asynchronous, with a JSCValue reply
  page -> Python   a user content manager script message handler

Together they are how you build an application whose interface is HTML but whose
logic is Python. Everything here works against a page you load yourself; do not
wire an untrusted page to a handler that does anything privileged.
"""

import sys
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("WebKit", "6.0")
from gi.repository import Gio, GLib, Gtk, WebKit

PAGE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <style>
      body { font: 15px system-ui, sans-serif; margin: 2rem; color: #241f31; }
      button { font: inherit; padding: .4rem .8rem; }
      #count { font-weight: 700; }
    </style>
  </head>
  <body>
    <h1>A page that talks back</h1>
    <p>Clicked <span id="count">0</span> times.</p>
    <button onclick="tell()">Tell the application</button>

    <script>
      let count = 0;
      function tell() {
        count += 1;
        document.getElementById('count').textContent = count;
        // The handler name registered on the Python side becomes a property of
        // window.webkit.messageHandlers.
        window.webkit.messageHandlers.fromPage.postMessage(
          JSON.stringify({clicks: count})
        );
      }
      function setTitle(text) { document.title = text; return document.title; }
    </script>
  </body>
</html>
"""


class Window(Gtk.ApplicationWindow):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.set_title("JavaScript bridge")
        self.set_default_size(720, 520)

        # Register the handler *before* the view is created, and the page can use
        # window.webkit.messageHandlers.fromPage from its first line.
        manager = WebKit.UserContentManager()
        manager.register_script_message_handler("fromPage", None)
        manager.connect("script-message-received::fromPage", self.on_message)

        self.view = WebKit.WebView(user_content_manager=manager)
        self.view.set_vexpand(True)

        # A script injected into every page this view loads.
        manager.add_script(WebKit.UserScript.new(
            "console.log('injected before the page runs');",
            WebKit.UserContentInjectedFrames.TOP_FRAME,
            WebKit.UserScriptInjectionTime.START,
            None, None,
        ))

        self.status = Gtk.Label(label="waiting for the page", xalign=0)
        self.status.set_margin_start(12)
        self.status.set_margin_end(12)
        self.status.set_margin_bottom(6)

        ask = Gtk.Button(label="Set the page title from Python")
        ask.set_margin_start(12)
        ask.set_margin_end(12)
        ask.connect("clicked", self.on_ask)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.append(self.view)
        box.append(ask)
        box.append(self.status)
        self.set_child(box)

        # A base URI matters: without one the page is treated as coming from
        # nowhere, and anything origin-checked will fail.
        self.view.load_html(PAGE, "file:///")

    # -- page -> Python ---------------------------------------------------------

    def on_message(self, _manager: WebKit.UserContentManager,
                   message: WebKit.JavascriptResult) -> None:
        # The payload is a JSCValue. to_string() for text, or to_json() for
        # anything structured.
        payload = message.to_string()
        self.status.set_text(f"the page said: {payload}")

    # -- Python -> page ---------------------------------------------------------

    def on_ask(self, _button: Gtk.Button) -> None:
        self.view.evaluate_javascript(
            "setTitle('set from Python at ' + new Date().toLocaleTimeString())",
            -1,                 # length; -1 means "it is nul-terminated"
            None, None, None,   # world, source uri, cancellable
            self.on_evaluated,
        )

    def on_evaluated(self, view: WebKit.WebView, result: Gio.AsyncResult,
                     _data: object = None) -> None:
        try:
            value = view.evaluate_javascript_finish(result)
        except GLib.Error as error:
            self.status.set_text(f"the script failed: {error.message}")
            return

        if value.is_string():
            self.status.set_text(f"the page returned: {value.to_string()}")
        else:
            self.status.set_text(f"the page returned: {value.to_json(0)}")


def on_activate(app: Gtk.Application) -> None:
    Window(application=app).present()


app = Gtk.Application(application_id="com.example.JavaScriptBridge")
app.connect("activate", on_activate)
sys.exit(app.run(sys.argv))
