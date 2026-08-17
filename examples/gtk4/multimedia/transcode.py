#!/usr/bin/env python3
"""Converting one file into another, with progress.

This is the pattern for any job GStreamer does in the background: build a
pipeline, put it on the bus, poll for position, and come back to NULL at the end.
uridecodebin3 works out how to decode whatever it is given, so the same pipeline
converts anything the installed plugins can read.
"""

import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

from sample_media import ensure_sample

Gst.init(None)

# uridecodebin, not uridecodebin3. The two look interchangeable and are not: the
# newer one is built for playback with stream selection, and in a pipeline that
# ends in a muxer it links up perfectly and then never propagates EOS -- so the
# muxer never finalises the file and the job hangs at around 90%.
#
# decodebin has no output pads until it has seen the stream, so the encoders are
# linked in a pad-added handler rather than up front.
PIPELINE = """
  uridecodebin name=source uri={uri}
  theoraenc name=videoenc ! oggmux name=mux ! filesink location={out}
  vorbisenc name=audioenc ! mux.
  videoconvert name=videoconv ! videoenc.
  audioconvert name=audioconv ! audioenc.
"""


def on_pad_added(_element: Gst.Element, pad: Gst.Pad, pipeline: Gst.Element) -> None:
    """Route each stream that appears into the right converter.

    A new pad may have no *current* caps yet if nothing has flowed through it, so
    fall back to asking what it is willing to carry, which is enough to tell audio
    from video.
    """
    caps = pad.get_current_caps() or pad.query_caps(None)
    if caps is None or caps.is_empty():
        return
    kind = caps.to_string().split(",")[0]

    if kind.startswith("video/"):
        target = pipeline.get_by_name("videoconv")
    elif kind.startswith("audio/"):
        target = pipeline.get_by_name("audioconv")
    else:
        return

    sink_pad = target.get_static_pad("sink")
    if not sink_pad.is_linked():
        result = pad.link(sink_pad)
        if result != Gst.PadLinkReturn.OK:
            print(f"could not link {kind}: {result.value_nick}")


def report_progress(pipeline: Gst.Element) -> bool:
    ok, position = pipeline.query_position(Gst.Format.TIME)
    ok2, duration = pipeline.query_duration(Gst.Format.TIME)
    if ok and ok2 and duration > 0:
        print(f"\r{100 * position / duration:5.1f}%", end="", flush=True)
    return GLib.SOURCE_CONTINUE


def main() -> int:
    source = sys.argv[1] if len(sys.argv) > 1 else str(ensure_sample())
    output = sys.argv[2] if len(sys.argv) > 2 else "transcoded.ogg"

    pipeline = Gst.parse_launch(
        PIPELINE.format(uri=Gst.filename_to_uri(source), out=output)
    )
    pipeline.get_by_name("source").connect("pad-added", on_pad_added, pipeline)

    loop = GLib.MainLoop()
    status = {"code": 0}

    def on_message(_bus: Gst.Bus, message: Gst.Message,
                   _data: object = None) -> bool:
        if message.type == Gst.MessageType.EOS:
            loop.quit()
        elif message.type == Gst.MessageType.ERROR:
            error, debug = message.parse_error()
            print(f"\nerror: {error.message}\n{debug}")
            status["code"] = 1
            loop.quit()
        return True

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message)

    pipeline.set_state(Gst.State.PLAYING)
    progress = GLib.timeout_add(200, report_progress, pipeline)

    try:
        loop.run()
    finally:
        GLib.source_remove(progress)
        pipeline.set_state(Gst.State.NULL)

    if status["code"] == 0:
        print(f"\rwrote {output}          ")
    return status["code"]


sys.exit(main())
