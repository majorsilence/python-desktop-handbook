---
layout: chapter
title: "Printing"
number: 4
---

> Please send any fixes or suggestions to peter@majorsilence.com or leave a comment at http://www.majorsilence.com/pygtk\_book.

A requirement for printing with PyGTK is cairo so it will be helpful to read the chapter on cairo first. However it is only necessary if you wish to know what is going on. If all you want is quick and easy printing than this chapter by itself should suffice.

Cairo is not only used for drawing pretty pictures. It can be used with PyGTK to print documents or whatever it is you wish to print.

## Print Example

This chapter will provide a simple python class that takes as arguments:

- action - The action to be performed (see section [Print Actions](04-printing.html#sub-cario-print-actions))
- data - print the provided string
- filename - open a text file to be printed

To use the PrintExample class all you have to do is create an instance specifying some data to print and the type of print action that is to be taken. For example lets say that the text "This text is Printed" is to be printed with a print dialog being opened to the user, then the following code would be used.

```python
printer = PrintExample(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG,
"This text is Printed")
```

Inside the \_\_init\_\_ method of the PrintExample class the paper size(see section[Paper Sizes](04-printing.html#sub-cario-paper-sizes)) is set, page setup information is created, and a print operation is initiated.

```python
class PrintExample:
  def __init__(self, action=None, data=None, filename=None):
    self.text = data
    self.layout = None
    self.font_size=12
    self.lines_per_page=0
    if action==None:
      action = gtk.PRINT_OPERATION_ACTION_PREVIEW

    paper_size = gtk.PaperSize(gtk.PAPER_NAME_A4)
    setup = gtk.PageSetup()
    setup.set_paper_size(paper_size)

    print_ = gtk.PrintOperation()
    print_.set_default_page_setup(setup)
    print_.set_unit(gtk.UNIT_MM)

    print_.connect("begin_print", self.begin_print)
    print_.connect("draw_page", self.draw_page)
    if action == gtk.PRINT_OPERATION_ACTION_EXPORT:
      print_.set_export_filename(filename)

   response = print_.run(action)
```

So first off in the \_\_init\_\_ method a few instance variables are created.

self.text
: Is used to hold the data that is to be printed

self.layout
: Is used to hold an pango layout instance

self.font\_size
: Is used to hold the font size that will be use with the layout with a pango.FontDescription instance

self.lines\_per\_page
: Is used to store how many lines are available per page

Next it checks to see what action as been set. If there is no action it will set as default to show a print preview.

```python
action = gtk.PRINT_OPERATION_ACTION_PREVIEW
```

Next an instance of the gtk.PaperSize class is created with a paper type of gtk.PAPER\_NAME\_A4 and is assigned to the variable `paper_size`. After this an instance of gtk.PageSetup is created and has a page size set by the just created instance of gtk.PaperSize `paper_size`.

The print operation instance is assigned to the variable print\_ using the gtk.PrintOperation class. It uses the print setup created above and sets the unit size to millimeters.

```python
    print_.set_default_page_setup(setup)
    print_.set_unit(gtk.UNIT_MM)
```

It then connects the signals needed to print to their methods in the PrintExample class. The needed signals are `begin_print` and `draw_page`. The begin\_print signal calls a method that sets up the needed information for the print operation. The `draw_page` signal calls a method that uses the the information from the `begin_print` method to print each individual page.

```python
    print_.connect("begin_print", self.begin_print)
    print_.connect("draw_page", self.draw_page)
```

Lastly, if the print action is to export it also sets the filename that it is to be exported.

As stated above the begin\_print method is called with the begin\_print signal and will setup the information that is needed to print using the draw\_page method.

```python
def begin_print(self, operation, context):
  width = context.get_width()
  height = context.get_height()
  self.layout = context.create_pango_layout()

  self.layout.set_font_description(
      pango.FontDescription("Sans " + str(self.font_size)) )
  self.layout.set_width(int(width*pango.SCALE))
  self.layout.set_text(self.text)

  num_lines = self.layout.get_line_count()
  self.lines_per_page = math.floor(
      context.get_height() / (self.font_size/2) )
  pages = ( int(math.ceil( float(num_lines) /
      float(self.lines_per_page) ) ) )
  operation.set_n_pages(pages)
```

The begin\_print method has the arguments *operation* and *context*. The operation argument will be used to set the number of pages. The context is used to get the information needed and create a pango layout. Pango is the part of gtk that is used for fonts and is needed for setting the font type, setting the width of the page and setting the text.

The the first two lines retrieve the width and the height of the of the context argument (which is a cairo context). It then creates a pango instance using the context.create\_pango\_layout() method and assigns this to the class instance variable self.layout from this point out obviously become a pango.Layout instance.

The next part now uses self.layout to set the font type to Sans 12. The self.font\_size is set as a class instance variable in the \_\_init\_\_ method so that it can be used from both the begin\_print and draw\_page methods. It sets the self.layout with to the cairo *context* width multiplied by the pango.SCALE constant (1024). After this the text of the pango layout is then set to the text that is held in the variable self.text; which was set in the \_\_init\_\_ method.

The number of lines in the whole document is retrieved with by calling self.layout.get\_line\_count(). The number of lines per page is calculated using the context height and dividing by the font size. The font size is divided by two so the lines are not spaced to far apart[^1].

The number pages is calculated by dividing the number of lines in the whole document by the number of lines per page. It then sets the number pages by calling the operation.set\_n\_pages method.

The draw\_page method is called directly after the begin\_print method. It uses the information that was stored in class instance variables and in the operation argument to print each page. It also has the argument page\_number. This holds the current page number that is being printed. Remember that the draw\_page method is not called once, it is called once for each page that is to be printed.

```python
def draw_page (self, operation, context, page_number):
  cr = context.get_cairo_context()
  cr.set_source_rgb(0, 0, 0)
  start_line = page_number * self.lines_per_page
  if page_number + 1 != operation.props.n_pages:
    end_line = start_line + self.lines_per_page
  else:
    end_line = self.layout.get_line_count()

  cr.move_to(0, 0)
  iter = self.layout.get_iter()
  i=0
  while 1:
    if i > start_line:
      line = iter.get_line()
      cr.rel_move_to(0, self.font_size/2)
      cr.show_layout_line(line)
    i += 1
    if not (i < end_line and iter.next_line()):
      break
```

First off the draw\_page method creates a cairo context by calling context.get\_cairo\_context(). The context is assigned to cr. It then sets the color of the text to black using cr.set\_source\_rgb(0, 0, 0). After this the starting line for the current page to print is calculated by multiplying the current page by the number of lines per page.

It then calculates the last line that is on the page. If it is not the last page of the document the last line is the start line plus the lines per page. If it is the last page to be printed the end line is the line count of the whole document.

```python
if page_number + 1 != operation.props.n_pages:
  end_line = start_line + self.lines_per_page
else:
  end_line = self.layout.get_line_count()
```

With this information the method is now able to draw the text using cairo. The context is set to the upper most left part of the page using *cr.move\_to(0, 0)*.

It creates an iter of the layout that is used to iterate through each line of the document that is left. A while loop is used to move through the lines. Each time through the while loop the variable i is incremented. Once I is greater than the start line, that was calculated for this page, the line is retrieved using `iter.get_line()`. The context is moved relative to its current position by the font size divided by two. Then the text is drawn to the context using the cr.show\_layout\_line method.

Once the variable is as incremented to a greater value then the end line, or there are no more lines in the iter to iterate through, break is called ending the while loop and exiting the draw\_page method.

## Print Actions {#sub-cario-print-actions}

There are several print actions that can be used with printing.

gtk.PRINT\_OPERATION\_ACTION\_PREVIEW
: Show the print preview

gtk.PRINT\_OPERATION\_ACTION\_EXPORT
: Export to a file. This requires the "export-filename" property to be set

gtk.PRINT\_OPERATION\_ACTION\_PRINT\_DIALOG
: Show the print dialog

gtk.PRINT\_OPERATION\_ACTION\_PRINT
: Start printing immediately without showing the print dialog. Based on the current print settings.

## Paper Sizes {#sub-cario-paper-sizes}

There are several different predefined paper sizes that can be used with PyGTK printing. These are listed below. There is also the possibility to use a custom paper size, but this is not discussed here.

gtk.PAPER\_NAME\_A3
: Name for the A3 paper size.

gtk.PAPER\_NAME\_A4
: Name for the A4 paper size.

gtk.PAPER\_NAME\_A5
: Name for the A5 paper size.

gtk.PAPER\_NAME\_B5
: Name for the B5 paper size.

gtk.PAPER\_NAME\_LETTER
: Name for the Letter paper size.

gtk.PAPER\_NAME\_EXECUTIVE
: Name for the Executive paper size.

gtk.PAPER\_NAME\_LEGAL
: for the Legal paper size.

## Summary

In summary, printing using cairo sucks but at least it is not to bad.

[^1]: There is a different way to do this but I found this the easiest way to start off with.
