#!/usr/bin/env bash
#
# Build the book's PDF from the Markdown chapters.
#
# The output keeps the shape the LyX original had: LaTeX `book` class, 10pt,
# two-sided, custom 20.95cm x 27.31cm paper, parts and numbered chapters with an
# appendix, a table of contents and a list of figures, and coloured hyperlinks.
#
# Requires: pandoc, and a LaTeX engine (xelatex by default, pdflatex works too).
#
#   ./tools/build-pdf.sh                    # -> build/python-desktop-notebook.pdf
#   ./tools/build-pdf.sh -o out/book.pdf    # somewhere else
#   PDF_ENGINE=pdflatex ./tools/build-pdf.sh
#
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

output="build/python-desktop-notebook.pdf"
while [ $# -gt 0 ]; do
  case "$1" in
    -o|--output) output="$2"; shift 2 ;;
    -h|--help) sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

engine="${PDF_ENGINE:-xelatex}"

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "error: $1 is required but not installed." >&2
    echo "  Debian/Ubuntu: sudo apt-get install pandoc texlive-xetex texlive-fonts-recommended texlive-latex-extra" >&2
    exit 1
  }
}
need pandoc
need "$engine"

title="$(sed -n 's/^title: *//p' _config.yml | head -1)"
subtitle="$(sed -n 's/^subtitle: *//p' _config.yml | head -1)"
author="$(sed -n 's/^author: *//p' _config.yml | head -1)"
version="$(sed -n 's/^version: *//p' _config.yml | head -1 | tr -d '"')"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir -p "$(dirname "$output")"

# --- assemble one Markdown file out of the chapters ------------------------------
#
# Per chapter we drop the Jekyll front matter, promote the front-matter title to a
# level-1 heading, and rewrite the two Jekyll-only conventions that pandoc does not
# read: kramdown inline attribute lists on images, and cross-chapter links (which
# become plain intra-document anchors once every chapter lives in one file).

book="$work/book.md"
: > "$book"

python3 - "$book" <<'PY'
import glob
import os
import re
import sys

out = open(sys.argv[1], "w", encoding="utf-8")
appendix_started = False
current_part = None

# Part titles live in _config.yml so the site and the PDF agree on them.
config = open("_config.yml", encoding="utf-8").read()
part_titles = {}
for block in re.finditer(r"^  - number: (\d+)\n    title: (.+)$", config, re.M):
    part_titles[block.group(1)] = block.group(2).strip().strip('"')

def unnumber_headings(body):
    """Add pandoc's .unnumbered class to every heading, skipping fenced code."""
    out, fenced = [], False
    for line in body.split("\n"):
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced:
            match = re.match(r"^(#{2,6} .*?)(?:\s*\{#([^}]*)\})?$", line)
            if match:
                ident = "#" + match.group(2) + " " if match.group(2) else ""
                line = f"{match.group(1)} {{{ident}.unnumbered}}"
        out.append(line)
    return "\n".join(out)


def front_matter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}, text
    meta = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = value.strip().strip('"')
    return meta, text[match.end():]

for path in sorted(glob.glob("_chapters/*.md")):
    meta, body = front_matter(open(path, encoding="utf-8").read())

    # kramdown IAL -> pandoc link attributes:  {: width="50%"}  ->  {width=50%}
    body = re.sub(r'\{:\s*([^}]*)\}',
                  lambda m: "{" + m.group(1).replace('"', "") + "}", body)
    # Bare HTML anchors are dropped by the LaTeX writer; a bracketed span with the
    # same id becomes a real \label that cross references can point at.
    body = re.sub(r'<a id="([^"]+)"></a>', r"[]{#\1}", body)
    # Cross-chapter links collapse to plain anchors in a single-file PDF.
    body = re.sub(r'\]\(\d+-[a-z0-9-]+\.html#', "](#", body)
    body = re.sub(r'\]\((\d+-[a-z0-9-]+)\.html\)', r"](#\1)", body)
    # Footnotes are numbered per chapter; namespace them so one file can hold them all.
    stem = os.path.basename(path)[:-3]
    body = re.sub(r'\[\^(\w+)\]', lambda m: f"[^{stem}-{m.group(1)}]", body)

    # An unnumbered chapter's sections should not be numbered either, but no heading
    # attribute syntax is read by both kramdown and pandoc, so apply it here.
    if meta.get("unnumbered") == "true":
        body = unnumber_headings(body)

    part = meta.get("part")
    if part and part != current_part:
        current_part = part
        title = part_titles.get(part, f"Part {part}")
        out.write("```{=latex}\n\\part{%s}\n```\n\n" % title)

    if meta.get("appendix") == "true" and not appendix_started:
        appendix_started = True
        out.write("```{=latex}\n\\appendix\n```\n\n")

    # The chapter heading is identified by its file stem, so whole-chapter links
    # ("](02-more-gtk4.html)" -> "](#02-more-gtk4)") land on it.
    attrs = ["#" + stem]
    if meta.get("unnumbered") == "true":
        attrs.append(".unnumbered")
    out.write(f"# {meta.get('title', os.path.basename(path))} {{{' '.join(attrs)}}}\n\n")
    if meta.get("anchor"):
        # A second name for the same place, kept from the LyX cross references.
        out.write(f"[]{{#{meta['anchor']}}}\n\n")
    out.write(body.rstrip() + "\n\n")

out.close()
PY

# --- metadata and LaTeX shape ----------------------------------------------------

cat > "$work/meta.yaml" <<EOF
---
title: "$title"
subtitle: "$subtitle"
author: "$author"
date: "Version $version"
documentclass: book
classoption:
  - twoside
  - openright
geometry:
  - paperwidth=20.95cm
  - paperheight=27.31cm
  - margin=2.2cm
  - bindingoffset=0.5cm
fontsize: 10pt
linestretch: 1.0
secnumdepth: 3
toc: true
toc-depth: 3
lof: true
colorlinks: true
linkcolor: blue
filecolor: blue
urlcolor: blue
toccolor: black
links-as-notes: false
lang: en
---
EOF

echo "building $output with $engine ..."
pandoc \
  "$work/meta.yaml" "$book" \
  --from=markdown+definition_lists+footnotes+link_attributes+raw_attribute+smart-raw_tex \
  --to=pdf \
  --pdf-engine="$engine" \
  --top-level-division=chapter \
  --number-sections \
  --resource-path="$repo_root" \
  --highlight-style=tango \
  --output="$output"

echo "wrote $output"
