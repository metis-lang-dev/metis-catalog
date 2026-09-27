#!/bin/sh
# metis-catalog gates — metisc only (set METISC, default: the sibling
# metis-lang checkout). Gate 1: parse (pretty a) = a over every .llp.
# Gate 2: the committed scene instance grounds to the committed
# canonical program_key — the cross-toolchain identity contract
# (the same key is asserted python-side in metispy's cross-checks).
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
METISC=${METISC:-$ROOT/../metis-lang/src/metisc}
WORK=${TMPDIR:-/tmp}/metis-catalog-check.$$
mkdir -p "$WORK"
trap 'rm -rf "$WORK"' EXIT

echo "== 1. roundtrip over every catalog, pack, demo, scene"
# metisc resolves llp paths relative to the MANIFEST, so the
# generated manifest lives at the repo root with repo-relative paths.
RT="$ROOT/.roundtrip-manifest.tmp"
trap 'rm -rf "$WORK" "$RT"' EXIT
( cd "$ROOT" && for f in road/*.llp packs/*.llp demo/*.llp scenes/*.llp \
                         domains/*/*.llp; do
    printf 'case rt-%s\nllp %s\nsteps 1\nend\n' "$(basename "$f" .llp)" "$f"
  done ) > "$RT"
"$METISC" --roundtrip "$RT"

echo "== 2. canonical keys: scene instance grounds to the committed key"
"$METISC" --keys "$ROOT/scenes/manifest.txt" > "$WORK/keys.txt"
diff -u "$ROOT/goldens/KEYS.txt" "$WORK/keys.txt"

echo "ALL GATES GREEN"
