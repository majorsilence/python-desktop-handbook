#!/usr/bin/env python3
"""A GStreamer pipeline built by hand, and the bus that reports on it.

Three ideas cover most of GStreamer:

  elements   do one thing -- read a file, decode, resample, play
  pads       connect them, and negotiate what format flows between them
  the bus    carries messages back out of the pipeline to your main loop

Nothing here needs a window, so it runs on any machine with GStreamer.
"""

import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

Gst.init(None)


def build() -> Gst.Element:
    """audiotestsrc -> audioconvert -> fakesink, wired up one element at a time."""
    pipeline = Gst.Pipeline.new("tone")

    source = Gst.ElementFactory.make("audiotestsrc", "source")
    convert = Gst.ElementFactory.make("audioconvert", "convert")
    sink = Gst.ElementFactory.make("fakesink", "sink")

    if not all((pipeline, source, convert, sink)):
        raise SystemExit("an element is missing; is gst-plugins-base installed?")

    source.set_property("num-buffers", 50)
    source.set_property("freq", 440)
    sink.set_property("sync", False)      # go as fast as the CPU allows

    for element in (source, convert, sink):
        pipeline.add(element)

    # link() fails if the two elements cannot agree on a format.
    if not source.link(convert) or not convert.link(sink):
        raise SystemExit("the elements would not link")

    return pipeline


def on_message(_bus: Gst.Bus, message: Gst.Message, loop: GLib.MainLoop) -> bool:
    """Messages arrive on the main loop, not on the streaming thread."""
    kind = message.type

    if kind == Gst.MessageType.EOS:
        print("end of stream")
        loop.quit()

    elif kind == Gst.MessageType.ERROR:
        error, debug = message.parse_error()
        print(f"error: {error.message}")
        print(f"debug: {debug}")
        loop.quit()

    elif kind == Gst.MessageType.WARNING:
        warning, _debug = message.parse_warning()
        print(f"warning: {warning.message}")

    elif kind == Gst.MessageType.STATE_CHANGED:
        # Every element reports its own changes; usually only the pipeline's matter.
        if message.src is pipeline:
            old, new, _pending = message.parse_state_changed()
            print(f"pipeline: {old.value_nick} -> {new.value_nick}")

    return True          # stay subscribed


pipeline = build()
loop = GLib.MainLoop()

bus = pipeline.get_bus()
bus.add_signal_watch()               # without this, no messages reach the loop
bus.connect("message", on_message, loop)

# States go NULL -> READY -> PAUSED -> PLAYING, and set_state() may return
# ASYNC, meaning "I have started; watch the bus".
if pipeline.set_state(Gst.State.PLAYING) == Gst.StateChangeReturn.FAILURE:
    raise SystemExit("the pipeline would not start")

try:
    loop.run()
except KeyboardInterrupt:
    pass
finally:
    # Always come back to NULL: it is what releases the audio device and the file
    # handles. Leaving a pipeline in PLAYING at exit leaks both.
    pipeline.set_state(Gst.State.NULL)

sys.exit(0)
