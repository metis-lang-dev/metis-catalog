#!/bin/sh
# metis-catalog diagnostics gate (CI.md): every .llp, compiled
# standalone by metisc, must carry no error-severity diagnostic —
# except the files listed (with reasons) in ci/diag-exempt.txt.
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
  if ! out=$("$METISC" --diagnostics-json "$f" 2>&1); then
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
    "$METISC" --diagnostics "$f" 2>&1 | grep '^error' | head -5
    fail=1
  else
    echo "ok   $f"
  fi
done
echo "diagnosed $n catalogs"
[ "$fail" = 0 ] && echo "DIAGNOSTICS GREEN" || exit 1
