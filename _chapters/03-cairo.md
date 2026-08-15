---
layout: chapter
title: "Cairo"
number: 3
---

> Please send any fixes or suggestions to peter@majorsilence.com or leave a comment at http://www.majorsilence.com/pygtk\_book.

## Introduction

Welcome to the chapter on cairo. What is cairo? Cario is a powerful 2d graphics library that lets you output to many different surfaces. Surfaces that are supported include image surfaces (png) pdf, postscript, win32, svg, quartz, and xlib. What all these different surfaces achieve will be discussed throughout the chapter; however every surface type here supports writing to png. Besides including png write support, cairo also includes png import support.

While reading about cairo in other sources you may find that it is suggested to think of cairo is as a canvas that you will paint on. This kind of works for me. You have the canvas that you can put different layers of paint on that when combined and finished produces your final output. But that is about as far I will be using this metaphor in this chapter.

Things that cairo can be used for include creating graphics, combining work, doing layout for printing, or even creating reports as pdf documents. Really the only limitation to cairo is your imagination.

Dig in and see what you can learn.

## Basics

The first example with cairo will be some simple drawing. It will create a surface and draw a line saving to a image file. When working with cairo it must be remembered that the *cairo* module is needed and must be imported.

```python
import cairo

WIDTH, HEIGHT = 400, 400

# Setup Cairo
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
context = cairo.Context(surface)

# Set thickness of brush
context.set_line_width(15)
# Draw Vertical Line
context.move_to(200, 150)
context.line_to(200, 250)

# Draw horizontal line
context.move_to(150, 200)
context.line_to(250, 200)
context.stroke()

# Output a PNG file
surface.write_to_png("cairo-draw-line1.png")
```

This example creates an ImageSurface with a width and height of 400. The ImageSurface is set to use the cairo.FORMAT\_ARG32 (See below for details). The context is what actually keeps track of everything that is done to the surface and is used to draw. It is used to control how the drawing operations are used.

With a context set it is now possible to draw or perform other actions. First thing that is done is to set the line width to 15 using the *context.set\_line\_width(15)* method. The `set_line` method sets the width of a line for a context.

Next, using the contexts move\_to method moves the position of the brush to the position specified; which in the line is x position 200 and y position 150. X coordinates are measured from the left most part of the surface. Y coordinates are measured from the top most part of the surface.

Using the contexts `line_to` method will draw a line from the current position, that was specified with the move\_to method, to the new position specified with the line\_to method. To display what has been drawn with the `line_to` method the contexts *stroke* method must be called. Once `context.stroke()` is called then the lines are actually applied to the surface.

See figure [Two Straight Lines](03-cairo.html#fig-cairo-two-striaght-lines) to see what the output should look like.

![Two Straight Lines](images/cairo/cairo-draw-line1.png){: #fig-cairo-two-striaght-lines width="50%"}

### Cairo Surface Format

There are four surface options available[^1] and they are:

cairo.FORMAT\_ARGB32
: each pixel is a 32-bit quantity, with alpha in the upper 8 bits, then red, then green, then blue. The 32-bit quantities are stored native-endian. Pre-multiplied alpha is used. (That is, 50% transparent red is 0x80800000, not 0x80ff0000.)

cairo.FORMAT\_RGB24
: each pixel is a 32-bit quantity, with the upper 8 bits unused. Red, Green, and Blue are stored in the remaining 24 bits in that order.

cairo.FORMAT\_A8
: each pixel is a 8-bit quantity holding an alpha value.

cairo.FORMAT\_A1
: each pixel is a 1-bit quantity holding an alpha value. Pixels are packed together into 32-bit quantities. The ordering of the bits matches the endianess of the platform. On a big-endian machine, the first pixel is in the uppermost bit, on a little-endian machine the first pixel is in the least-significant bit.

In most cases cairo.FORMAT\_ARGB32 or cairo.FORMAT\_RGB24 will be used.

### Cairo Surfaces

cairo.ImageSurface(cairo.FORMAT\_ARGB32, WIDTH, HEIGHT)
: Use to render to memory buffers.

cairo.PDFSurface("drawings.pdf", WIDTH, HEIGHT)
: Renders to the specified PDF file.

cairo.PSSurface("drawings.ps", WIDTH, HEIGHT)
: Renders to the specified Postscript file.

cairo.SVGSurface("drawings.svg", WIDTH, HEIGHT)
: Renders to the specified SVG file.

## Drawing Context

As discussed above, a context is what allows the programmer to use the cairo surface. This section will discover different uses of the context class by making use of several different examples. For a list of the context methods used in this section please skip ahead to [Context Methods](03-cairo.html#sub-cairo-context-methods).

### Paths: Lines, Curves, Arcs

To start off this section lets take a look at line drawing again, but using it to draw more than two straight lines. This example will use the `line_to` method to create a rectangle and triangle. It will also use a new method, *arc*, to create a circle. Along with with these two methods, the color of the context will be set using the `set_source_rgb` value. These methods set points that are then used to create a path.

This example starts by calling the *main* function. Inside the main function it creates a cairo ImageSurface with an alpha RGB format and a width and height of 400. It then creates a context from this surface. The ImageSurface renders to a memory buffer and not an image. To save to an image the surface must call the `write_to_png` method that is available to all surface types.

Next it sets the line with of the context to 15. Immediately after this it calls the draw\_rectangle, draw\_triangle, and draw\_circle functions. These are functions that are defined in this example and are not cairo builtin methods. While cairo contexts do have a builtin method to create rectangles, this example is doing it manually just to show how to use the line\_to method in different ways.

Cairo Context Basics

```python
#!/usr/bin/env python
import cairo
import math

def draw_rectangle(context=None):
  x1, y1 = 25, 150 # top left corner
  x2, y2 = 25, 250 # bottom left corner
  x3, y3 = 125, 250 # bottom right corner
  x4, y4 = 125, 150 # top right corner

  context.set_source_rgb(1.0, 0.0, 0.0) # red
  context.move_to(x1, y1)
  context.line_to(x2, y2)
  context.line_to(x3, y3)
  context.line_to(x4, y4)
  context.close_path()
  context.stroke()
```

The draw\_rectangle function starts off by defining four corners that will make up the rectangle.

These four x and four y coordinates create the four corners of the rectangle. Top left, bottom left, bottom right and the top right corners. To draw a rectangle the function first uses the *move\_to(x1, y1)* method on the context to move the starting position to the first corner. Then it uses the *line\_to(x2, y2)* method to create a line from the first corner to the second. Then it again uses the `line_to` method with x3 and y3 to create a line from the second corner to the third corner. And last with the `line_to` method it creates a line from the third to the fourth corner.

Now if you follow that lines that were created, you will notice only the left side, bottom, and right side where drawn, but all four corners were used. The line\_to method could be used again to draw a line from x4 and y4 to x1 and y1, but instead the `close_path` method is used. The close path method will draw a line from the current position to the first position (since the last time the *stroke* method was called).

Also in the draw\_rectangle function the context is set to draw these lines in red using the set\_source\_rgb(red, green, blue) method. This method takes 3 variables each with a value between 0.0 and 1.0, with 0.0 being none of that color and 1.0 being a solid color. The lower the value, the higher the opacity.

```python
def draw_triangle(context=None):
  context.set_source_rgb(0.0, 1.0, 0.0) # green
  context.move_to(275, 175)
  context.line_to(375, 375)
  context.rel_line_to(-200, 0)
  context.close_path()
  context.stroke()
```

The draw\_triangle method is similar to the draw\_rectangle function in that it also uses the move\_to, line\_to and close\_path methods. But it also uses the `rel_line_to` method; this method stand for relative\_line\_to, and moves to a new position based on the current location instead of using the absolute value of the surfaces width and height.

Like in the rectangle function, the triangle function sets the color (to green)

Next it starts by moving the starting coordinate to x coordinate 275 and y coordinate 175. Then draws a line to x 375 and y 375.

After this instead of drawing based on absolute coordinates of the surface width and height, it uses the `rel_line_to` method to draw from x 375 and 375. It uses -200 x which moves from 375 to 175 and moves 0 from y. This means there is a line drawn from (375, 375) to (175, 375).

Finally it closes the path and uses the *stroke* method to apply the lines to the surface.

```python
def draw_circle(context=None):
  width, height = 100, 100
  radius = min(width, height)
  context.set_source_rgb(0.0, 0.0, 1.0) # blue
  context.arc(275, 100, radius / 2.0 - 20, 0, 2 * math.pi)
  context.stroke()
```

The draw\_circle function introduces the a new method; *arc*.

The start\_angle and stop\_angle are specified in radians. If you do not know how to work with radians take a look at section [Radians and Degrees](03-cairo.html#sub-radians-and-degrees). Here the start angle is set to 0. The stop\_angle is set to 2 * math.pi, which is 360 degrees. This arc therefore forms a full circle.

Other parts of the arc method is the x and y coordinate positions for the center of the arc. After the x and y coordinates come the radius of the arc.

```python
def draw_curve(context=None):
  context.set_source_rgb(0.5, 0.0, 0.3)

  context.move_to(20, 20)
  context.curve_to (60, 100, 100, 20, 140, 100)
  context.stroke()
```

The draw\_curve function is used to draw a cubic Bézier spline from the current position to x3 and y3, using x1, x2, y1, y2 as control points. If no current position is set, x1 and y1 are used as the starting position. This is accomplished using the curve\_to method. The curve\_to method is defined as context.curve\_to(x1, y1, x2, y2, x3, y3).

```python
def main():
  surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 400)
  context = cairo.Context(surface)
  context.set_line_width(15)

  draw_rectangle(context)
  draw_triangle(context)
  draw_circle(context)
  draw_curve(context)

  surface.write_to_png("cairo-basics.png")

if __name__ == "__main__":
  main()
```

#### Radians and Degrees {#sub-radians-and-degrees}

If you do not know how to work with radians you are in luck, as it is very simple.

```python
radians=degree*(math.pi/180)
```

You can also use.

```python
radians = math.radians(degree)
```

If you want to know what the degrees of a radian is that is simple as well. Switch the degree with the radian and divide 180 by PI.

```python
degree=radians*(180/math.pi)
```

You can also use.

```python
degree = math.degrees(radian)
```

### Text

Drawing text is with cairo is the same as drawing a line or an arc but using some specific functions for text. Start off like any other cairo application setting the type of surface and setup a context.

```python
import cairo
text = "Hello to the Great Text."

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 75)
context = cairo.Context(surface)
context.set_source_rgb(0.0, 0.0, 0.0) # set to black
```

What is then needed is to set the type of font and its size. Here a Monospace font is set with a normal slant and is set to be bold (see section [Font Styles](03-cairo.html#sub-cairo-font-styles) for more styles). The size of the font is set to 50.

```python
context.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL,
    cairo.FONT_WEIGHT_BOLD)
context.set_font_size(50)
```

Using the context that was created it is possible to retrieve information on the text that is being used with the text\_extents method.

```python
x_bearing, y_bearing, width, height = context.text_extents(text)[:4]
```

Last is to move the context to the location that it should be drawn. Here the text is set to draw a X coordinate 5 and at a Y coordinate that is is the height of the text. To apply the text the show\_text method is now called. This method adds text to the cairo context. To show the text the stroke method is called. To finish off it is saved to a file called cairo-draw-text1.png.

```python
context.move_to(5, height)
context.show_text(text)
context.stroke()
surface.write_to_png("cairo-draw-text1.png")
```

#### Font Styles {#sub-cairo-font-styles}

There are more than two types of font face styles available with cairo; there are five.

- cairo.FONT\_SLANT\_ITALIC
- cairo.FONT\_SLANT\_NORMAL
- cairo.FONT\_SLANT\_OBLIQUE
- cairo.FONT\_WEIGHT\_BOLD
- cairo.FONT\_WEIGHT\_NORMAL

### Antialias

First lets define antialias so there is no confusion.

Antialias
: Is the technique of minimizing the distortion artifacts created while drawing.

But what does this mean? Basically nothing if a straight line is being drawn. However if a curve or arc is being drawn it will look distorted or jagged, not very smooth at all. However with antialiasing turned on it will look smooth by setting the color correctly around the edges. The best way to understand this is to view an image. Take a look at figure [Antialias Example - As can be seen the circle on the left uses the default cairo antialias while the circle on the left turns antialias off. As can be seen when antialias is turned off the curves become jagged/distorted.](03-cairo.html#fig-cairo-antialias-example) and see if you can tell the difference.

![Antialias Example - As can be seen the circle on the left uses the default cairo antialias while the circle on the left turns antialias off. As can be seen when antialias is turned off the curves become jagged/distorted.](images/cairo/cairo-antialias.png){: #fig-cairo-antialias-example}

Now the question is why would you want to turn off antialiasing? I cannot think of to many reasons, but one that I can think of is for the program DeVeDe. It is a GUI application that uses a few command line applications to create DVDs from video files.

One of the programs that DeVeDe uses is dvdauthor. One of the functions of dvdauthor is to create dvd menus. And one part of the menu system is not able to handle more than four colors in an image including the alpha channel. With antialiasing turned on it will output images with many colors, because to make a curve look smooth it uses different shades of the color being used. However if antialias is set to none the image created with cairo will only have the colors specified and will be able to be used with dvdauthor.

#### Changing Antialias

To change the default antialias the contexts set\_antialias method is used.

```python
context.set_antialias(Antialias Type)
```

To find out what the current setting is just use the context get\_antialias() method.

The example below sets up a normal cairo surface and context. It then draws two circles. The first circles draws with the default antialias, which is cairo.ANTIALIAS\_DEFAULT, and the second circle is drawn with antialias turned off.

```python
import cairo, math

def draw_circle(context, xc, yc):
  radius = 150
  context.set_source_rgb(0.0, 0.0, 1.0)
  context.arc(xc, yc, radius / 2.0 - 20, 0, 2 * math.pi)
  context.stroke()

if __name__ == "__main__":
  surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 300, 200)
  context = cairo.Context(surface)
  context.set_line_width(20)

  draw_circle(context, 75, 100)
  context.set_antialias(cairo.ANTIALIAS_NONE)
  draw_circle(context, 225, 100)
  surface.write_to_png("cairo-antialias.png")
```

To turn off antialias, the context set\_antialias method must be given the cairo.ANTIALIAS\_NONE type. To see what this looks like take a look at figure [Antialias Example - As can be seen the circle on the left uses the default cairo antialias while the circle on the left turns antialias off. As can be seen when antialias is turned off the curves become jagged/distorted.](03-cairo.html#fig-cairo-antialias-example).

#### Antialias Types

The four options available for antialias are:

- cairo.ANTIALIAS\_DEFAULT
- cairo.ANTIALIAS\_GRAY
- cairo.ANTIALIAS\_SUBPIXEL
- cairo.ANTIALIAS\_NONE

### Context Methods {#sub-cairo-context-methods}

set\_source\_rgb(R,G,B)
: This allows setting the color value of the context

rel\_curve\_to(x1,y1,x2,y2,x3,y3)
: Create a curve instead of a straight line from the current position to x3 and y3, using x1/y1 and x2/y2 as control point. Where x1, x2, x3, y1, y2, y3 are relative to the current position.

curve\_to(x1,y1,x2,y2,x3,y4)
: Create a curve instead of a straight line from the current position to x3 and y3, using x1/y1 and x2/y2 as control point

rel\_line\_to(x,y)
: Draw a line relative to the current position with an offset of x and of y

line\_to(x,y)
: Draw a line from the current position to the new position

rel\_mov\_to(x,y)
: Move the position relative to the current position

move\_to(x,y)
: Move by an absolute position

set\_font\_size(size)
: set the size of the font

arc
: Draw an arc

fill
: Color the path that as been set with rectangle or line\_to with the color that has been set

rectangle(x1,y1,x2,y2)
: Draw a rectangle

set\_antialias(type)
: Set the the type of antialias that is to be used

close\_path
: Draw a line from the starting position since the last time stroke was called from the current position, thus closing the path

## Cairo and PyGTK {#sec-cairo-cairo-and-pygtk}

![Custom PyGTK widget with Cairo](images/cairo/cairo-gtk-screenshot.png){: #fig-cairo-pygtk-cairo-custom-widget width="70%"}

Cairo can be used with PyGTK by creating a custom widget. The custom widget discussed here will extend the gtk.DrawingArea class and override[^2] the expose\_event signal callback method; `do_expose_event`.

```python
class CairoGtkOverride(gtk.DrawingArea):
  __gsignals__ = {"expose_event": "override" }

  def __init__(self):
    gtk.DrawingArea.__init__(self)

  def do_expose_event(self, event):
    context = self.window.cairo_create()
    context.rectangle(event.area.x, event.area.y,
        event.area.width, event.area.height)
    context.clip()

    self.draw(context, *self.window.get_size())

  def draw(self, context, width, height):
    context.set_source_rgb(0.5, 0.0, 0.0)
    context.rectangle(0, 0, width, height)
    context.fill()
```

To properly override a signal in PyGTK set the class variable \_\_gsignals\_\_ to override the expose\_event signal. In the \_\_init\_\_ method the class initiates its base class.

The `do_expose_event` method is the callback for the expose\_event signal. It sets up a cairo context, creates a rectangle to the size of the widget. It uses the event to retrieve the size that is needed; `event.area.x` and `event.area.y` are the starting x and y coordinates while `event.area.width` and `event.area.height` are the width and height of the widget. Then the widget is set to only draw to the size of the rectangle using `context.clip()`. The last part is to call the classes *draw* method on every expose event.

The draw method takes as arguments a cairo context and a width and height of the widget. The draw method is where you can use cairo just as if it were not with PyGTK. The draw method in CairoGtkOverride draws a red rectangle.

Now that a custom widget class has been created it can be extend as much as is wanted and the draw method overwritten to draw what is desired.

```python
class Circle(CairoGtkOverride):
  def draw(self, context, width, height):
    context.set_source_rgb(1.0, 0.0, 0.0)
    radius = min(width, height)
    context.arc(width / 2.0, height / 2.0,
      radius / 2.0 - 20, 0, 2 * math.pi)
    context.stroke()
```

The above code extend the gtk custom widget class that was created further up and draws a circle instead of a red rectangle.

To run the code just add these widgets to your PyGTK application the same way you would any other widget.

```python
if __name__ == "__main__":
  win = gtk.Window()
  win.connect("delete-event", gtk.main_quit)
  vbox = gtk.VBox()

  override_widget = CairoGtkOverride()
  circle_widget = Circle()

  vbox.pack_start(override_widget, True, True, 0)
  vbox.pack_start(circle_widget, True, True, 0)
  win.add(vbox)
  win.show_all()
  gtk.main()
```

## Summary

For more examples on PyGTK and cairo you can take a look at the following resources:

- <http://blog.eikke.com/index.php/ikke/2007/02/17/python_cairo_xshape_and_clocks>
- <http://ralph-glass.homepage.t-online.de/clock/readme.html>
- <http://ralph-glass.homepage.t-online.de/shogi/readme.html>
- <http://www.cairographics.org/pycairo/resources/>
- <http://www.tortall.net/mu/wiki/CairoTutorial>
- <http://www.tortall.net/mu/wiki/PyGTKCairoTutorial>
- <http://www.pygtk.org/articles/cairo-pygtk-widgets/cairo-pygtk-widgets.htm>
- <http://www.pygtk.org/articles/cairo-pygtk-widgets/cairo-pygtk-widgets2.htm>

Remember, if you want to see what is available in your cairo install, use dir(cairo) from within python to see what is available.

```python
import cairo
dir(cairo)
```

[^1]: The list of formats available are taken from the cairo website and can be found at: <http://www.cairographics.org/manual/cairo-Image-Surfaces.html>
[^2]: Take a look at <http://www.sicem.biz/personal/lgs/docs/docs/gobject-python/gobject-tutorial.html> for a tutorial on creating custom properties and signals. Overriding signals is also covered.
