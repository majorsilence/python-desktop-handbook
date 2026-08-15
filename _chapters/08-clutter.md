---
layout: chapter
title: "Clutter"
number: 8
---

> Please send any fixes or suggestions to peter@majorsilence.com or leave a comment at http://www.majorsilence.com/pygtk\_book.

## Introduction

Note: This chapter is about pyclutter 1.0 and no longer contains information on older versions.

The best way to describe clutter is to quote its home page which states:

Clutter is an open source software library for creating fast, visually rich and animated graphical user interfaces.

Clutter can be integrated with many Linux technologies including GStreamer, Cairo a GTK+. It also is portable and runs on Windows and OSX which allows for cross platform goodness.

But how is clutter used? This is actually very simple. Instead of creating a gtk.Window as with using PyGTK, with clutter a clutter.Stage is created. And instead of using widgets, Actors are used. This is actually rather neat. We have Stages on which to do our work and Actors that perform.

Some base Actors included with clutter are:

- Texture
- CloneTexture
- Text - For all things text. Replaces Label and Entry
- Rectangle - For creating Rectangles
- Label - displaying Labels (deprecated as of 1.0)
- Entry - For entering text (deprecated as of 1.0)

A stage is created by using the clutter.Stage object like so:

```python
stage = clutter.Stage()
```

The size of stage can be set:

```python
stage.set_size(800, 400)
```

The title of the stage can be set using the stage.set\_title() method:

```python
stage.set_title("Hey Hey, My First Clutter App")
```

To make sure that a clutter application is shut down properly make sure to add

```python
stage.connect('destroy', clutter.main_quit)
```

## Colors

The colour of a stage can be set using set\_color() method and using the clutter.color\_from\_string()[^1] method. The clutter parse method can take several different colour inputs including the colours as Text or RGB Notation.

The colour of a stage can be set:

```python
stage.set_color(clutter.color_from_string("red"))
stage.set_color(clutter.Color(255, 0, 0))
```

Colours can be applied to more then just stages, they may also be applied to all the Actors that will be shown in the next section.

## User Input

### Keyboard

It is very easy to catch user input. For catching keyboard events the stage must connect the "key-press-event" to a handler.

```python
# key-press-event is for the keyboard
stage.connect("key-press-event", on_key_press_event)

def on_key_press_event(self, stage, event):
    # event has the following:
    # event.hardware_keycode
    # event.keyval - ascii (or unicode) value of the key
    # event.modifier_state
    # event.put
    # event.source
    # event.time
    # event.type

    print "keyval ", event.keyval
    try:
        print "key pressed ", chr(event.keyval)
    except ValueError:
        print "Key pressed not recognized ascii character."
        print "Returning from key pressed function"
        return
```

What is probably going to be the most useful when handling a key press event is the character pressed. The event.keval can be converted using the builtin function *chr*. For example in ascii 97 is a. So if we press a and have the following code

```python
print chr(event.keyval)
```

an "a" will be printed to the screen.

### Mouse

Catching input from a mouse is also very easy and all that needs to be done is to handle the "button-press-event". The handler function takes two arguments "stage" and "event" and is handled like so:

```python
stage.connect("button-press-event", on_button_press_event)

def on_button_press_event (stage, event):
    #mouse button
    #event.button - 1 left click
    #             - 3 right click
    #             - 2 left and right clicked same time
    #
    # event.x - X Coordinate of button press
    # event.y - Y Coordinate of button press
    #
    print "mouse button %d pressed at (%d, %d)" % (event.button, event.x, event.y)
```

## Actors

### Text {#sub-clutter-actor-text}

```python
class clutter.Text(clutter.Actor)
    get_text()
    set_text(text) - Sets the text in the entry
    set_editable(Boolean)
    set_reactive(Boolean)
    set_position(xPos, yPos)
    ...
```

You can set text in it using the set\_text(text) method and get text using the get\_text() method. If you want to use the Text actor as a label you would set it to *set\_editable(False)*. Here is an example with a Text actor being created and added to a stage. You will have to click on the Text actor to be able to type in it, just like a normal gtk or windows text field.

```python
class EntryExample:
    def __init__(self):
       self.stage = clutter.Stage()
       self.stage.set_size(400, 400)
       self.stage.set_color(clutter.color_from_string("red"))
       self.text = clutter.Text()
       self.text.set_text("Text Entry")
       self.text.set_color(clutter.color_parse("green"))
       self.text.set_size(150, 50)
       self.text.set_position(200, 200)
       self.text.set_reactive(True)
       self.text.set_editable(True)

       self.text.connect("button-press-event",
          self.on_mouse_press_event)
       self.text.connect("key-press-event",
          self.on_key_press_event)
       self.stage.connect('destroy',
          clutter.main_quit)

        self.stage.add(self.text)
        self.stage.show_all()

    def on_mouse_press_event(self, actor, event):
       self.stage.set_key_focus(self.text)
       return False

    def on_key_press_event(self, actor, event):
        print "Text Actor is: ", actor.get_text()
        print "Key pressed is: ", unichr(event.keyval)

if __name__ == "__main__":
    app = EntryExample()
    clutter.main()
```

As can be seen in the code above the stage color is set to red, the text color in the Text actor is set to green. The text actor is set to have width of 150 and a height of 50. The position of the Text actor on the stage is set to x 200 y 200. The actor is also set to be editable and reactive. Simple enough.

Three call back functions are added. One callback for when a mouse button is pressed over the Text actor. One callback event for when a key is pressed on the keyboard while the focus is in the Text actor. Finally the last callback event is for the stage destroy signal which is connected above to `clutter.main_quit` to insure the program exits properly.

### Rectangles

```python
class clutter.Rectangle(clutter.Actor):
    clutter.Rectangle(color=None)
    get_color()
    set_color(color)
    get_border_color()
    set_border_color(color)
    get_border_width()
    set_border_width(width)
```

Creating rectangles does not entail much. Basically you just call the clutter.Rectangle class and you are done. Of course you will probably want to do more to it then that and add it to a stage. As can be seen in the class outline of a clutter.Rectangle above there is not much to work with in and of themselves making them easy to work with.

Setting a border width on a Rectangle will increase its size bye the border size multiplied by 2. So if your rectangle is set to 200 wide and you add a border of 20 you end up with a rectangle that is 240 wide.

### Textures

```python
class clutter.Texture(Actor)
        set_area_from_rgb_data(data, has_alpha, x, y, width, height, rowstride, bpp, flags, error)
            - Updates a sub-region of the pixel data in a Texture.
        set_from_rgb_data(data, has_alpha, width, height, rowstride, bpp, flags, error)
            - Sets the Texture from RBG data.
        set_from_yuv_data(data, width, height, flags, error)
            - Sets the Texture from a YUV image data.
        set_from_file(filename, error) - obvious
        set_filter_quality(filter_quality)
        ...
```

Loading an image file and setting it up as a texture is very simple.

```python
purple_flower = clutter.Texture(filename="flower.jpg")
```

Look at that, only one line of code and we have a texture that is ready to be used in our pyclutter program. Now all that needs to be done is add the purple\_flower to the stage.

```python
import clutter
stage = clutter.Stage()
stage.set_size(400, 400)

purple_flower = clutter.Texture(filename="flower.jpg")
(width, height) = purple_flower.get_size()
stage.add(purple_flower)

stage.show_all()
stage.connect('destroy', clutter.main_quit)
clutter.main()
```

#### Cloning a textue

```python
class clutter.CloneTexture(Actor)
    get_parent_texture()
    set_parent_texture(Texture)
```

Cloning a texture is as easy to create as the original texture.

```python
# Create the original Texture
purple_flower = clutter.Texture(filename="flower.jpg")

# Create the cloned Texture
clone = clutter.CloneTexture(purple_flower)
```

And it is that simple. Now the actual work starts with making the texture do what it is supposed to be doing. It should probably be properly placed, maybe have some behaviours (this is discussed later), setting up time lines.

Lets make the Texture and the cloned texture show up on the stage now.

```python
clone.set_position(200, 200)
stage.add(purple_flower, clone)
stage.show_all()
stage.connect('destroy', clutter.main_quit)
```

Now the the original texture is in the upper most left corner of the stage and the clone is displayed at coordinates x 200 and y 200.

```python
import clutter

def create_texture(fName):
    image = clutter.Texture(filename=fName)
    (width, height) = image.get_size()
    return image

stage = clutter.Stage()
stage.set_size(400, 400)

# Create the original Texture from a picture of a flower
purple_flower = create_texture("flower.jpg")

# Create a clone of the origial Texture cloned_flower = clutter.CloneTexture(purple_flower)
cloned_flower.set_position(200, 200)

stage.add(purple_flower, cloned_flower) stage.show_all() stage.connect('destroy', clutter.main_quit)
clutter.main()
```

### Labels

Labels have been deprecated and as of pyclutter 1.0 you they should not be used. Instead the Text actor should be used and will be demonstrated here. To see more about the Text actor please see [Text](08-clutter.html#sub-clutter-actor-text).

```python
class clutter.Text
    set_text(text)
    set_editable(Boolean)
    set_color(color)
    ....
```

So here is the example of use Text as a label. Bascially all that is being done is using the method *set\_editable(False)* to make sure users cannot change the text.

```python
import clutter

stage = clutter.Stage()
stage.set_size(400, 400)

label = clutter.Text()
label.set_editable(False)
label.set_text("Clutter Label Text")
label.set_color(clutter.color_from_string("brown"))

# If no position is given it defaults to the upper most left corner.
stage.add(label)
stage.show_all()
stage.connect('destroy', clutter.main_quit)
clutter.main()
```

## Animations

### Timelines {#sub-clutter-timelines}

```python
class clutter.Timeline:
     __init__(duration)
         fps - Frames per second
         num_frames - The total number of frames
         duration - The duration of the timeline, in milliseconds
    def get_duration()
    def set_duration(msecs)
    def get_direction() - retrieves the direction of the timeline, either forward or backward.
    def set_direction()
    def get_loop()
    def set_loop(True or False) - Set the timeline to loop
    def get_progress()
    def start() - Start the timeline
    def pause() - Pause the timeline
    def stop()
    def rewind()
```

To use a time line you will want to add it to a clutter actor. The timeline is setup and then the animation effect that it is to be applied to it.

So lets create a time line with a duration of 3000(3 seconds).

```python
timeline = clutter.Timeline(duration=3000)
```

Next we will set the timeline to loop using the set\_loop() method. This sets the timeline to loop once it has finished each run through.

```python
timeline.set_loop(True)
```

### Alpha {#sub-clutter-alpha}

```python
class clutter.Alpha(goject.GObject)
    clutter.Alpha(timeline, func, data)
        def get_alpha()
        def get_timeline()
        def set_func(func)
        def set_timeline(timeline)
```

Next if you want to apply an animation you will want to setup the effect that is going to happen to your chosen object. So what is going to happen now is to create a clutter.Alpha object. Then create a clutter.BehaviourOpacity object using our just created alpha and apply this action to our rectangle. Then start the timeline running which will start the animation.

```python
alpha = clutter.Alpha(timeline, clutter.EASE_IN_OUT_BOUNCE)
behaviour = clutter.BehaviourOpacity(0xdd, 0, alpha)
behaviour.apply(rect)

# start the timeline running, thus starting the animation
timeline.start()
```

The timeline can be setup anywhere and then started at any time using the timeline.start() method and stopped with the timeline.stop() method.

If we put all this together we get a working application that is only a few lines long.

What is needed to be known about clutter.Alpha is that it is a function of time not pixel form of alpha.

There are many predefined Clutter.Alpha functions that can be used with the clutter.Alpha class to effect the behaviour of the timeline. You will just have to experiment with them to see what suits your needs.

- clutter.EASE\_IN\_OUT\_BOUNCE
- clutter.EASE\_IN\_BACK
- clutter.EASE\_IN\_BOUNCE
- clutter.EASE\_IN\_CIRC
- clutter.EASE\_IN\_CUBIC
- clutter.EASE\_IN\_ELASTIC
- clutter.EASE\_IN\_EXPO
- clutter.EASE\_IN\_OUT\_BACK
- clutter.EASE\_IN\_OUT\_CIRC
- clutter.EASE\_IN\_OUT\_CUBIC
- clutter.EASE\_IN\_OUT\_ELASTIC
- clutter.EASE\_IN\_OUT\_EXPO
- clutter.EASE\_IN\_OUT\_QUAD
- clutter.EASE\_IN\_OUT\_QUART
- clutter.EASE\_IN\_OUT\_QUINT
- clutter.EASE\_IN\_OUT\_SINE
- clutter.EASE\_IN\_QUAD
- clutter.EASE\_IN\_QUART
- clutter.EASE\_IN\_QUINT
- clutter.EASE\_IN\_SINE
- clutter.EASE\_OUT\_BACK
- clutter.EASE\_OUT\_BOUNCE
- clutter.EASE\_OUT\_CIRC
- clutter.EASE\_OUT\_CUBIC
- clutter.EASE\_OUT\_ELASTIC
- clutter.EASE\_OUT\_EXPO
- clutter.EASE\_OUT\_QUAD
- clutter.EASE\_OUT\_QUART
- clutter.EASE\_OUT\_QUINT
- clutter.EASE\_OUT\_SINE

### BehaviourOpacity {#sub-clutter-behaviouropacity}

Please see the section [Alpha](08-clutter.html#sub-clutter-alpha) before reading this section. Using Behaviour Opacity

```python
import clutter

class Blinker:
    def __init__(self):
        self.stage = clutter.Stage()
        self.stage.set_color(clutter.color_from_string("red"))
        self.stage.set_size(400, 400)
        self.stage.set_title("My Blinking (BehaviourOpacity) Rectangle Example")

        self.rect = clutter.Rectangle()
        self.rect.set_color(clutter.color_from_string("green"))
        self.rect.set_size(200, 200)

        rect_xpos = self.stage.get_width() / 4
        rect_ypos = self.stage.get_height() / 4

        self.rect.set_position(rect_xpos, rect_ypos)
        self.timeline = clutter.Timeline(duration=3000)
        self.timeline.set_loop(True)

        alpha = clutter.Alpha(self.timeline, clutter.EASE_IN_OUT_SINE)
        self.behaviour = clutter.BehaviourOpacity(alpha=alpha , opacity_start=0xdd, opacity_end=0)
        self.behaviour.apply(self.rect)
        self.timeline.start()

        self.stage.add(self.rect)
        self.stage.show_all()
        self.stage.connect('destroy', clutter.main_quit)

if __name__ == "__main__":
    app = Blinker()
    clutter.main()
```

### BehaviourRotate {#sub-clutter-behaviourrotate}

```python
class clutter.BehaviourRotate(Behaviour)
    clutter.BehaviourRotate(alpha(optional),  angle_end, angle_start)
        def get_axis()
        def set_axis(axis)
            -clutter.Z_AXIS
            -clutter.Y_AXIS
            -clutter.X_AXIS
        get_bounds(angle_start, angle_end)
        set_bounds(angle_start, angle_end)
        get_center(x, y, z)
        set_center(x, y, z)
        get_direction()
        set_direction(direction)
        ...
```

The clutter.BehaviourRotate class allows you to set a rotate behaviour on an a chosen actor.

The example that is to follow will create a Rectangle and add it to a stage and then we will create a time line. The timeline will control a BehaviourRotate that will affect the Rectangle (though any Actor will do).

At this point I will assume you know how to create a rectangle and add it to a stage, so from this point out I will just focus on the Behaviours.

So we have to create a timeline that will control the behaviour.

```python
timeline = clutter.Timeline(duration=3000)
timeline.set_loop(True)
alpha = clutter.Alpha(timeline, clutter.EASE_IN_OUT_SINE)
```

Now that the timeline that is going to be used with the behaviour has been created we can create the behaviour itself. You will should notice that the axis is set to clutter.Z\_AXIS, also available are clutter.X\_AXIS and clutter.Y\_AXIS.

```python
rotate_behaviour = clutter.BehaviourRotate(axis=clutter.Z_AXIS, angle_start=0.0, angle_end=359.0)
rotate_behaviour.set_alpha(alpha)
rotate_behaviour.apply(rect)
```

So a instance of BehaviourRotate is created, rotating on the z axis, using the alpa timeline created above and this is applied to the rectangle instance rect.

```python
import clutter

stage = clutter.Stage()
stage.set_size(400, 400)
rect = clutter.Rectangle()
rect.set_color(clutter.color_from_string("red"))
rect.set_size(100, 100) rect.set_position(150, 150)

timeline = clutter.Timeline(duration=3000)
timeline.set_loop(True)
alpha = clutter.Alpha(timeline, clutter.EASE_IN_OUT_SINE)

rotate_behaviour = clutter.BehaviourRotate(
    axis=clutter.Z_AXIS, angle_start=0.0, angle_end=359.0)
rotate_behaviour.set_alpha(alpha)
rotate_behaviour.apply(rect)
timeline.start()

stage.add(rect)
stage.show_all()
stage.connect('destroy', clutter.main_quit)
clutter.main()
```

### BehaviourScale - Not Finished {#sub-clutter-behaviourscale}

```python
class clutter.BehaviourScale(Behaviour)
    clutter.BehaviourScale(x_scale_start, y_scale_start, x_scale_end, y_scale_end, alpha(optional) )
        def get_bounds()
        def set_bounds(x_scale_begin, y_scale_begin, x_scale_end, y_scale_end)
```

### BehaviourDepth {#sub-clutter-behaviourdepth}

```python
class clutter.BehaviourDepth
    clutter.BehaviourDepth(depth_start, depth_end)
        def set_bounds(depth_start, depth_end)
        def get_bounds(depth_start, depth_end)
```

BehaviourDepth works like the other behaviours that have been discussed above. You create your behaviour specifying your desired action and attach it to a timeline.

With BehaviourDepth the only options (and required) are the start depth and end depth. Play around with them a little to get your desired result.

```python
timeline = clutter.Timeline(duration=6000)
timeline.set_loop(True)
alpha = clutter.Alpha(timeline, clutter.EASE_IN_OUT_SINE)

rotate_behaviour = clutter.BehaviourDepth(0, 250)
rotate_behaviour.set_alpha(alpha)
rotate_behaviour.apply(rect)
```

All you have to do to start the required behaviour is start the time line and watch the results.

```python
import clutter

stage = clutter.Stage()
stage.set_size(400, 400)
rect = clutter.Rectangle()
rect.set_color(clutter.color_from_string("red"))
rect.set_size(100, 100) rect.set_position(150, 150)

timeline = clutter.Timeline(duration=6000)
timeline.set_loop(True) alpha = clutter.Alpha(
    timeline, clutter.EASE_OUT_BOUNCE)

rotate_behaviour = clutter.BehaviourDepth(0, 250)
rotate_behaviour.set_alpha(alpha)
rotate_behaviour.apply(rect)
timeline.start()

stage.add(rect)
stage.show_all()
stage.connect('destroy', clutter.main_quit)
clutter.main()
```

## Groups and Positioning {#sec-clutter-groups-and-positioning}

Groups allow the programmer to group together many actors. Instead of the Actor references the colors and position of the stage, they reference off of the group that they are in. Groups also allow for relative positioning, as in the positions of Actors are placed relative to their parent Group.

For example if you have a Rectangle and it is inside Group when you set the position of the rectangle to (100, 100), it is relative to the position of the group. So in the following snippet of code, the Rectangle is is being set to (100, 100) in the Group but relative to the stage it is set to (200, 200)

```python
group = clutter.Group()
group.set_position(100, 100)

rect = clutter.Rectangle()
rect.set_size(100, 100)
rect.set_position(100, 100)
group.add(rect)
```

## Summary

For more information about clutter you can visit its web site at:

<http://www.clutter-project.org>

For more information on the pyclutter api you can download the pyclutter source from the clutter project site and view the documentation or load the documentation in a python console using:

```python
import clutter
help(clutter)
```

Also for each section of pyclutter covered in this chapter full source examples are on the books website. You are encouraged to download and inspect these and expand upon them to further learn how to best use clutter for your own projects. The address for these downloads is <http://www.majorsilence.com/rubbish/pygtk-book/examples/>.

[^1]: Formally clutter.color\_parse(...)
