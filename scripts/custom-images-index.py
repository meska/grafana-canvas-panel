#!/usr/bin/env python3
"""Keep the Canvas custom image folders in sync with Grafana and write index.json.

Usage: custom-images-index.py <images dir> [--grafana-db /srv/grafana/grafana.db]
Layout: <dir>/common/, <dir>/org-<orgId>-<slug>/ (the slug is cosmetic, the id matters).
With --grafana-db (read-only) a folder is created for every org, and a bare org-<id> folder is renamed
to org-<id>-<slug>. Folders and files are never deleted. Run from cron every minute.
"""
import json
import os
import re
import sqlite3
import sys
import tempfile
import unicodedata

IMAGE = re.compile(r"\.(png|jpe?g|gif|webp|svg)$", re.I)
FOLDER = re.compile(r"^(common|org-\d+(-[a-z0-9-]*)?)$")


def slugify(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def sync_orgs(root, db):
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=5)
    try:
        orgs = con.execute("select id, name from org").fetchall()
    finally:
        con.close()
    existing = os.listdir(root)
    for org_id, name in orgs:
        target = f"org-{org_id}-{slugify(name)}".rstrip("-")
        has_dir = any(d == f"org-{org_id}" or d.startswith(f"org-{org_id}-") for d in existing)
        if f"org-{org_id}" in existing and target not in existing:
            os.rename(os.path.join(root, f"org-{org_id}"), os.path.join(root, target))
        elif not has_dir:
            os.makedirs(os.path.join(root, target))
            os.chmod(os.path.join(root, target), 0o755)  # makedirs mode is masked by umask


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
    args = sys.argv[1:]
    db = args[args.index("--grafana-db") + 1] if "--grafana-db" in args else None
    if db:
        sync_orgs(args[0], db)
    write_index(args[0])
