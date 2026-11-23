"""Download the public files this project needs, pinned by URL and checksum.

Usage::

    python -m brainchimp.fetch data/            # everything
    python -m brainchimp.fetch data/ mindgrab   # one group only

No file needs a registration. The macaque images of PRIME-DE are not here: they
come from the supervisor's dataset (see the README).
"""

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

_BRAINCHOP_CLI = (
    "https://github.com/neuroneural/brainchop-cli/raw/31150c39dae90dba3d18b00d05d32eba273056af"
)
_MODELS = (
    "https://github.com/neuroneural/brainchop-models/raw/528f2d8d2ca937968b2d4b2b9ef9fa9170f4b9cf"
)
_NMT = "https://templateflow.s3.amazonaws.com/tpl-NMT31Sym"

#: group -> list of (relative destination, URL, SHA-256)
FILES = {
    "mindgrab": [
        (
            "mindgrab/model.json",
            f"{_MODELS}/meshnet/mindgrab/model.json",
            "e321f27014eb05f187667873d5301be57f9aac4c5be427e68e9f484748d643fd",
        ),
        (
            "mindgrab/model.pth",
            f"{_MODELS}/meshnet/mindgrab/model.pth",
            "31f1bda17b8d3eee17a54cf3f199899763a6615a049f05ab2a05f18eb98ec23a",
        ),
    ],
    "human": [
        (
            "human/brain.nii.gz",
            f"{_BRAINCHOP_CLI}/examples/brain.nii.gz",
            "9f5708dd1980fe0017ad70f63d895bae66bd9f5487eb1c38d129591116113613",
        ),
    ],
    "nmt": [
        (
            "nmt/tpl-NMT31Sym_res-1_desc-brain_mask.nii.gz",
            f"{_NMT}/tpl-NMT31Sym_res-1_desc-brain_mask.nii.gz",
            "e2013fa4a493124f0c8c1bf74cba4be836ee815e0740e38f417ebf696aaca85d",
        ),
        (
            "nmt/tpl-NMT31Sym_res-1_T1w.nii.gz",
            f"{_NMT}/tpl-NMT31Sym_res-1_T1w.nii.gz",
            "3ed1ec95df5b05de55f6a2e4a3e44e7395aff372ee36a74f31c614cd816ca9d3",
        ),
    ],
}


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_file(dest, url, sha256):
    """Download ``url`` to ``dest`` unless a file with the right checksum is there."""
    dest = Path(dest)
    if dest.exists() and _sha256(dest) == sha256:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    urllib.request.urlretrieve(url, tmp)
    if _sha256(tmp) != sha256:
        tmp.unlink()
        raise RuntimeError(f"Checksum mismatch for {url}")
    tmp.replace(dest)
    return dest


def fetch(root, groups=None):
    """Download the files of ``groups`` (all by default) under ``root``."""
    root = Path(root)
    paths = []
    for group in groups or FILES:
        for rel, url, sha256 in FILES[group]:
            print(f"{group}: {rel}", file=sys.stderr)
            paths.append(fetch_file(root / rel, url, sha256))
    return paths


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("root", type=Path, help="destination folder, e.g. data/")
    parser.add_argument("groups", nargs="*", choices=sorted(FILES), help="default: all")
    args = parser.parse_args(argv)
    fetch(args.root, args.groups)


if __name__ == "__main__":
    main()
