#!/usr/bin/env python3
"""Write index.json for the Canvas custom image folders.

Usage: custom-images-index.py /srv/grafana-images
Layout: <root>/common/*.png, <root>/org-<orgId>/*.png  (one sub-folder per Grafana org).
Run from cron every minute: the picker reads <root>/index.json at runtime.
"""
import json
import os
import re
import sys
import tempfile

IMAGE = re.compile(r"\.(png|jpe?g|gif|webp|svg)$", re.I)
FOLDER = re.compile(r"^(common|org-\d+)$")


def build_index(root):
    folders = {}
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if FOLDER.match(name) and os.path.isdir(path):
            folders[name] = sorted(f for f in os.listdir(path) if IMAGE.search(f) and os.path.isfile(os.path.join(path, f)))
    return {"folders": folders}


def write_index(root):
    data = json.dumps(build_index(root), indent=1)
    out = os.path.join(root, "index.json")
    # skip the write when nothing changed
    if os.path.exists(out) and open(out).read() == data:
        return
    fd, tmp = tempfile.mkstemp(dir=root)
    with os.fdopen(fd, "w") as f:
        f.write(data)
    os.chmod(tmp, 0o644)  # Grafana runs as uid 472, must be able to read it
    os.replace(tmp, out)  # atomic: the picker never sees a half-written file


if __name__ == "__main__":
    write_index(sys.argv[1])
