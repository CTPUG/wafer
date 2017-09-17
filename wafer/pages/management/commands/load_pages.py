import os
import sys

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from wafer.pages.models import Page
import yaml


class Command(BaseCommand):
    help = 'Load pages from markdown files into the DB'

    def handle(self, *args, **options):
        for dirpath, dirnames, filenames in os.walk(settings.PAGE_DIR):
            parent = self.get_parent(dirpath)
            for fn in filenames:
                if not fn.endswith('.md'):
                    continue
                slug = fn[:-3]
                meta, content = self.read_page(os.path.join(dirpath, fn))
                self.load_page(parent, slug, meta, content)

    def get_parent(self, directory):
        """
        Given a directory name, return the Page representing it in the menu
        heirarchy.
        """
        assert settings.PAGE_DIR.startswith('/')
        assert settings.PAGE_DIR.endswith('/')

        parents = directory[len(settings.PAGE_DIR):]

        page = None
        if parents:
            for slug in parents.split('/'):
                page = Page.objects.get(parent=page, slug=slug)
        return page

    def read_page(self, fn):
        with open(fn) as f:
            if f.readline() != '---\n':
                self.stderr.write('Missing front matter in %s\n' % fn)
                sys.exit(1)
            front_matter = []
            for line in f:
                if line == '---\n':
                    break
                front_matter.append(line)
            meta = yaml.load(''.join(front_matter))
            contents = ''.join(f)
        return meta, contents

    def load_page(self, parent, slug, meta, content):
        if not meta.get('published', True):
            return
        page, created = Page.objects.get_or_create(parent=parent, slug=slug)
        page.name = meta['name']
        page.content = content
        page.include_in_menu = meta.get('include_in_menu', False)
        page.exclude_from_static = meta.get('exclude_from_static', False)
        page.people.clear()
        page.people.add(*(
            get_user_model().objects.get(username=person)
            for person in meta.get('people', ())
        ))
        page.save()
        self.stdout.write('Loaded page %s\n' % '/'.join(page.get_path()))
