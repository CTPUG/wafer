from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView, TemplateView, UpdateView

from bakery.views import BuildableDetailView
from reversion import revisions
from reversion.models import Version
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from wafer.compare.admin import make_diff, get_author, get_date

from wafer.pages.models import Page
from wafer.pages.serializers import PageSerializer
from wafer.pages.forms import PageForm


class ShowPage(BuildableDetailView):
    template_name = 'wafer.pages/page.html'
    model = Page

    # Needed so django-bakery honours the exclude_from_static flag
    def build_object(self, obj):
        """Override django-bakery to skip pages marked exclude_from_static"""
        if not obj.exclude_from_static:
            super(ShowPage, self).build_object(obj)
        # else we just ignore this page entirely
        # This does create a directory, but that's usually what we want
        # for container pages, so we leave it.

class EditPage(UpdateView):
    template_name = 'wafer.pages/page_form.html'
    model = Page
    form_class = PageForm

    @revisions.create_revision()
    def form_valid(self, form):
        revisions.set_user(self.request.user)
        revisions.set_comment("Page Modified")
        return super(EditPage, self).form_valid(form)


class ComparePage(DetailView):
    template_name = 'wafer.pages/page_compare.html'
    model = Page

    def get_context_data(self, **kwargs):
        context = super(ComparePage, self).get_context_data(**kwargs)

        versions = Version.objects.get_for_object(self.object)
        # By revisions api definition, this is the most recent version
        current = versions[0]
        context['cur_author'] = get_author(versions[0])
        context['cur_date'] = get_date(versions[0])
        context['prev_author'] = None
        context['prev_date'] = None
        context['prev'] = None
        context['next'] = None
        context['diff_list'] = None

        if len(versions) == 1:
            # only 1 version, so short circuit everything
            return context
        requested_version = int(self.request.GET.get('version', 1))
        if requested_version > len(versions):
            # Incorrect data, so fail to sane state
            return context
        if requested_version == 1:
            # No next revision in this case
            context['next'] = None
        else:
            context['next'] = requested_version - 1
        if requested_version >= len(versions) - 1:
            # No previous revision
            context['prev'] = None
        else:
            context['prev'] = requested_version + 1

        previous = versions[requested_version]
        context['prev_author'] = get_author(previous)
        context['prev_date'] = get_date(previous)

        context['diff_list'] = make_diff(current, previous)

        return context


def slug(request, url):
    """Look up a page by url (which is a tree of slugs)"""
    page = None

    if url:
        for slug in url.split('/'):
            if not slug:
                continue
            try:
                page = Page.objects.get(slug=slug, parent=page)
            except Page.DoesNotExist:
                raise Http404
    else:
        try:
            page = Page.objects.get(slug='index', parent=None)
        except Page.DoesNotExist:
            return TemplateView.as_view(
                template_name='wafer/index.html')(request)

    if 'edit' in request.GET:
        if not request.user.has_perm('pages.change_page'):
            raise PermissionDenied
        return EditPage.as_view()(request, pk=page.id)

    if 'compare' in request.GET:
        if not request.user.has_perm('pages.change_page'):
            raise PermissionDenied
        return ComparePage.as_view()(request, pk=page.id)

    return ShowPage.as_view()(request, pk=page.id)


class PageViewSet(viewsets.ModelViewSet):
    """API endpoint for users."""
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )
