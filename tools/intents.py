#!/usr/bin/env python3
"""tools/intents.py — a domain's intents: the generator and its check are metispy's
`metis.intents` now (metis-packages s-65778b98). This path stays for one release, so
`python3 tools/intents.py gen|check|schema|skeleton NAME` still works in a checkout (its
root is this checkout); the CLI to use is `python -m metis.intents …` (from a catalog's
directory, or with $METIS_CATALOG). CATALOG.md "intent.yaml"."""
import sys
from pathlib import Path

from metis import intents

intents.ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    sys.exit(intents.main(sys.argv[1:]))
