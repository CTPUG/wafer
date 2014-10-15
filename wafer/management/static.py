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
            # This is a hack because dajngo_medusa doens't understand 301
            if path == '/':
                DEPLOY_DIR = settings.MEDUSA_DEPLOY_DIR
                # Also copy to index, as specified by the pages url
                outpath = os.path.join(DEPLOY_DIR, 'index')
                inpath = os.path.join(DEPLOY_DIR, 'index.html')
                shutil.copyfile(inpath, outpath)
