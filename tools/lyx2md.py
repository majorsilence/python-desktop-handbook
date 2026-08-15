#!/usr/bin/env python3
"""Convert the PyGTK Notebook LyX sources into Jekyll-flavoured Markdown.

This is a one-shot migration tool: it was used to turn ``pygtk-notebook-latest.lyx``
into the per-chapter Markdown files under ``_chapters/``.  It is kept in the tree so
the conversion can be re-run and audited, but after the migration the Markdown files
are the source of truth -- edit those, not the LyX.

Usage::

    python3 tools/lyx2md.py pygtk-notebook-latest.lyx --outdir _chapters

The converter understands the subset of the LyX file format that this book actually
uses: chapters/sections, LyX-Code listings, itemize/enumerate/description/labeling
lists, floats with graphics and captions, footnotes, URL and href insets, labels and
cross references, the bibliography, and the character styles (emphasis, bold,
italic shape).  Notes, branches, index entries and raw LaTeX (ERT) are dropped, which
matches what LyX itself emits for this document.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata

# Sentinels used while a paragraph is being accumulated, so that emphasis spans can be
# rebalanced (Markdown will not accept "* text *") once the full text is known.
EMPH = "\x01"
BOLD = "\x02"
CODE = "\x03"
APPENDIX = "\x06"

HEADING_STYLES = {
    "Chapter": 1,
    "Section": 2,
    "Subsection": 3,
    "Subsubsection": 4,
    "Paragraph": 5,
}


def slugify(text: str) -> str:
    """Turn a LyX label name or a heading into a stable anchor id."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.replace(":", "-")
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return re.sub(r"-{2,}", "-", text)


# --------------------------------------------------------------------------------------
# Document model
# --------------------------------------------------------------------------------------


class Para:
    """One LyX paragraph: a layout style plus its rendered inline Markdown."""

    def __init__(self, style: str, text: str = "", label: str | None = None):
        self.style = style
        self.text = text
        self.label = label
        self.children: list = []  # nested blocks (figures, quote boxes, ...)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Para({self.style!r}, {self.text[:40]!r})"


class Figure:
    def __init__(self, path: str, caption: str, label: str | None, scale: int | None):
        self.path = path
        self.caption = caption
        self.label = label
        self.scale = scale


class QuoteBlock:
    def __init__(self, paras):
        self.paras = paras


# --------------------------------------------------------------------------------------
# Parser
# --------------------------------------------------------------------------------------


class LyxParser:
    def __init__(self, lines: list[str], base_dir: str):
        self.lines = lines
        self.base_dir = base_dir
        self.i = 0
        self.footnotes: list[str] = []

    # -- low level ---------------------------------------------------------------

    def peek(self) -> str | None:
        return self.lines[self.i] if self.i < len(self.lines) else None

    def skip_inset(self) -> None:
        """Consume the current inset (self.i sits on its ``\\begin_inset``)."""
        depth = 0
        while self.i < len(self.lines):
            line = self.lines[self.i]
            if line.startswith("\\begin_inset"):
                depth += 1
            elif line.startswith("\\end_inset"):
                depth -= 1
                if depth == 0:
                    self.i += 1
                    return
            self.i += 1

    def inset_args(self) -> dict[str, str]:
        """Read the ``key value`` / ``key "value"`` argument lines of an inset."""
        args: dict[str, str] = {}
        while self.i < len(self.lines):
            line = self.lines[self.i].strip()
            if not line:
                self.i += 1
                continue
            if line.startswith("\\begin_layout") or line.startswith("\\end_inset"):
                break
            if line.startswith("\\begin_inset"):
                break
            parts = line.split(None, 1)
            if len(parts) == 2:
                args[parts[0].lstrip("\\")] = parts[1].strip('"')
            else:
                args[parts[0].lstrip("\\")] = ""
            self.i += 1
        return args

    # -- paragraph level ---------------------------------------------------------

    def parse_paragraphs(self, stop: tuple[str, ...]) -> list:
        """Parse ``\\begin_layout`` blocks until one of *stop* is reached."""
        blocks: list = []
        while self.i < len(self.lines):
            line = self.lines[self.i]
            if any(line.startswith(s) for s in stop):
                return blocks
            if line.startswith("\\begin_layout"):
                style = line[len("\\begin_layout"):].strip()
                self.i += 1
                blocks.extend(self.parse_layout_body(style))
            else:
                self.i += 1
        return blocks

    def parse_layout_body(self, style: str) -> list:
        """Render one layout, returning it plus any block-level insets it contained."""
        buf: list[str] = []
        extra: list = []
        label: str | None = None
        first_line = True
        code = style == "LyX-Code"

        while self.i < len(self.lines):
            line = self.lines[self.i]
            if line.startswith("\\end_layout"):
                self.i += 1
                break
            if line.startswith("\\begin_inset"):
                text, blocks, lbl = self.parse_inset(code)
                buf.append(text)
                extra.extend(blocks)
                label = label or lbl
                first_line = False
                continue
            if line.startswith("\\end_inset"):
                # Defensive: a stray close means the enclosing inset ended.
                break
            self.i += 1
            if line.startswith("\\"):
                buf.append(self.character_style(line, code))
                continue
            if not line.strip() and first_line:
                continue
            buf.append(line if not first_line or code else line.lstrip())
            if line.strip():
                first_line = False

        text = "".join(buf)
        if not code:
            text = finish_inline(text)
        para = Para(style, text, label)
        para.children = extra
        result: list = []
        if text.strip() or code or style in ("Chapter", "Section", "Subsection"):
            result.append(para)
        elif label or extra:
            # A paragraph that only carried a label or a float still matters.
            result.append(para)
        return result

    def character_style(self, line: str, code: bool) -> str:
        cmd = line.strip()
        if code:
            # Inside listings, character styles are meaningless.
            return "\\" if cmd == "\\backslash" else ""
        if cmd == "\\backslash":
            return "\\"
        if cmd.startswith("\\emph"):
            return EMPH
        if cmd.startswith("\\shape"):
            return EMPH if "italic" in cmd else EMPH
        if cmd.startswith("\\series"):
            return BOLD
        if cmd.startswith("\\family"):
            return CODE
        if cmd == "\\start_of_appendix":
            return APPENDIX
        # \size, \lang, \bar, \noun, \labelwidthstring, ... carry no Markdown meaning.
        return ""

    # -- insets ------------------------------------------------------------------

    def parse_inset(self, code: bool) -> tuple[str, list, str | None]:
        """Return (inline text, block-level children, label) for the inset at self.i."""
        header = self.lines[self.i][len("\\begin_inset"):].strip()
        kind = header.split()[0] if header else ""

        if kind == "Quotes":
            self.skip_inset()
            return ('"' if code else '"'), [], None
        if kind == "Index":
            self.skip_inset()
            return "", [], None
        if kind == "Note":
            self.skip_inset()
            return "", [], None
        if kind == "Branch":
            # Both branches are unselected in the source, so LyX prints neither.
            self.skip_inset()
            return "", [], None
        if kind == "ERT":
            return self.parse_ert(), [], None
        if kind == "Newpage":
            self.skip_inset()
            return "", [], None
        if kind == "space":
            self.skip_inset()
            return " ", [], None
        if kind == "Flex":
            return self.parse_flex(header), [], None
        if kind == "Foot":
            return self.parse_footnote(), [], None
        if kind == "Float":
            return "", self.parse_float(header), None
        if kind == "Graphics":
            args = self.grab_simple_inset()
            return "", [Figure(args.get("filename", ""), "", None, _int(args.get("scale")))], None
        if kind == "Box":
            return "", self.parse_box(), None
        if kind == "CommandInset":
            return self.parse_command_inset()
        if kind == "Caption":
            self.skip_inset()
            return "", [], None

        self.skip_inset()
        return "", [], None

    def grab_simple_inset(self) -> dict[str, str]:
        self.i += 1
        args = self.inset_args()
        # Consume up to and including the closing \end_inset.
        depth = 1
        while self.i < len(self.lines) and depth:
            line = self.lines[self.i]
            if line.startswith("\\begin_inset"):
                depth += 1
            elif line.startswith("\\end_inset"):
                depth -= 1
            self.i += 1
        return args

    def parse_ert(self) -> str:
        """Raw LaTeX. Only ``\\_`` carries content in this book; the rest is layout."""
        start = self.i
        self.skip_inset()
        raw = "\n".join(self.lines[start:self.i])
        return "_" if re.search(r"\\backslash\n_", raw) else ""

    def parse_flex(self, header: str) -> str:
        args_start = self.i
        self.skip_inset()
        body = self.lines[args_start:self.i]
        text = "".join(
            l for l in body
            if not l.startswith("\\") and l.strip() and not l.startswith("status")
        ).strip()
        if header.endswith("URL"):
            return f"<{text}>" if text else ""
        return text

    def parse_footnote(self) -> str:
        self.i += 1
        paras = self.parse_paragraphs(("\\end_inset",))
        self.i += 1  # consume \end_inset
        text = " ".join(p.text.strip() for p in paras if p.text.strip())
        if not text:
            return ""
        self.footnotes.append(text)
        return f"[^{len(self.footnotes)}]"

    def parse_box(self) -> list:
        """A framed box; in this book it only ever wraps the per-chapter contact note."""
        self.i += 1
        self.inset_args()
        paras = self.parse_paragraphs(("\\end_inset",))
        self.i += 1
        paras = [p for p in paras if p.text.strip()]
        return [QuoteBlock(paras)] if paras else []

    def parse_float(self, header: str) -> list:
        self.i += 1
        self.inset_args()
        path, scale, caption, label = "", None, "", None
        while self.i < len(self.lines):
            line = self.lines[self.i]
            if line.startswith("\\end_inset"):
                self.i += 1
                break
            if line.startswith("\\begin_layout"):
                self.i += 1
                continue
            if line.startswith("\\end_layout"):
                self.i += 1
                continue
            if line.startswith("\\begin_inset Graphics"):
                args = self.grab_simple_inset()
                path = args.get("filename", path)
                scale = _int(args.get("scale")) or scale
                continue
            if line.startswith("\\begin_inset Caption"):
                self.i += 1
                paras = self.parse_paragraphs(("\\end_inset",))
                self.i += 1
                caption = " ".join(p.text.strip() for p in paras if p.text.strip())
                label = next((p.label for p in paras if p.label), label)
                continue
            if line.startswith("\\begin_inset CommandInset"):
                # The label usually sits beside the caption rather than inside it.
                _text, _blocks, found = self.parse_command_inset()
                label = found or label
                continue
            if line.startswith("\\begin_inset"):
                self.skip_inset()
                continue
            self.i += 1
        return [Figure(path, caption, label, scale)] if path else []

    def parse_command_inset(self) -> tuple[str, list, str | None]:
        args = self.grab_simple_inset()
        cmd = args.get("LatexCommand", "")
        if cmd == "label":
            return "", [], args.get("name", "")
        if cmd in ("ref", "vref", "pageref", "vpageref", "eqref"):
            return f"\x04{args.get('reference', '')}\x04", [], None
        if cmd == "href":
            target = args.get("target", "")
            name = args.get("name", "")
            if not name or name == target:
                return f"<{target}>", [], None
            return f"[{name}]({target})", [], None
        if cmd == "bibitem":
            return f"\x05{args.get('key', '')}\x05", [], None
        if cmd in ("input", "include"):
            fname = args.get("filename", "")
            return self.parse_include(fname), [], None
        # toc / printindex / nomencl -- generated content, not source text.
        return "", [], None

    def parse_include(self, filename: str) -> str:
        path = os.path.join(self.base_dir, filename)
        if not os.path.exists(path):
            return ""
        sub = LyxParser(read_lyx_body(path), os.path.dirname(path) or ".")
        paras = sub.parse_paragraphs(("\\end_body",))
        text = " ".join(p.text.strip() for p in paras if p.text.strip())
        # The caller runs finish_inline() over the whole paragraph, so hand back
        # unescaped text rather than escaping it twice.
        return text.replace("\\_", "_")


def _int(value: str | None) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def read_lyx_body(path: str) -> list[str]:
    with open(path, encoding="utf-8", errors="replace") as handle:
        lines = handle.read().split("\n")
    for idx, line in enumerate(lines):
        if line.startswith("\\begin_body"):
            return lines[idx + 1:]
    return lines


# --------------------------------------------------------------------------------------
# Inline post-processing
# --------------------------------------------------------------------------------------

CODEISH = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*(\(\))?$")


def _span(marker: str, text: str) -> str:
    """Rebalance one emphasis span so the markers hug non-space characters."""
    lead = text[: len(text) - len(text.lstrip())]
    trail = text[len(text.rstrip()):]
    core = text.strip()
    if not core:
        return text
    if marker == "*" and CODEISH.match(core) and re.search(r"[_.()]", core):
        return f"{lead}`{core}`{trail}"
    return f"{lead}{marker}{core}{marker}{trail}"


def finish_inline(text: str) -> str:
    """Resolve style sentinels and escape the characters Markdown would misread."""
    for sentinel, marker in ((EMPH, "*"), (BOLD, "**"), (CODE, "`")):
        out, parts = [], text.split(sentinel)
        for idx, part in enumerate(parts):
            out.append(_span(marker, part) if idx % 2 else part)
        text = "".join(out)
    text = re.sub(r"\s+", " ", text).strip()
    # Underscores are common in API names, so escape them -- but never inside inline
    # code, autolinks or link targets, where the backslash would become literal.
    pieces = re.split(r"(`[^`]*`|<[^ >]+>|\]\([^)]*\))", text)
    for idx, piece in enumerate(pieces):
        if idx % 2 == 0:
            pieces[idx] = piece.replace("_", r"\_")
    return "".join(pieces)


# --------------------------------------------------------------------------------------
# Code fence language detection
# --------------------------------------------------------------------------------------


def guess_language(code: str) -> str:
    """Pick a fence language. Most listings in this book are Python, so that is the
    fallback, but shell sessions, XML/Glade files and .desktop entries are common too."""
    sample = code.strip()
    low = sample.lower()
    if sample.startswith("<?xml") or re.match(r"^\s*<[a-zA-Z!/]", sample):
        return "xml"
    if re.search(r"^\s*\[(Desktop Entry|[A-Za-z ]+)\]\s*$", sample, re.M):
        return "ini"
    if re.search(r"\b(msgid|msgstr)\b", sample):
        return "po"
    if re.search(r"^\s*(sudo|apt-get|apt|yum|cd|ls|cp|mv|chmod|mkdir|rm|\./|msgfmt|"
                 r"xgettext|intltool-\w+|make|gcc|export|source|pkg-config|\$)\b",
                 low, re.M):
        return "bash"
    if re.search(r"^\s*(using |namespace )|\bpublic static void\b|\bConsole\.", sample):
        return "csharp"
    return "python"


# --------------------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------------------

LIST_STYLES = {"Itemize": "-", "Enumerate": "1."}
DEF_STYLES = ("Description", "Labeling")


class Chapter:
    def __init__(self, title: str, number: int, appendix: bool):
        self.title = title
        self.number = number
        self.appendix = appendix
        self.blocks: list = []
        self.footnotes: list[str] = []
        self.slug = ""
        self.label: str | None = None
        self.unnumbered = False

    @property
    def filename(self) -> str:
        return f"{self.number:02d}-{self.slug}.md"


def split_chapters(blocks: list) -> list[Chapter]:
    chapters: list[Chapter] = []
    front = Chapter("Changelog", 0, False)
    front.slug = "changelog"
    front.unnumbered = True
    current = front
    appendix = False
    for block in blocks:
        if isinstance(block, Para) and block.style == "Bibliography" \
                and current.title != "Bibliography":
            # LyX generates the heading for the bibliography; give it its own page.
            current = Chapter("Bibliography", len(chapters) + 1, False)
            current.slug = "bibliography"
            current.unnumbered = True
            chapters.append(current)
        if isinstance(block, Para) and block.style == "Chapter":
            if APPENDIX in block.text:
                appendix = True
            title = block.text.replace(APPENDIX, "").replace(r"\_", "_").strip()
            current = Chapter(title, len(chapters) + 1, appendix)
            current.slug = slugify(title)
            chapters.append(current)
            continue
        current.blocks.append(block)
    return [front] + chapters


def render_chapter(chapter: Chapter, labels: dict[str, tuple[str, str]]) -> str:
    out: list[str] = []
    pending_label: str | None = None
    code_buffer: list[str] = []
    prev_style = ""

    def flush_code() -> None:
        nonlocal code_buffer
        if not code_buffer:
            return
        while code_buffer and not code_buffer[0].strip():
            code_buffer.pop(0)
        while code_buffer and not code_buffer[-1].strip():
            code_buffer.pop()
        if code_buffer:
            body = "\n".join(code_buffer)
            out.append(f"```{guess_language(body)}\n{body}\n```\n")
        code_buffer = []

    for block in chapter.blocks:
        if isinstance(block, Figure):
            flush_code()
            out.append(render_figure(block))
            continue
        if isinstance(block, QuoteBlock):
            flush_code()
            body = "\n".join(f"> {p.text}" for p in block.paras)
            out.append(body + "\n")
            continue

        para = block
        if para.style == "LyX-Code":
            code_buffer.append(para.text.rstrip())
            prev_style = para.style
            continue
        flush_code()

        text = resolve_refs(para.text, labels)
        style = para.style.rstrip("*")

        if style in HEADING_STYLES:
            level = HEADING_STYLES[style]
            anchor = f" {{#{slugify(para.label)}}}" if para.label else ""
            out.append(f"{'#' * level} {unescape_heading(text)}{anchor}\n")
            pending_label = None
        elif style in LIST_STYLES:
            marker = LIST_STYLES[style]
            out.append(f"{marker} {text}")
            if prev_style not in LIST_STYLES:
                pass
        elif style in DEF_STYLES:
            term, rest = split_definition(text)
            # A label with no body (the stock-icon tables) is really just a list item.
            out.append(f"{term}\n: {rest}\n" if rest else f"- {term}")
        elif style == "Bibliography":
            out.append(render_bibitem(para.text, labels))
        elif style == "Date":
            out.append(f"*{text}*\n")
        elif style in ("Title", "Author"):
            continue
        elif not text.strip():
            if para.label:
                pending_label = para.label
        else:
            out.append(text + "\n")

        if para.label and style not in HEADING_STYLES and text.strip():
            out.append(f'<a id="{slugify(para.label)}"></a>\n')

        # A label-only paragraph right after a heading belongs to that heading; the
        # two-pass label index already recorded it, so emit a plain anchor here.
        if pending_label and (text.strip() or para is chapter.blocks[-1]):
            out.append(f'<a id="{slugify(pending_label)}"></a>\n')
            pending_label = None

        for child in para.children:
            if isinstance(child, Figure):
                out.append(render_figure(child))
            elif isinstance(child, QuoteBlock):
                out.append("\n".join(f"> {p.text}" for p in child.paras) + "\n")

        prev_style = para.style

    flush_code()
    if pending_label:
        out.append(f'<a id="{slugify(pending_label)}"></a>\n')

    body = join_blocks(out)
    if chapter.footnotes:
        body += "\n" + "\n".join(
            f"[^{n}]: {resolve_refs(t, labels)}" for n, t in enumerate(chapter.footnotes, 1)
        ) + "\n"
    return body


def join_blocks(parts: list[str]) -> str:
    """Join rendered pieces, keeping consecutive list items in one list."""
    text = ""
    for part in parts:
        if not text:
            text = part
            continue
        is_item = part.startswith(("- ", "1. "))
        was_item = text.rstrip("\n").split("\n")[-1].startswith(("- ", "1. "))
        text = text.rstrip("\n") + ("\n" if is_item and was_item else "\n\n") + part
    return text.strip() + "\n"


def split_definition(text: str) -> tuple[str, str]:
    """Split a Description/Labeling paragraph into its term and its definition.

    LyX puts the term first and the definition after the first space, but this book
    routinely uses terms containing spaces (``foo(a, b) - does a thing``), so prefer an
    explicit ``-`` or ``:`` separator when one is present.
    """
    for separator in (" - ", ": "):
        head, sep, tail = text.partition(separator)
        if sep and len(head) <= 80:
            return head.strip(), tail.strip()
    term, _, rest = text.partition(" ")
    return term.strip(), rest.strip()


def unescape_heading(text: str) -> str:
    return text.replace(r"\_", "_")


def render_figure(fig: Figure) -> str:
    caption = fig.caption or ""
    caption = caption.replace(r"\_", "_")
    attrs = ""
    if fig.scale and fig.scale != 100:
        attrs = f"{{width={fig.scale}%}}"
    anchor = f'<a id="{slugify(fig.label)}"></a>\n\n' if fig.label else ""
    return f"{anchor}![{caption}]({fig.path}){attrs}\n"


def render_bibitem(text: str, labels: dict[str, tuple[str, str]]) -> str:
    match = re.match(r"\x05([^\x05]*)\x05\s*(.*)", text, re.S)
    if not match:
        return resolve_refs(text, labels) + "\n"
    key, rest = match.group(1), resolve_refs(match.group(2).strip(), labels)
    return f'- <a id="{slugify("bib-" + key)}"></a>{rest}\n'


def resolve_refs(text: str, labels: dict[str, tuple[str, str]]) -> str:
    def repl(match: re.Match) -> str:
        name = match.group(1)
        target = labels.get(name)
        if not target:
            return f"*{name}*"
        filename, title = target
        return f"[{title}]({filename.replace('.md', '.html')}#{slugify(name)})"

    text = re.sub(r"\x04([^\x04]*)\x04", repl, text)
    return re.sub(r"\x05[^\x05]*\x05", "", text)


# --------------------------------------------------------------------------------------
# Label index (first pass)
# --------------------------------------------------------------------------------------


def index_labels(chapters: list[Chapter]) -> dict[str, tuple[str, str]]:
    labels: dict[str, tuple[str, str]] = {}
    for chapter in chapters:
        last_heading = chapter.title
        if chapter.label:
            labels[chapter.label] = (chapter.filename, chapter.title)
        for block in chapter.blocks:
            if isinstance(block, Figure):
                if block.label:
                    labels[block.label] = (chapter.filename, block.caption or "figure")
                continue
            if not isinstance(block, Para):
                continue
            if block.style.rstrip("*") in HEADING_STYLES:
                last_heading = block.text.replace(r"\_", "_")
            if block.label:
                labels[block.label] = (chapter.filename, last_heading)
            for child in block.children:
                if isinstance(child, Figure) and child.label:
                    labels[child.label] = (chapter.filename, child.caption or "figure")
    return labels


# --------------------------------------------------------------------------------------
# Heading/label attachment
# --------------------------------------------------------------------------------------


def attach_labels(chapters: list[Chapter]) -> None:
    """Move a label from a label-only paragraph onto the heading just above it."""
    for chapter in chapters:
        blocks = chapter.blocks
        for idx, block in enumerate(blocks):
            if not isinstance(block, Para) or not block.label or block.text.strip():
                continue
            for back in range(idx - 1, max(-1, idx - 3), -1):
                prev = blocks[back]
                if isinstance(prev, Para) and prev.style.rstrip("*") in HEADING_STYLES:
                    if not prev.label:
                        prev.label = block.label
                        block.label = None
                    break
                if isinstance(prev, Para) and prev.text.strip():
                    break


def attach_chapter_labels(chapters: list[Chapter]) -> None:
    """A label in the opening paragraph of a chapter labels the chapter itself."""
    for chapter in chapters:
        for block in chapter.blocks[:2]:
            if isinstance(block, Para) and block.label and not block.text.strip():
                chapter.label = block.label
                block.label = None
                break


# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------


def front_matter(chapter: Chapter, total: int) -> str:
    fields = [
        "---",
        "layout: chapter",
        f'title: "{chapter.title}"',
        f"number: {chapter.number}",
    ]
    if chapter.appendix:
        fields.append("appendix: true")
    if chapter.unnumbered:
        fields.append("unnumbered: true")
    if chapter.label:
        fields.append(f"anchor: {slugify(chapter.label)}")
    fields.append("---")
    return "\n".join(fields) + "\n\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="path to the .lyx book")
    parser.add_argument("--outdir", default="_chapters")
    args = parser.parse_args(argv)

    base_dir = os.path.dirname(os.path.abspath(args.source)) or "."
    lyx = LyxParser(read_lyx_body(args.source), base_dir)
    blocks = lyx.parse_paragraphs(("\\end_body",))

    chapters = split_chapters(blocks)
    attach_labels(chapters)
    attach_chapter_labels(chapters)

    # Footnotes were collected document-wide; hand each one to its chapter.
    assign_footnotes(chapters, lyx.footnotes)

    labels = index_labels(chapters)
    os.makedirs(args.outdir, exist_ok=True)

    written = 0
    for chapter in chapters:
        if not chapter.blocks:
            continue
        body = render_chapter(chapter, labels)
        if not body.strip():
            continue
        path = os.path.join(args.outdir, chapter.filename)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(front_matter(chapter, len(chapters)) + body)
        written += 1
        print(f"wrote {path} ({len(body.splitlines())} lines)")
    print(f"{written} files, {len(labels)} labels indexed")
    return 0


def assign_footnotes(chapters: list[Chapter], notes: list[str]) -> None:
    """Renumber the document-wide footnote list per chapter."""
    counter = 0
    for chapter in chapters:
        local = 0
        for block in chapter.blocks:
            if not isinstance(block, Para):
                continue
            hits = re.findall(r"\[\^(\d+)\]", block.text)
            for _ in hits:
                counter += 1
                local += 1
                chapter.footnotes.append(notes[counter - 1] if counter <= len(notes) else "")
            if hits:
                start = local - len(hits) + 1
                block.text = renumber(block.text, start)


def renumber(text: str, start: int) -> str:
    counter = [start - 1]

    def repl(_match: re.Match) -> str:
        counter[0] += 1
        return f"[^{counter[0]}]"

    return re.sub(r"\[\^\d+\]", repl, text)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
