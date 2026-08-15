"""Make a short test clip, so the other examples have something to play.

Rather than shipping a video file, the examples generate one with GStreamer's own
test sources. gst-launch-1.0 would write it in one line:

    gst-launch-1.0 -e videotestsrc num-buffers=90 ! video/x-raw,width=320,height=240 \
        ! vp8enc ! webmmux name=mux ! filesink location=sample.webm \
        audiotestsrc num-buffers=130 ! vorbisenc ! mux.

parse_launch() takes the same string, which makes it a good way to prototype a
pipeline before building it element by element.
"""

import pathlib

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

Gst.init(None)

SAMPLE = pathlib.Path(__file__).parent / "sample.webm"

PIPELINE = """
  videotestsrc num-buffers=90 pattern=smpte
    ! video/x-raw,width=320,height=240,framerate=30/1
    ! vp8enc deadline=1
    ! webmmux name=mux
    ! filesink location={path}
  audiotestsrc num-buffers=130 wave=sine freq=440
    ! audioconvert
    ! vorbisenc
    ! mux.
"""


def ensure_sample():
    """Return the path to a three-second test clip, making it if need be."""
    if SAMPLE.exists():
        return SAMPLE

    pipeline = Gst.parse_launch(PIPELINE.format(path=SAMPLE))
    pipeline.set_state(Gst.State.PLAYING)

    # Wait for the file to be finished, or for an error, whichever comes first.
    bus = pipeline.get_bus()
    message = bus.timed_pop_filtered(
        30 * Gst.SECOND, Gst.MessageType.EOS | Gst.MessageType.ERROR
    )

    # An EOS has to reach the muxer for the file to have a usable header, so send
    # one explicitly before tearing the pipeline down.
    pipeline.send_event(Gst.Event.new_eos())
    pipeline.set_state(Gst.State.NULL)

    if message is not None and message.type == Gst.MessageType.ERROR:
        error, debug = message.parse_error()
        raise SystemExit(f"could not build the sample: {error.message}\n{debug}")

    if not SAMPLE.exists():
        raise SystemExit("the sample was not written")
    return SAMPLE


if __name__ == "__main__":
    print("wrote", ensure_sample())
