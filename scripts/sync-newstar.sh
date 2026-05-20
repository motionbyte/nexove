#!/usr/bin/env bash
# Sync Sun texture: images/svg/newStar.svg -> textures/newStar.png
# Prefers images/newStar-master.png (white logo on black) for full thorn/spike detail.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SVG="$ROOT/images/svg/newStar.svg"
MASTER="$ROOT/images/newStar-master.png"
OUT="$ROOT/textures/newStar.png"
TMP="${OUT}.tmp.png"
EXPORT_SVG="${TMP}.export.svg"
SIZE="${NEWSTAR_SIZE:-1024}"

if [[ ! -f "$SVG" ]]; then
  echo "sync-newstar: missing $SVG" >&2
  exit 1
fi

if [[ -f "$MASTER" ]]; then
  python3 "$ROOT/scripts/postprocess-newstar.py" "$MASTER" "$OUT" "$SIZE" --master
  echo "sync-newstar: $MASTER -> $OUT (${SIZE}px, master shape)"
  exit 0
fi

# Quick Look renders light SVG paths on white; spikes vanish. Export on black instead.
python3 - "$SVG" "$EXPORT_SVG" <<'PY'
import re, sys
from pathlib import Path
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
text = src.read_text()
match = re.search(r"<svg[^>]*>", text)
if not match:
    raise SystemExit("sync-newstar: invalid SVG")
rect = '<rect width="100%" height="100%" fill="#000000"/>'
dst.write_text(text[: match.end()] + "\n" + rect + text[match.end() :])
PY

convert_svg() {
  if command -v qlmanage >/dev/null 2>&1; then
    qlmanage -t -s "$SIZE" -o "$ROOT/textures" "$EXPORT_SVG" >/dev/null 2>&1
    local gen="$ROOT/textures/$(basename "$EXPORT_SVG").png"
    if [[ -f "$gen" ]]; then
      mv -f "$gen" "$TMP"
      return 0
    fi
  fi

  if command -v rsvg-convert >/dev/null 2>&1; then
    rsvg-convert -w "$SIZE" -h "$SIZE" -o "$TMP" "$EXPORT_SVG"
    return 0
  fi

  if command -v magick >/dev/null 2>&1; then
    magick -background black -density 300 "$EXPORT_SVG" -resize "${SIZE}x${SIZE}" "$TMP"
    return 0
  fi

  if command -v convert >/dev/null 2>&1; then
    convert -background black -density 300 "$EXPORT_SVG" -resize "${SIZE}x${SIZE}" "$TMP"
    return 0
  fi

  return 1
}

mkdir -p "$ROOT/textures"

if ! convert_svg; then
  echo "sync-newstar: no converter found (need qlmanage, rsvg-convert, or ImageMagick)" >&2
  exit 1
fi

python3 "$ROOT/scripts/postprocess-newstar.py" "$TMP" "$OUT" "$SIZE"
rm -f "$TMP" "$EXPORT_SVG"
echo "sync-newstar: $SVG -> $OUT (${SIZE}px, SVG export — add images/newStar-master.png for full shape)"
