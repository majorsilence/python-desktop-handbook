#!/usr/bin/env sh
#
# Extract the translatable strings, merge them into the existing translations,
# and compile the result.
#
# In a real project a build system does this: Meson has i18n.gettext(), which
# generates the same commands from a LINGUAS file.
#
set -eu

cd "$(dirname "$0")"

domain=greeter
languages="de fr"

# --- extract -------------------------------------------------------------------
#
# xgettext reads Python and GtkBuilder XML. The keywords tell it which calls mark
# a string: the :1,2 on ngettext means both the singular and the plural argument,
# and the :1c,2 on pgettext means the first argument is a context.
xgettext \
  --from-code=UTF-8 \
  --add-comments=Translators: \
  --keyword=_ \
  --keyword=N_ \
  --keyword=ngettext:1,2 \
  --keyword=pgettext:1c,2 \
  --package-name="$domain" \
  --copyright-holder="The example authors" \
  --msgid-bugs-address="you@example.com" \
  --output="po/$domain.pot" \
  greeter.py window.ui

# --- merge ---------------------------------------------------------------------
#
# msgmerge keeps existing translations and marks changed ones as fuzzy, rather
# than throwing away work when a string is edited.
for language in $languages; do
  if [ -f "po/$language.po" ]; then
    msgmerge --update --backup=none --quiet "po/$language.po" "po/$domain.pot"
  else
    msginit --no-translator --locale="$language" \
            --input="po/$domain.pot" --output="po/$language.po"
  fi
done

# --- compile -------------------------------------------------------------------
#
# The .mo has to land at <locale dir>/<language>/LC_MESSAGES/<domain>.mo, and the
# path is not negotiable: gettext looks there and nowhere else.
for language in $languages; do
  mkdir -p "locale/$language/LC_MESSAGES"
  msgfmt --check --output-file="locale/$language/LC_MESSAGES/$domain.mo" \
         "po/$language.po"
done

echo "extracted, merged and compiled: $languages"
echo "try it with: LANGUAGE=de python3 greeter.py"
