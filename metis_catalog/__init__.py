"""metis_catalog — the catalog's loader moved into metispy as metis.catalog.manifests (metis-packages
s-65778b98: the runtime's own distribution), re-exported here for one release (removed at r0.2).
This package stays the domains' data: domains/ and tools/ beside it (a checkout) or in it (the
wheel), which metis.catalog.installed() and manifests.data_dir() find through it (the default root is
the cwd: release-r02).

    import metis_catalog as mc        # → from metis.catalog import manifests as mc
"""
import warnings

from metis.catalog.manifests import *  # noqa: F401,F403
from metis.catalog.manifests import (KEYS, INTENT_KEYS, SKIP, Domain, ManifestError, check_manifest,  # noqa: F401
                                     data_dir, domains, get, index, readme_head, root, walk)

__version__ = "0.1.1"

warnings.warn("metis_catalog is metis.catalog.manifests now (metispy >= 0.1.2); metis_catalog re-exports it "
              "until r0.2", DeprecationWarning, stacklevel=2)
