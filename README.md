# PyGTK Notebook

*A Journey Through Python Gnome Technologies* — an open source book about PyGTK
and the Linux desktop technologies around it: Cairo graphics, GStreamer
multimedia, Clutter animation, DBus, printing, internationalization and Gnome
desktop integration.

Read it online at <https://majorsilence.github.io/pygtknotebook/>, or download
[the PDF](https://majorsilence.github.io/pygtknotebook/pygtk-notebook.pdf).

> **Note:** everything currently in the book targets GTK 2 and the original
> `pygtk` bindings. Updating it to GTK 3/4 and PyGObject is in progress.

## Repository layout

| Path | What it is |
| --- | --- |
| `_chapters/` | The book. One Markdown file per chapter — **this is the source of truth.** |
| `images/`, `examples/` | Figures and the runnable sample programs the text refers to. |
| `_layouts/`, `assets/`, `index.md`, `_config.yml` | The Jekyll site. |
| `tools/build-pdf.sh` | Builds the PDF from `_chapters/` via pandoc + LaTeX. |
| `tools/lyx2md.py` | The one-shot LyX → Markdown migration, kept for reference. |
| `pygtk-notebook-latest.lyx` | The retired LyX source. No longer edited. |

## Writing

Chapters are plain Markdown with a small amount of Jekyll front matter:

```yaml
---
layout: chapter
title: "Cairo"
number: 3
---
```

Add `appendix: true` for back matter and `unnumbered: true` for pages that
should not get a chapter number. Body headings start at `##`; the `#` level is
generated from `title`.

Two conventions are worth knowing:

- **Cross references** are ordinary relative links —
  `[Glade 3](02-more-pygtk.html#sec-glade-3)`. The PDF build rewrites them into
  internal document anchors, so one form works in both outputs.
- **Image sizing** uses a kramdown attribute list —
  `![Caption](images/cairo/example.png){: width="50%"}`. The PDF build translates
  it to pandoc's syntax.

An image alone in a paragraph becomes a numbered figure in the PDF, with its alt
text as the caption.

## Building

### The website

```sh
bundle install
make serve      # http://127.0.0.1:4000
```

### The PDF

Needs pandoc and a LaTeX installation:

```sh
sudo apt-get install pandoc texlive-xetex texlive-fonts-recommended texlive-latex-extra
make pdf        # -> build/pygtk-notebook.pdf
```

The PDF is laid out to match the retired LyX original: `book` class, 10pt,
two-sided, 20.95 × 27.31 cm paper, numbered chapters and an appendix, a table of
contents and a list of figures.

### Continuous builds

`.github/workflows/pages.yml` builds the PDF, builds the site, copies the PDF
into it, and deploys the result to GitHub Pages on every push to `main`. Enable
it under *Settings → Pages → Build and deployment → GitHub Actions*.

## Contributing

Corrections, examples and modernization are all welcome — open an issue or a
pull request.

## License

Book text is licensed under
[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/legalcode).
Sample code is released under the MIT license.
