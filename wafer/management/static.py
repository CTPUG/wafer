import shutil
import os

from django_medusa.renderers import DiskStaticSiteRenderer
from django.conf import settings


class WaferDiskStaticSiteRenderer(DiskStaticSiteRenderer):

    # People may create pages that mirror directories - if this happens,
    # we skip the page, rather than aborting and print a message, since
    # this may require manual fixup later
    def render_path(self, path=None, view=None):
        if not path:
            super(WaferDiskStaticSiteRenderer, self).render_path(path, view)
        else:
            try:
                super(WaferDiskStaticSiteRenderer, self).render_path(path,
                                                                     view)
            except IOError as err:
                print('Skiping %s - threw IOError %s' % (path, err))

    # Copy static assets into place.
    @classmethod
    def finalize_output(self):
        DiskStaticSiteRenderer.finalize_output()

        static_path = os.path.join(settings.MEDUSA_DEPLOY_DIR,
                                   settings.STATIC_URL.lstrip('/'))
        media_path = os.path.join(settings.MEDUSA_DEPLOY_DIR,
                                  settings.MEDIA_URL.lstrip('/'))

        shutil.rmtree(static_path, ignore_errors=True)
        shutil.rmtree(media_path, ignore_errors=True)

        shutil.copytree(settings.STATIC_ROOT, static_path)
        shutil.copytree(settings.MEDIA_ROOT, media_path)
