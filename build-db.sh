#!/bin/sh
# Rebuild database.html from its parts.
# designs.js is the editable database; it gets inlined here so the
# built page is a single self-contained file that works anywhere.
set -e
cd "$(dirname "$0")"
{
  cat _d1_shell.html
  cat _p2_kit.html
  cat _k2_dash_css.html
  cat _d2_head.html
  cat _d_kitbody.html
  cat _k2_dash_markup.html
  cat _d2_tail.html
  echo '<script>'
  cat designs.js
  echo '</script>'
  cat _d3_app.html
  cat _p6_interactions.html
  cat _d4_editor.html
} > database.html
echo "database.html: $(wc -l < database.html) lines, $(du -h database.html | cut -f1), $(grep -c '^{"id"' designs.js) designs"
