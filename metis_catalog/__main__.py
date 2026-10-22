"""python -m metis_catalog list [--json] — the loader's CLI, moved to metispy (metis.catalog.manifests_cli)."""
import sys

from metis.catalog.manifests_cli import main

if __name__ == "__main__":
    sys.exit(main())
