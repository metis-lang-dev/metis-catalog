#!/bin/sh
# metis-catalog diagnostics gate (CI.md): every .llp, compiled
# standalone by metisc, must carry no error-severity diagnostic —
# except the files listed (with reasons) in ci/diag-exempt.txt. A domain
# package's extension (domains/**/extensions/*.llp) only compiles with the
# program it extends: it is compiled against its package's program
# (`--base`, the manifest's program:), the served chain's first link as the
# loader and the bundle emitter build it (catalog-entry step 2). metisc
# takes one base, so an extension that extends another extension is not
# expressible here yet: today every extension extends the program.
# METISC as in check.sh. A listed file that now typechecks is reported
# so the exemption can be dropped.
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
METISC=${METISC:-$ROOT/../metis-lang/src/metisc}
cd "$ROOT"
EXEMPT=$(grep -v '^#' ci/diag-exempt.txt | awk 'NF{print $1}')
fail=0; n=0
for f in $(git ls-files '*.llp'); do
  n=$((n + 1))
  # a metisc CRASH (Fatal error / exit != 0) is never "clean": its
  # stdout is empty, so counting error rows alone read it as 0 errors —
  # that is how road_zones' DiagnosticDefect passed as clean.
  base=""
  case "$f" in
    domains/*/extensions/*.llp)
      pkg=$(dirname "$(dirname "$f")")
      prog=$(sed -n 's/^program:[[:space:]]*\([^[:space:]#]*\).*/\1/p' "$pkg/domain.yaml" 2>/dev/null | head -1)
      if [ -z "$prog" ] || [ ! -f "$pkg/$prog" ]; then
        echo "FAIL $f: an extension of $pkg, whose manifest names no program to compile it with"
        fail=1
        continue
      fi
      base="$pkg/$prog" ;;
  esac
  if ! out=$("$METISC" --diagnostics-json "$f" ${base:+--base "$base"} 2>&1); then
    echo "FAIL $f: metisc crashed — $(printf '%s\n' "$out" | tail -1)"
    fail=1
    continue
  fi
  errs=$(printf '%s\n' "$out" | grep -c '"severity":"error"' || true)
  if printf '%s\n' "$EXEMPT" | grep -qx "$f"; then
    [ "$errs" = 0 ] && echo "NOTE $f typechecks now — drop it from ci/diag-exempt.txt"
    echo "exempt $f ($errs error(s))"
    continue
  fi
  if [ "$errs" != 0 ]; then
    echo "FAIL $f: $errs error diagnostic(s)"
    "$METISC" --diagnostics "$f" ${base:+--base "$base"} 2>&1 | grep '^error' | head -5
    fail=1
  else
    echo "ok   $f${base:+ (with $base)}"
  fi
done
echo "diagnosed $n catalogs"
[ "$fail" = 0 ] && echo "DIAGNOSTICS GREEN" || exit 1
