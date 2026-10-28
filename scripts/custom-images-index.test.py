import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "custom-images-index.py")


def run(root, *extra):
    subprocess.run([sys.executable, SCRIPT, root, *extra], check=True)
    return json.load(open(os.path.join(root, "index.json")))


class IndexTest(unittest.TestCase):
    def test_index_lists_only_known_folders_and_images(self):
        with tempfile.TemporaryDirectory() as root:
            for d, f in [("common", "a.png"), ("common", "x.txt"), ("org-3", "b.SVG"), ("org-4-demo", "c.png"), ("other", "c.png"), ("org-x", "d.png")]:
                os.makedirs(os.path.join(root, d), exist_ok=True)
                open(os.path.join(root, d, f), "w").close()
            idx = run(root)
            self.assertEqual(idx, {"folders": {"common": ["a.png"], "org-3": ["b.SVG"], "org-4-demo": ["c.png"]}})
            self.assertEqual(os.stat(os.path.join(root, "index.json")).st_mode & 0o777, 0o644)

    def test_sync_creates_renames_and_never_deletes(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as dbdir:
            db = os.path.join(dbdir, "g.db")
            con = sqlite3.connect(db)
            con.execute("create table org (id integer, name text)")
            con.executemany("insert into org values (?,?)", [(1, "Maric Automation Srl"), (2, "Comune di Cantù"), (3, "Già fatta")])
            con.commit()
            con.close()
            os.makedirs(os.path.join(root, "org-1"))
            open(os.path.join(root, "org-1", "a.png"), "w").close()  # bare -> renamed, keeps files
            os.makedirs(os.path.join(root, "org-3-vecchio-nome"))  # already named -> untouched
            os.makedirs(os.path.join(root, "org-99-orfana"))  # org gone from db -> kept
            idx = run(root, "--grafana-db", db)
            self.assertEqual(sorted(idx["folders"]), ["org-1-maric-automation-srl", "org-2-comune-di-cantu", "org-3-vecchio-nome", "org-99-orfana"])
            self.assertEqual(idx["folders"]["org-1-maric-automation-srl"], ["a.png"])
            self.assertEqual(os.stat(os.path.join(root, "org-2-comune-di-cantu")).st_mode & 0o777, 0o755)
            # a new org appears later
            con = sqlite3.connect(db)
            con.execute("insert into org values (4, 'Nuova Org')")
            con.commit()
            con.close()
            self.assertIn("org-4-nuova-org", run(root, "--grafana-db", db)["folders"])


if __name__ == "__main__":
    unittest.main()
