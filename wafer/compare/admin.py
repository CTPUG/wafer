# hack'ish support for comparing a django reversion
# hisoty object with the current state

from reversion.admin import VersionAdmin
from django.conf.urls import url
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _


class CompareVersionAdmin(VersionAdmin):

    compare_template = "admin/wafer.compare/compare.html"
    compare_list_template = "admin/wafer.compare/compare_list.html"

    # Add a compare button next to the History button.
    change_form_template = "admin/wafer.compare/change_form.html"

    def get_urls(self):
         urls = super(CompareVersionAdmin, self).get_urls()
         opts = self.model._meta
         compare_urls = [
               url("^([^/]+)/compare/$", self.admin_site.admin_view(self.compare_view),
                   name='%s_%s_compare' % (opts.app_label, opts.model_name)),
               url("^([^/]+)/comparelist/$", self.admin_site.admin_view(self.comparelist_view),
                   name='%s_%s_comparelist' % (opts.app_label, opts.model_name)),
         ]
         return compare_urls + urls

    def compare_view(self, request, object_id, extra_context=None):
        """Actually compare two versions."""
        opts = self.model._meta
        current = get_object_or_404(self.model, pk=object_id)
        context = {
            "title": _("Compare %s") % current.object_repr,
            "app_label": opts.app_label,
            "history_url": reverse("%s:%s_%s_history" % (self.admin_site.name, opts.app_label, opts.model_name),
                                                         args=(quote(obj.pk),)),
        }

        extra_context = extra_context or {}
        context.update(extra_context)
        return render(request, self.compare_template or self._get_template_list("compare.html"),
                      context)

    def comparelist_view(self, request, object_id, extra_context=None):
        """Allow selecting versions to compare."""
        opts = self.model._meta
        context = {
            "title": _("Choose version of %s to compare") % opts.verbose_name,
            "app_label": opts.app_label,
            "opts": opts,
            "module_name": opts.verbose_name,
        }
        each_context = self.admin_site.each_context(request)
        context.update(each_context)

        extra_context = extra_context or {}
        context.update(extra_context)
        return render(request, self.compare_list_template or self._get_template_list("compare_list.html"),
                      context)

