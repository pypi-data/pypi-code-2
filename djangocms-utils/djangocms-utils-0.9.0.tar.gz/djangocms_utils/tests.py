import unittest
from django.test.testcases import TestCase
from django.core.handlers.wsgi import WSGIRequest
from django.conf import settings
from django.template import Template, Context
from cms.plugins.text.models import Text
from testapp.models import MultiplePlaceholdersExample, PlaceholderAsExample
from djangocms_utils.admin import get_or_create_placeholders
from djangocms_utils.templatetags.djangocms_utils_tags import choose_placeholder

class MultiplePlaceholdersTestCase(unittest.TestCase):
    
    def setUp(self):
        
        self.obj = MultiplePlaceholdersExample(heading='Example heading')
        self.obj.save()
        
        for placeholder, slot in get_or_create_placeholders(self.obj, MultiplePlaceholdersExample):
            for i in range(3):
                plugin = Text(plugin_type='TextPlugin',
                    placeholder=placeholder,
                    position=i,
                    body='Page %s' %(i),
                    language=settings.LANGUAGE_CODE
                )
                plugin.insert_at(None, position='last-child', commit=True)
                        
class TestAttachedField(MultiplePlaceholdersTestCase):
    
    def testAttachedField(self):
        # make sure manytomany fields are found as the field Placeholder is related via
        ph = self.obj.placeholders.all()[0]
        self.assertEqual('placeholders', ph._get_attached_field().name)
                
class ChoosePlaceholderTestCase(MultiplePlaceholdersTestCase):
    
    def testChoosePlaceholder(self):
        ph = self.obj.placeholders.get(slot='first')
        self.assertEqual(choose_placeholder(self.obj.placeholders, 'first'), ph)

class RenderPlaceholderAsTestCase(TestCase):
    
    def get_request(self, path=None):
        
        if not path:
            path = '/'

        environ = {
            'HTTP_COOKIE': self.client.cookies,
            'PATH_INFO': path,
            'QUERY_STRING': '',
            'REMOTE_ADDR': '127.0.0.1',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': '80',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1,0),
            'wsgi.url_scheme': 'http',
            'wsgi.errors': self.client.errors,
            'wsgi.multiprocess': True,
            'wsgi.multithread': False,
            'wsgi.run_once': False,
        }
        request = WSGIRequest(environ)
        request.session = self.client.session
        request.LANGUAGE_CODE = settings.LANGUAGE_CODE
        return request
        
    def setUp(self):
        
        self.obj = PlaceholderAsExample(heading='Example heading')
        self.obj.save()
        
        placeholder = self.obj.placeholder
        
        for i in range(3):
            plugin = Text(plugin_type='TextPlugin',
                placeholder=placeholder,
                position=i,
                body='Page %s' %(i),
                language=settings.LANGUAGE_CODE
            )
            plugin.insert_at(None, position='last-child', commit=True)
                        
    def testRenderAs(self):
        t = Template('{% load djangocms_utils_tags %}{% render_placeholder_as obj.placeholder as testcontent %}{{ testcontent }}')
        c = Context({"obj": self.obj, "request": self.get_request()})
        out = t.render(c)
        self.assertEqual(out, u'Page 0\nPage 1\nPage 2\n')



