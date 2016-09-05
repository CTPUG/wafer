from django_medusa.renderers import DiskStaticSiteRenderer


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
