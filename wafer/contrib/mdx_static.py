import re

from django.contrib.staticfiles.templatetags.staticfiles import static

from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor

assetRE = re.compile(r'{% static [\'"](.*?)[\'"] %}')


class DjangoStaticAssetsProcessor(Postprocessor):
    def replacement(self, match):
        path = match.group(1)
        url = static(path)
        return url

    def run(self, text):
        return assetRE.sub(self.replacement, text)


class StaticExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.postprocessors.add('django_static_assets',
                              DjangoStaticAssetsProcessor(md), '_end')


def makeExtension(**kwargs):
    return StaticExtension(**kwargs)
