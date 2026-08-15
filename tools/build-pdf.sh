#!/usr/bin/env bash
#
# Build the PyGTK Notebook PDF from the Markdown chapters.
#
# The output aims to match what LyX used to produce: LaTeX `book` class, 10pt,
# two-sided, custom 20.95cm x 27.31cm paper, numbered chapters with an appendix,
# a table of contents and a list of figures, and coloured hyperlinks.
#
# Requires: pandoc, and a LaTeX engine (xelatex by default, pdflatex works too).
#
#   ./tools/build-pdf.sh                    # -> build/pygtk-notebook.pdf
#   ./tools/build-pdf.sh -o out/book.pdf    # somewhere else
#   PDF_ENGINE=pdflatex ./tools/build-pdf.sh
#
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

output="build/pygtk-notebook.pdf"
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
    # Cross-chapter links collapse to plain anchors in a single-file PDF.
    body = re.sub(r'\]\(\d+-[a-z0-9-]+\.html#', "](#", body)
    body = re.sub(r'\]\((\d+-[a-z0-9-]+)\.html\)', r"](#\1)", body)
    # Footnotes are numbered per chapter; namespace them so one file can hold them all.
    stem = os.path.basename(path)[:-3]
    body = re.sub(r'\[\^(\w+)\]', lambda m: f"[^{stem}-{m.group(1)}]", body)

    if meta.get("appendix") == "true" and not appendix_started:
        appendix_started = True
        out.write("```{=latex}\n\\appendix\n```\n\n")

    attrs = []
    if meta.get("anchor"):
        attrs.append("#" + meta["anchor"])
    if meta.get("unnumbered") == "true":
        attrs.append(".unnumbered")
    suffix = " {" + " ".join(attrs) + "}" if attrs else ""
    out.write(f"# {meta.get('title', os.path.basename(path))}{suffix}\n\n")
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
papersize: custom
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
  --from=markdown+definition_lists+footnotes+link_attributes+raw_attribute+smart \
  --to=pdf \
  --pdf-engine="$engine" \
  --top-level-division=chapter \
  --resource-path="$repo_root" \
  --highlight-style=tango \
  --output="$output"

echo "wrote $output"
