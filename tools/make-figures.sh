#!/usr/bin/env bash
#
# Regenerate the book figures that are produced by examples.
#
# Some illustrations in this book are the output of a listing rather than a
# screenshot.  Running them here keeps the figure and the code that made it from
# drifting apart: change the example, run this, and the picture in the book
# changes with it.
#
#   ./tools/make-figures.sh
#
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# example script -> figure it produces, relative to images/
figures=(
  "examples/gtk4/cairo/paths-and-fills.py:paths-and-fills.png:gtk4-cairo"
  "examples/gtk4/cairo/text-with-pango.py:text-with-pango.png:gtk4-cairo"
  "examples/gtk4/cairo/antialias.py:antialias.png:gtk4-cairo"
  "examples/gtk4/cairo/draw-to-png.py:draw-to-png.png:gtk4-cairo"
  "examples/gtk4/cairo/surfaces.py:surfaces.png:gtk4-cairo"
)

for entry in "${figures[@]}"; do
  script="${entry%%:*}"
  rest="${entry#*:}"
  produced="${rest%%:*}"
  target_dir="images/${rest#*:}"

  mkdir -p "$target_dir"
  ( cd "$(dirname "$script")" && python3 "$(basename "$script")" >/dev/null )
  mv "$(dirname "$script")/$produced" "$target_dir/$produced"
  echo "wrote $target_dir/$produced"
done

# The vector output is a by-product of the surfaces example, not a book figure.
rm -f examples/gtk4/cairo/surfaces.pdf \
      examples/gtk4/cairo/surfaces.svg \
      examples/gtk4/cairo/surfaces.ps
