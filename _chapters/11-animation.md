---
layout: chapter
title: "Animation and Transitions"
number: 11
part: 1
---

> Every listing in this chapter is a file under `examples/gtk4/animation/`. They are
> run on each build, so if one of them stops working the build says so.

## Introduction

The previous edition of this book had a chapter on Clutter — a separate scene
graph, with its own actors, its own stage and its own animation framework, bolted
onto a GTK window. That is not how any of this works now.

**Clutter is gone.** It was folded into GNOME's compositor, deprecated as a public
library, and the parts an application actually needed came back inside GTK 4. GTK
now has a GPU-backed scene graph of its own (GSK), a frame clock, transforms on
every widget, and — through libadwaita — a proper animation API. There is nothing
left to bolt on.

So this chapter is about four ways to make something move, in the order you should
reach for them:

1. **Let a container do it.** Stacks, revealers and navigation views animate their
   own changes.
2. **CSS.** Transitions and keyframes, for anything that is really a style change.
3. **`Adw.Animation`.** Timed or spring-driven, when you are animating a value.
4. **The frame clock.** When you are drawing every frame yourself.

Most applications never get past the first two.

## Transitions you get for free {#transitions}

Nearly all the motion in a well-behaved GTK application is a container animating
its own state change.

```python
stack = Gtk.Stack()
stack.set_transition_duration(400)
stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
stack.add_titled(first_page, "one", "One")
stack.add_titled(second_page, "two", "Two")
```

Changing the visible child now animates. The types include `CROSSFADE`,
`SLIDE_LEFT_RIGHT`, `SLIDE_UP_DOWN`, `OVER_UP` and a rotation, and
`Gtk.StackSwitcher` or `Adw.ViewSwitcher` will drive the stack for you.

`Gtk.Revealer` does the same for showing and hiding one thing:

```python
revealer = Gtk.Revealer()
revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
revealer.set_transition_duration(300)
revealer.set_child(extra_controls)

toggle.bind_property("active", revealer, "reveal-child",
                     GObject.BindingFlags.SYNC_CREATE)
```

That `bind_property` is worth noticing: the revealer's state *is* a property, so
there is no handler to write at all.

libadwaita adds more of the same idea — `Adw.NavigationView` for
push-and-pop navigation, `Adw.OverlaySplitView` for a sidebar that slides away on a
narrow window, `Adw.Carousel` for swipeable pages. All animated, none of it your
code.

The full example is `examples/gtk4/animation/transitions.py`.

## CSS {#css}

GTK styles its widgets with a subset of CSS, and that subset includes transitions
and keyframe animations. For anything that is really a *style* change, this is the
least code:

```css
.swatch {
    background: #3584e4;
    border-radius: 12px;
    transition: background 400ms ease-in-out,
                border-radius 400ms ease-in-out;
}

.swatch:hover      { background: #813d9c; }
.swatch.round      { background: #2ec27e; border-radius: 60px; }

@keyframes pulse {
    from { opacity: 1;    }
    50%  { opacity: 0.35; }
    to   { opacity: 1;    }
}

.pulsing { animation: pulse 1.2s ease-in-out infinite; }
```

Load it once, onto the display rather than onto a widget:

```python
provider = Gtk.CssProvider()
provider.load_from_data(CSS)
Gtk.StyleContext.add_provider_for_display(
    Gdk.Display.get_default(), provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
)
```

After that, animating is `widget.add_css_class("round")` and
`widget.remove_css_class("round")`. The hover state costs nothing at all.

Two things to know. GTK's CSS is a *subset* — there is no layout in it, no
`display`, no `float`, no positioning; it styles widgets that GTK has already laid
out. And the property names are GTK's, so it is worth reading the GTK CSS
documentation rather than assuming the web's.

The GTK Inspector (`GTK_DEBUG=interactive python3 app.py`) has a CSS editor that
applies changes live, which turns styling from a compile-and-look loop into
something interactive.

The full example is `examples/gtk4/animation/css-animation.py`.

## AdwAnimation {#adw-animation}

When you are animating a *value* rather than a style, libadwaita has the API. An
animation is three things: a widget, to borrow a frame clock from; a range of
values; and a **target** that receives each value.

```python
animation = Adw.TimedAnimation.new(
    widget, 0, 380, 900,                            # from, to, milliseconds
    Adw.CallbackAnimationTarget.new(self.on_value),
)
animation.set_easing(Adw.Easing.EASE_IN_OUT_CUBIC)
animation.play()
```

There are two kinds of target, and the second one is the reason to like this API:

```python
Adw.CallbackAnimationTarget.new(fn)                    # fn(value) every frame
Adw.PropertyAnimationTarget.new(widget, "opacity")     # no callback at all
```

A property target writes straight to a GObject property, so fading a widget is an
animation object and nothing else.

`Adw.TimedAnimation` has a fixed duration and an easing curve — around thirty of
them, from `LINEAR` through `EASE_IN_OUT_CUBIC` to `EASE_OUT_BOUNCE`. It can also
repeat and alternate, which covers "flash twice" in one object:

```python
animation.set_alternate(True)
animation.set_repeat_count(2)
```

`Adw.SpringAnimation` has no duration. It simulates a spring and runs until it
settles:

```python
Adw.SpringAnimation.new(
    widget, 0, 380,
    Adw.SpringParams.new(0.6, 1, 180),    # damping ratio, mass, stiffness
    target,
)
```

A damping ratio below 1 overshoots and wobbles; exactly 1 is critically damped and
arrives as fast as it can without overshooting; above 1 crawls in. Springs are the
right choice for anything the user is *dragging*, because a spring can be handed a
starting velocity — `set_initial_velocity()` — and continue naturally from the
gesture that started it. That is why a flicked list decelerates the way it does.

The `done` signal fires when an animation finishes:

```python
animation.connect("done", lambda _a: self.status.set_text("finished"))
```

Calling `play()` on a running animation restarts it. `pause()`, `resume()`,
`reset()` and `skip()` do what they say, and `skip()` jumps straight to the end
value while still emitting `done` — which is the correct way to cancel, because
whatever the animation was setting ends up where it was going.

The full example is `examples/gtk4/animation/adwaita-animations.py`.

## The frame clock {#frame-clock}

For a drawing that changes every frame — a visualiser, a game, a clock with a
sweeping second hand — you want the frame clock directly:

```python
def on_tick(self, widget, frame_clock):
    now = frame_clock.get_frame_time()          # microseconds, monotonic
    if self.start_time is None:
        self.start_time = now

    self.phase = ((now - self.start_time) % PERIOD_US) / PERIOD_US
    widget.queue_draw()
    return GLib.SOURCE_CONTINUE

widget.add_tick_callback(on_tick)
```

**Do not animate with `GLib.timeout_add(16, ...)`.** A timeout is not synchronised
with the display: frames land slightly early or late, and the result judders in a
way that is hard to see in a screenshot and obvious in motion. The frame clock's
`get_frame_time()` is the time the frame will be *displayed*, which is what makes
motion smooth.

Compute position **from elapsed time**, never by adding a step per frame. A frame
can be dropped, and a per-frame increment turns a dropped frame into a permanent
drift; deriving the position from the clock makes a dropped frame invisible.

The callback runs until it returns `GLib.SOURCE_REMOVE`, and stops on its own when
the widget is unmapped. Keep the id from `add_tick_callback()` if you want to stop
it yourself with `remove_tick_callback()`.

The full example is `examples/gtk4/animation/frame-clock.py`.

## Moving a whole widget {#widget-transforms}

Every widget has a transform, applied by its parent when it is snapshotted. To
move, rotate or scale one without touching its layout, override `do_snapshot()`
and transform the snapshot before chaining up:

```python
def do_snapshot(self, snapshot):
    snapshot.save()
    snapshot.translate(Graphene.Point().init(self.offset, 0))
    snapshot.rotate(self.angle)
    Gtk.Widget.do_snapshot(self, snapshot)
    snapshot.restore()
```

Combine that with an `Adw.CallbackAnimationTarget` that sets `self.angle` and
calls `queue_draw()`, and you have any transform animation you like — running on
the GPU, with no re-layout, at any scale factor.

This is what Clutter's actors were for, and it is now three lines in a widget you
already have.

## Respecting the user {#reduced-motion}

Some people get motion sickness from animated interfaces, and every desktop has a
setting for it. Honour it.

GTK's own transitions already do. If you write your own, check:

```python
settings = Gtk.Settings.get_default()
if settings.get_property("gtk-enable-animations"):
    animation.play()
else:
    animation.skip()          # jump to the end value, no motion
```

`skip()` rather than not playing, so whatever the animation was setting still ends
up where it should be.

In CSS, the same preference is the media query browsers use:

```css
@media (prefers-reduced-motion: reduce) {
    .swatch  { transition: none; }
    .pulsing { animation: none; }
}
```

Two more habits worth keeping. Animation durations belong in the 150–400 ms range;
anything slower stops feeling responsive and starts feeling broken. And never
animate something the user is waiting on — a spinner during a two-second load is
fine, a 600 ms slide before a menu opens is not.

## Summary

- Clutter is gone. GTK 4 has the scene graph, the frame clock and the transforms;
  libadwaita has the animation API.
- Reach for a container transition first, CSS second, `Adw.Animation` third, the
  frame clock last.
- `Adw.PropertyAnimationTarget` animates a GObject property with no callback at all.
- Springs take an initial velocity, which is what makes gesture-driven motion feel
  continuous.
- Use `add_tick_callback()`, not a 16 ms timeout, and derive position from elapsed
  time rather than accumulating per frame.
- Transform a whole widget by transforming its snapshot before chaining up.
- Check `gtk-enable-animations` and `prefers-reduced-motion`, and cancel with
  `skip()`.

[Embedding Web Content](12-web-content.html) is next.
