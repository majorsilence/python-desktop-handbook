#!/usr/bin/env python3
"""What is in a media file, without playing it.

GstDiscoverer opens a file, works out the container, the streams and the codecs,
and reports whether anything needed to decode it is missing.
"""

import sys

import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstPbutils", "1.0")
from gi.repository import Gst, GstPbutils

from sample_media import ensure_sample

Gst.init(None)


def describe(info):
    caps = info.get_caps()
    # A human-readable codec name, rather than the raw caps string.
    name = GstPbutils.pb_utils_get_codec_description(caps) if caps else "unknown"

    if isinstance(info, GstPbutils.DiscovererVideoInfo):
        return (f"video: {name}, {info.get_width()}x{info.get_height()}, "
                f"{info.get_framerate_num() / max(1, info.get_framerate_denom()):.3g} fps")

    if isinstance(info, GstPbutils.DiscovererAudioInfo):
        return (f"audio: {name}, {info.get_channels()} channel(s), "
                f"{info.get_sample_rate()} Hz")

    if isinstance(info, GstPbutils.DiscovererSubtitleInfo):
        return f"subtitles: {name} ({info.get_language()})"

    return f"other: {name}"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else str(ensure_sample())
    uri = Gst.filename_to_uri(path)

    # The timeout is a hard limit: a discoverer that cannot make sense of a stream
    # will otherwise sit there.
    discoverer = GstPbutils.Discoverer.new(5 * Gst.SECOND)

    try:
        info = discoverer.discover_uri(uri)
    except Exception as error:            # GLib.Error, or a plain failure
        print(f"could not read {path}: {error}")
        return 1

    result = info.get_result()
    print(f"{path}")
    print(f"  result:   {result.value_nick}")
    print(f"  duration: {info.get_duration() / Gst.SECOND:.2f} s")
    print(f"  seekable: {info.get_seekable()}")

    for stream in info.get_stream_list():
        print(f"  {describe(stream)}")

    if result == GstPbutils.DiscovererResult.MISSING_PLUGINS:
        # These strings are what the codec installer takes; see missing-codecs.py.
        for detail in info.get_missing_elements_installer_details():
            print(f"  missing: {detail}")

    # Tags live on the individual streams. DiscovererInfo.get_tags(), which merged
    # them all, is deprecated.
    for stream in info.get_stream_list():
        tags = stream.get_tags()
        if tags is None:
            continue
        for tag in (Gst.TAG_TITLE, Gst.TAG_ARTIST, Gst.TAG_ALBUM, Gst.TAG_ENCODER):
            found, value = tags.get_string(tag)
            if found:
                print(f"  {tag}: {value}")

    return 0


sys.exit(main())
