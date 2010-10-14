from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import connection
from django.template import TemplateDoesNotExist
from django.test import TestCase
from django.test.client import Client

from loader import CachedTemplateLoader
from models import Group, Template


class TemplateTest(TestCase):

    urls = "magneto.urls"

    def test_default_site(self):
        group = Group.objects.create(name="Home")
        template = Template.objects.create(
            group=group,
            name="about/staff",
        )
        self.assertEqual(template.site,
            Site.objects.get(domain="example.com"))

    def test_absolute_url(self):
        group = Group.objects.create(name="Home")
        template = Template.objects.create(
            group=group,
            name="about/staff",
        )
        self.assertEqual(template.get_absolute_url(), "/about/staff")

    def test_absolute_url_index(self):
        group = Group.objects.create(name="Home")
        template = Template.objects.create(
            group=group,
            name="index",
        )
        self.assertEqual(template.get_absolute_url(), "/")

    def test_strip(self):
        group = Group.objects.create(name="Home")
        template = Template.objects.create(
            group=group,
            name=" /about/staff/   ",
        )
        self.assertEqual(template.name, "about/staff")


class CachedTemplateLoaderTest(TestCase):

    def test_loader(self):
        group = Group.objects.create(name="Home")
        template = Template.objects.create(
            group=group,
            name="about/staff",
            content="Hello World",
        )

        self.assertEqual(
            CachedTemplateLoader().load_template_source("about/staff"),
            (u"Hello World", "about/staff"))
        self.assertEqual(template.site,
            Site.objects.get(domain="example.com"))

        self.assertEqual(cache.get("01c061d1a685bf3dbbed752c339bb579"), "Hello World")

    def test_loader_with_index_value(self):
        group = Group.objects.create(name="Home")
        template = Template.objects.create(
            group=group,
            name="index",
            content="Hello World",
        )

        self.assertEqual(CachedTemplateLoader().load_template_source(""),
            (u"Hello World", "index"))

    def test_loader_restricted_to_current_site(self):
        cache.clear()
        s1 = Site.objects.create(domain="site1.com", name="site1")
        group = Group.objects.create(name="Home")
        template = Template.objects.create(
            group=group,
            name="about/staff",
            content="Hello World",
            site=s1,
        )

        self.assertRaises(TemplateDoesNotExist,
            CachedTemplateLoader().load_template_source, "about/staff")

    def test_loader_caches_misses(self):
        group = Group.objects.create(name="Admin")
        template = Template.objects.create(
            group=group,
            name="about/admin",
            content='{% extends "admin/change_form.html" %}',
        )

        self.assertRaises(TemplateDoesNotExist,
            CachedTemplateLoader().load_template_source,
            "admin/change_form.html")
        self.assertEqual(cache.get("8eb1e907540975a50e9624b8766e58ea"), "miss")


class DetailViewTest(TestCase):

    urls = "magneto.urls"

    def test_detail(self):
        client = Client()

        group = Group.objects.create(name="Home")
        template = Template.objects.create(
            group=group,
            name="about/staff",
            content="Hello World",
            visible=True,
        )
        response = client.get(reverse("magneto.detail",
            args=["about/staff"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._headers["content-type"][1], "text/html")

    def test_detail_index(self):
        client = Client()

        group = Group.objects.create(name="Home")
        template = Template.objects.create(
            group=group,
            name="index",
            content="Hello World",
            visible=True,
        )
        response = client.get(reverse("magneto.detail.index"))
        self.assertEqual(response.status_code, 200)

    def test_detail_404_if_not_visible(self):
        client = Client()

        group = Group.objects.create(name="Home")
        template = Template.objects.create(
            group=group,
            name="about/staff",
            content="Hello World",
            visible=False,
        )
        response = client.get(reverse("magneto.detail",
            args=["about/staff"]))
        self.assertEqual(response.status_code, 404)

    def test_detail_content_type(self):
        client = Client()

        group = Group.objects.create(name="Home")
        template = Template.objects.create(
            group=group,
            name="css/main.css",
            content="body { color: #ccc }",
            content_type="text/css",
            visible=True,
        )
        response = client.get(reverse("magneto.detail",
            args=["css/main.css"]))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response._headers["content-type"][1], "text/css")

        # Make sure content type is sent as a string and not unicode
        # Unicode values seem to confuse either Apache or nginx
        self.assertEqual(type(response._headers["content-type"][1]),
            type(""))
