from mock import patch
from django.contrib.sites.models import Site
from wafer.pages.models import Page


def test_default_site():
    page = Page.objects.create(name="index", slug="index", content="hello")
    assert page.site_id == 1


@patch("django.contrib.sites.models.Site.objects.get_current")
def test_non_default_site(get_current):
    site = Site.objects.create(name="second site", domain="two.example.com")
    get_current.return_value = site
    page = Page.objects.create(name="index", slug="index", content="hello")
    assert page.site_id == site.id

