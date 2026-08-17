#!/usr/bin/env python3
"""A video player, the short way.

GTK 4 has media playback built in. GtkMediaFile is backed by GStreamer, and
GtkVideo is a widget that shows a GtkMediaStream with the usual controls. For
playing a file in an application window, this is all you need -- no pipeline, no
bus, no video sink to wire into a widget.

The chapter's other examples show the pipeline underneath, for when you need it.
"""

import sys
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GObject, Gtk

from sample_media import ensure_sample


class Player(Gtk.ApplicationWindow):
    def __init__(self, path, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.set_title("Video Player")
        self.set_default_size(480, 400)

        self.media = Gtk.MediaFile.new_for_file(Gio.File.new_for_path(str(path)))
        self.media.set_loop(True)

        video = Gtk.Video(media_stream=self.media)
        video.set_vexpand(True)

        # GtkGraphicsOffload (GTK 4.14) asks the compositor to put the video on
        # its own hardware plane instead of compositing every frame into the
        # window. When it works the frames never pass through GTK's renderer at
        # all, which is a large saving in power on a laptop and the difference
        # between smooth and not on a slow GPU. When it does not work -- the
        # wrong format, the wrong compositor, anything drawn on top -- it
        # silently falls back to ordinary rendering, so it is safe to ask for.
        offload = Gtk.GraphicsOffload(child=video)
        offload.set_enabled(Gtk.GraphicsOffloadEnabled.ENABLED)
        offload.set_vexpand(True)

        self.position = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 0.001)
        self.position.set_draw_value(False)
        self.seeking = False
        self.position.connect("value-changed", self.on_seek)

        self.time = Gtk.Label(label="0:00 / 0:00")

        play = Gtk.Button(icon_name="media-playback-start-symbolic")
        play.connect("clicked", lambda _b: self.media.play())
        pause = Gtk.Button(icon_name="media-playback-pause-symbolic")
        pause.connect("clicked", lambda _b: self.media.pause())

        volume = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 0.05)
        volume.set_value(self.media.get_volume())
        volume.set_size_request(120, -1)
        volume.connect("value-changed", lambda s: self.media.set_volume(s.get_value()))

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        for widget in (play, pause, self.position, self.time,
                       Gtk.Image.new_from_icon_name("audio-volume-high-symbolic"),
                       volume):
            controls.append(widget)
        self.position.set_hexpand(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_margin_top(6)
        box.set_margin_bottom(6)
        box.set_margin_start(6)
        box.set_margin_end(6)
        box.append(offload)
        box.append(controls)
        self.set_child(box)

        # A media stream reports through properties, not signals.
        self.media.connect("notify::timestamp", self.on_timestamp)
        self.media.connect("notify::error", self.on_error)

        self.media.play()

    def on_timestamp(self, media: Gtk.MediaStream, _pspec: GObject.ParamSpec) -> None:
        duration = media.get_duration()
        if duration <= 0:
            return
        fraction = media.get_timestamp() / duration

        # Do not fight the user: only move the slider when they are not holding it.
        if not self.seeking:
            self.position.handler_block_by_func(self.on_seek)
            self.position.set_value(fraction)
            self.position.handler_unblock_by_func(self.on_seek)

        self.time.set_text(
            f"{format_time(media.get_timestamp())} / {format_time(duration)}"
        )

    def on_seek(self, scale: Gtk.Scale) -> None:
        duration = self.media.get_duration()
        if duration > 0 and self.media.is_seekable():
            self.media.seek(int(scale.get_value() * duration))

    def on_error(self, media: Gtk.MediaStream, _pspec: GObject.ParamSpec) -> None:
        error = media.get_error()
        if error is not None:
            self.time.set_text(f"error: {error.message}")


def format_time(microseconds: int) -> str:
    seconds = int(microseconds // 1_000_000)
    return f"{seconds // 60}:{seconds % 60:02d}"


def on_activate(app: Gtk.Application) -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else ensure_sample()
    Player(path, application=app).present()


app = Gtk.Application(
    application_id="com.example.VideoPlayer",
    flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
)
app.connect("activate", on_activate)
app.connect("command-line", lambda a, cl: (a.activate(), 0)[1])
sys.exit(app.run(sys.argv))
