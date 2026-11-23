"""Shared test fixtures.

Downloads are cached in ``~/.cache/brainchimp`` (or ``$BRAINCHIMP_CACHE``), so
only the first test run needs the network.
"""

import os
from pathlib import Path

import pytest

from brainchimp.fetch import FILES, fetch, fetch_file

CACHE = Path(os.getenv("BRAINCHIMP_CACHE", Path.home() / ".cache" / "brainchimp"))


@pytest.fixture(scope="session")
def mindgrab_dir():
    """Folder holding MindGrab's ``model.json`` and ``model.pth``."""
    fetch(CACHE, ["mindgrab"])
    return CACHE / "mindgrab"


@pytest.fixture(scope="session")
def nmt_mask():
    """Path to the brain mask of the NMT v2 macaque template (0.25 mm voxels)."""
    rel, url, sha256 = FILES["nmt"][0]
    return fetch_file(CACHE / rel, url, sha256)
