import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "custom-images-index.py")


class IndexTest(unittest.TestCase):
    def test_index_lists_only_known_folders_and_images(self):
        with tempfile.TemporaryDirectory() as root:
            for d, f in [("common", "a.png"), ("common", "x.txt"), ("org-3", "b.SVG"), ("other", "c.png"), ("org-x", "d.png")]:
                os.makedirs(os.path.join(root, d), exist_ok=True)
                open(os.path.join(root, d, f), "w").close()
            subprocess.run([sys.executable, SCRIPT, root], check=True)
            idx = json.load(open(os.path.join(root, "index.json")))
            self.assertEqual(idx, {"folders": {"common": ["a.png"], "org-3": ["b.SVG"]}})
            self.assertEqual(os.stat(os.path.join(root, "index.json")).st_mode & 0o777, 0o644)


if __name__ == "__main__":
    unittest.main()
