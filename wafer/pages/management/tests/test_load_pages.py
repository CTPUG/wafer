# Test load_pages management commands

import os
import shutil
import tempfile

from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

PAGES = {
    "page1.md": "\n".join([
        "---",
        "name: Page 1",
        "---",
        "This is page 1.",
    ]),
    "page2.md": "\n".join([
        "---",
        "name: Page 2",
        "---",
        "This is page 2.",
    ]),
}


class LoadPagesTest(TestCase):
    def setUp(self):
        self._page_dir = tempfile.mkdtemp()
        for page, data in PAGES.items():
            with open(os.path.join(self._page_dir, page), "w") as f:
                f.write(data)

    def tearDown(self):
        shutil.rmtree(self._page_dir)

    def test_load_pages(self):
        out = StringIO()
        with self.settings(PAGE_DIR=self._page_dir + "/"):
            call_command('load_pages', stdout=out)
        self.assertEqual(out.getvalue(), "\n".join([
            "Loaded page page1",
            "Loaded page page2",
            "",
        ]))
