# hack'ish support for comparing a django reversion
# hisoty object with the current state

from reversion.admin import VersionAdmin
from django.conf.urls import url
from django.shortcuts import get_object_or_404, render
from django.contrib.admin.utils import unquote, quote
from django.core.urlresolvers import reverse
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
               url("^([^/]+)/([^/]+)/compare/$", self.admin_site.admin_view(self.compare_view),
                   name='%s_%s_compare' % (opts.app_label, opts.model_name)),
               url("^([^/]+)/comparelist/$", self.admin_site.admin_view(self.comparelist_view),
                   name='%s_%s_comparelist' % (opts.app_label, opts.model_name)),
         ]
         return compare_urls + urls

    def compare_view(self, request, object_id, version_id, extra_context=None):
        """Actually compare two versions."""
        opts = self.model._meta
        object_id = unquote(object_id)
        current = get_object_or_404(self.model, pk=object_id)

        context = {
            "title": _("Comparing curent %s with revision from ") % (opts.verbose_name,'xxx'),
            "app_label": opts.app_label,
            "compare_list_url": reverse("%s:%s_comparelist" % (self.admin_site.name, opts.app_label, opts.model_name),
                                                                  args=(quote(obj.pk),)),
        }

        extra_context = extra_context or {}
        context.update(extra_context)
        return render(request, self.compare_template or self._get_template_list("compare.html"),
                      context)

    def comparelist_view(self, request, object_id, extra_context=None):
        """Allow selecting versions to compare."""
        opts = self.model._meta
        object_id = unquote(object_id)
        current = get_object_or_404(self.model, pk=object_id)
        # As done by reversion's history_view
        action_list = [
            {
                "revision": version.revision,
                "url": reverse("%s:%s_%s_compare" % (self.admin_site.name, opts.app_label, opts.model_name), args=(quote(version.object_id), version.id)),
            } for version
              in self._order_version_queryset(self.revision_manager.get_for_object_reference(
                  self.model,
                  object_id,).select_related("revision__user"))
        ]
        context = {"action_list": action_list,
                   "opts": opts,
                   "object_id": quote(object_id),
                   "original": current,
                  }
        extra_context = extra_context or {}
        context.update(extra_context)
        return render(request, self.compare_list_template or self._get_template_list("compare_list.html"),
                      context)
