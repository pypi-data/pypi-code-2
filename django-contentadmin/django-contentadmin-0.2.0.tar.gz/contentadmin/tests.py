"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.template import Template, Context, TemplateSyntaxError
from models import TextContent, ImageContent, Page

class ContentAdminCase(TestCase):
    def assert_renders(self, tmpl, context, value):
        tmpl = Template(tmpl)
        self.assertEqual(tmpl.render(context), value)


    def test_blocktext(self):
        self.assert_renders(
            """{% load contentadmin_tags %}{% blocktext about test1 %}First test{% endblocktext %}""",
            Context(),
            "First test"
        )
        page = Page.objects.get(name="about")
        text1 = TextContent.objects.get(page=page, name="test1")
        text1.text = "New text"
        text1.save()
        self.assert_renders(
            """{% load contentadmin_tags %}{% blocktext about test1 %}First test{% endblocktext %}""",
            Context(),
            "New text"
        )
        


