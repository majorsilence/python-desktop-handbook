---
layout: chapter
title: "Internationalization"
number: 10
---

> Please send any fixes or suggestions to peter@majorsilence.com or leave a comment at http://www.majorsilence.com/pygtk\_book.

Must install intltool package on linux systems to provide the tools and scripts that are needed to extract the needed information from the python scripts and the programs glade files.

- gettext.bindtextdomain(domain, localedir) - Bind the text to main to the locale directory that is specified. Where the binary .mo files are looked for.
- gettext.textdomain(domain) - Sets the current global domain to the domain argument. If domain is none then the current global domain is returned.
- gettext.translation(domain, localedir, languages, class, fallback, codeset) - Set the domain and the locale directory. All this chapter will be interested in is the first two arguments domain and localedir.
- gettext.install(domain, localedir, unicode, codeset, names) - Install the function \_() in the python builtin namespace so that it may be used easily from any python module within a program.

## Python/PyGTK Translation {#sec-python-pygtk-translation}

To start off here is a very small program that has been setup for localization.

```python
import pygtk, gtk
pygtk.require("2.0")
import locale, gettext

APP="translation-example"
DIR="po"

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
lang = gettext.translation(APP, DIR)
_ = lang.gettext
gettext.install(APP, DIR)
```

To start off the variable APP is set to "translation-example" and is used to set the domain for the translation.

```python
class TranslationExample(object):
  def __init__(self):
    self.label_1 = gtk.Label( _("Hello World!") )
    label_2 = gtk.Label( _("Still in the HBox") )
    button = gtk.Button( _("Click Me") )

    button.connect("clicked", self.on_button_clicked,
        _("Anything can go here") )
    vbox = gtk.VBox()
    vbox.pack_start(self.label_1) vbox.pack_start(label_2)
    vbox.pack_start(button)

    win = gtk.Window()
    win.connect("destroy", lambda wid: gtk.main_quit())
    win.add(vbox)
    win.show_all()

  def on_button_clicked(self, widget, data=None):
    self.label_1.set_text( _("Hello ") + str(data) )

if __name__ == "__main__":
  TranslationExample()
  gtk.main()
```

For more indepth coverage of gettext visit <http://docs.python.org/library/gettext.html>. To download the tools from windows get them from the gnu site <ftp://ftp.gnu.org/gnu/gettext/gettext-tools-0.13.1.bin.woe32.zip>.

Now use the gettext command tool to extract the needed strings from all the python files and create the translation-example.pot file.

```python
gettext --language=Python --keyword=_ --keyword=N_
    --output=translation-example.pot translation-example.py
```

Now for each language that will be available for the application a .po file must be created. So if Canadian English is the language is to be used:

```python
msginit --input=translation-example.pot --locale=en_CA
```

Will output a en\_CA.po file. American English would be:

```python
msginit --input=translation-example.pot --locale=en_US
```

Will output an en\_US.po file. German would be:

```python
msginit --input=translation-example.pot --locale=de_DE
```

This of course would output de.po.

Finally the .po files must be edited and the localized language put into their proper places. Just make sure that when the .po files are created that the *charset* is set to *utf-8*.

```po
# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2009-02-17 16:01-0330\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"

#: translation-example.py:20
msgid "Hello "
msgstr ""

#: translation-example.py:23
msgid "Hello World!"
msgstr ""

#: translation-example.py:24
msgid "Still in the HBox"
msgstr ""

#: translation-example.py:25
msgid "Click Me"
msgstr ""

#: translation-example.py:29
msgid "Anything can go here"
msgstr ""
```

Now what you need to do is edit the .po files so that the empty msgstr have the translated text. So what this means is that:

<a id="translations-po-translations-example"></a>

```po
#: translation-example.py:20
msgid "Hello "
msgstr ""
```

Would become in German:

```po
#: translation-example.py:20
msgid "Hello "
msgstr "Guten Tag"
```

Once all the strings are translated then the .po file must be converted into a binary .mo file and placed in its proper folder. So the en\_CA.po file would be converted into translation-example.mo and placed in the folder ./po/en\_CA/LC\_MESSAGES/.

```bash
msgfmt --output-file=translation-example.mo en_CA.po
```

Now copy the translation-example.mo file to the folder ./po/en\_CA/LC\_MESSAGES/. To test the the translated copy do the following:

```python
LANG=lang python myapp.py
```

So to test translation-example.py with german that would become:

```python
LANG=de_DE.UTF-8 python translation-example.py
```

It should be noted that on some systems that the .UTF-8 part is not needed.

## gtk.glade Translation {#sec-gtk-glade-translation}

Translating a project that makes use of a glade file is easy. It just takes a few extra commands to extract the needed text strings. To start off here is an example program that makes use of the translation-example.glade file (See Figure [Glade Translation Project](10-internationalization.html#fig-translations-glade-translation-project)).

<a id="fig-translations-glade-translation-project"></a>

![Glade Translation Project](images/translations/translations-example.png){width=40%}

```python
import pygtk
pygtk.require("2.0")
import gtk, gtk.glade
import locale, gettext

APP="translation-example"
DIR="po-glade"

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
lang = gettext.translation(APP, DIR)
_ = lang.gettext
gettext.install(APP, DIR)

class TranslationExample(object):
  def on_button_clicked(self, widget, data=None):
    self.label_1.set_text( _("Hello ") + str(data) )

  def __init__(self):
    self.gladefile = gtk.glade.XML("translation-example.glade")
    gtk.glade.bindtextdomain(APP, DIR)
    self.gladefile.signal_autoconnect(self)

    self.main_window = self.gladefile.get_widget("window1")
    self.main_window.connect("delete_event", lambda wid, we: gtk.main_quit())
    self.main_window.show_all()

if __name__ == "__main__":
  TranslationExample()
  gtk.main()
```

Create a translation-example.glade.h file by running intltool-extract on translation-example.glade. This is needed to extract the strings to translate with the gettext command line tool.

```bash
intltool-extract --type=gettext/glade translation-example.glade
```

Now use the xgettext command tool to extract the needed strings from all the python files as well as the translation-example.glade.h header file that was created and create the translation-example.pot file.

```bash
xgettext --language=Python --keyword=_ --keyword=N_
    --output=translation-example.pot translation-example.py
    translation-example.glade.h
```

Now for each language that will be available for the application a .po file must be created. So if Canadian English is the language is to be used:

```python
msginit --input=translation-example.pot --locale=en_CA
```

Will output a en\_CA.po file. American English would be:

```python
msginit --input=translation-example.pot --locale=en_US
```

Will output an en\_US.po file. German would be:

```python
msginit --input=translation-example.pot --locale=de_DE
```

This of course would put de.po.

Finally the .po files must be edited and the localized language put into their proper places. To do this please refer back to [Python/PyGTK Translation](10-internationalization.html#translations-po-translations-example) as it shows you how to use the *msgfmt* command and proper way to do the translations.

## gtk.Builder Translation {#sec-gtk-builder-translation}

Translating a project that makes use of a gtk.Builder file is easy. It just takes a few extra commands to extract the needed text strings. To start off here is an example program that makes use of the translation-example.glade file (See Figure [Glade Translation Project](10-internationalization.html#fig-translations-glade-translation-project)). First this file must be translated to a gtk.Builder file using the gtk-builder-convert (See section [Builder](02-more-pygtk.html#sec-gtk-builder-convert)) script.

```python
import pygtk
pygtk.require("2.0")
import gtk
import locale, gettext

APP="translation-example"
DIR="po-glade"

locale.setlocale(locale.LC_ALL, '')
# This is needed to make gtk.Builder work by specifying the
# translations directory
locale.bindtextdomain(APP, DIR)

gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
lang = gettext.translation(APP, DIR)
_ = lang.gettext
gettext.install(APP, DIR)

class TranslationExample(object):
  def on_button_clicked(self, widget, data=None):
    self.label_1.set_text( _("Hello ") + str(data) )

  def __init__(self):
    self.gladefile = gtk.Builder()
    self.gladefile.set_translation_domain(APP)
    self.gladefile.add_from_file("translation-example.xml")
    self.gladefile.connect_signals(self)

    self.main_window = self.gladefile.get_object("window1")
    self.main_window.connect("delete_event", lambda wid, we: gtk.main_quit())
    self.main_window.show_all()

if __name__ == "__main__":
  TranslationExample()
  gtk.main()
```

Translating a gtk.Builder xml file uses the exact same commands as translating a glade file, however .glade is replaced with .xml for the file that is being used. So create a translation-example.xml.h file by running intltool-extract on translation-example.xml. This is needed to extract the strings to translate with the gettext command line tool.

```bash
intltool-extract --type=gettext/glade translation-example.xml
```

Now use the xgettext command tool to extract the needed strings from all the python files as well as the translation-example.glade.h header file that was created and create the translation-example.pot file.

```bash
xgettext --language=Python --keyword=_ --keyword=N_
    --output=translation-example.pot translation-example.py
    translation-example.xml.h
```

Now for each language that will be available for the application a .po file must be created. So if Canadian English is the language is to be used:

```python
msginit --input=translation-example.pot --locale=en_CA
```

Will output a en\_CA.po file. American English would be:

```python
msginit --input=translation-example.pot --locale=en_US
```

Will output an en\_US.po file. German would be:

```python
msginit --input=translation-example.pot --locale=de_DE
```

This of course would put de.po.

Finally the .po files must be edited and the localized language put into their proper places. To do this please refer back to [Python/PyGTK Translation](10-internationalization.html#translations-po-translations-example) as it shows you how to use the *msgfmt* command and proper way to do the translations.

## Testing Translations {#sec-testing-translations}

To make sure that the translation is working properly it should be tested. This section will go into a bit more detail on setting this up.

First the language suppport files that the application has been translated into must be installed on the operating system. This section assumes ubuntu is the test system and the examples are geared toward it.

So lets assume the test system is ubuntu and German is the language that is to be tested. The easiest way to make sure that German language support is installed is to install the *language-support-de* package. This package will install all the german translation packages for the test system. If you wish you do not need to install this meta package, but can hunt down all the individual packages for german support.

Now make sure that the .mo files, in this case translation-example.mo, are copied to each of their respective language folders; Eg ./po/en\_CA/LC\_MESSAGES/. To test the the translated copy do the following:

```python
LANG=lang python myapp.py
```

So to test translation-example.py with german that would become:

```python
LANG=de_DE.UTF-8 python translation-example.py
```

It should be noted that on some systems that the .UTF-8 part is not needed.

### Testing on Win32/Win64

From the command line:

```python
SET Lang=de_DE
myapp.py
```

Another problem on Windows with gtkbuilder is that that it will not be translated in a pygtk application. You have to force it using ctypes[^1]. At least at the time of writting (pygtk 2.16 with gtk 2.16 and 2.18)

After this line of code

```python
gettext.install(APP,localedir=DIR)
```

You will then try something like this:

```python
try:
    libintl = ctypes.cdll.LoadLibrary("C:\\GTK\\gtk-2.16.6\\bin\\intl.dll")
    libintl.bindtextdomain(APP, DIR)
except:
    print "Error Loading translations into gtk.builder files"
```

## Translation Cheatsheet {#sec-translation-cheatsheet}

Small quick cheetsheet of the commands that are needed to translate.

```bash
intltool-extract --type=gettext/glade translation-example.glade
```

Extract from both glade/builder and python scripts

```bash
xgettext --language=Python --keyword=_ --keyword=N_
    --output=translation-example.pot translation-example.py
    translation-example.glade.h
```

Canadian English

```python
msginit --input=translation-example.pot --locale=en_CA
```

American English

```python
msginit --input=translation-example.pot --locale=en_US
```

German

```python
msginit --input=translation-example.pot --locale=de_DE
```

Change charset in each .po file to "charset=UTF-8" and put in each translation string. Create binary .mo files for each .po file and place them in their proper ./po/LANG/LC\_MESSAGES/ folder.

```bash
msgfmt --output-file=translation-example.mo en_CA.po
msgfmt --output-file=translation-example.mo en_US.po
msgfmt --output-file=translation-example.mo de_DE.po
```

Test each language the application using each language that it has been translated into.

```python
LANG=en_CA.UTF-8 python translation-example.py
LANG=en_US.UTF-8 python translation-example.py
LANG=de_DE.UTF-8 python translation-example.py
```

## Locale Lists {#sec-translations-locale-lists}

To be able to use and test any of these locale languages the language support packages for your linux distrubtion must be installed. On ubuntu these start with *language-support* and can be found using the synaptic package manager. So for german it would be *language-support-de*.

Here is a short list of locales[^2] that can be translated to.

en\_US
: English, United States of America

en\_CA
: English, Canada

en\_AU
: English, Australian

en\_GB
: English, Great Britain/United Kingdom

es\_MX
: Spanish, Mexico

es\_ES,
: Spanish, Spain

de\_DE
: Germany, German

fr\_FR
: French, France

fr\_CA
: French, Canadian

it\_IT
: Italian, Italy

ru\_RU
: Russian, Russia

pt\_BR
: Portuguese, Brazil

## Summary {#sec-translations-summary}

For more information on this topic please see these sites:

- <http://docs.python.org/library/gettext.html>
- <http://www.learningpython.com/2006/12/03/translating-your-pythonpygtk-application/>
- <http://faq.pygtk.org/index.py?req=show&file=faq22.002.htp>

[^1]: For more information see <https://bugzilla.gnome.org/show_bug.cgi?id=574520>
[^2]: On my ubuntu system there is a very nice list at /usr/share/i18n/SUPPORTED. This is a big list that does not include long form of the location of the locale.
