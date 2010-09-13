# encoding: utf-8

"""
Tests for the last.fm app.

"""


from django.test import TestCase
import mock

from lastfm.templatetags import lastfm_widget


class TemplateTagsTestCase(TestCase):
    """Test the template tag for the last.fm widget."""
    
    def setUp(self):
        self.parser = mock.Mock(spec=['compile_filter'])
        self.token = mock.Mock(spec=['split_contents'])
        
    def test_get_sidebar_widgets(self):
        """
        Test if ``lastfm_widget.get_lastfm_widget()`` returns a node with the
        correct variable name.
        
        """
        tag = 'get_lastfm_widget'
        var_name = 'widgets'
        self.token.split_contents.return_value = (tag, 'as', var_name)
        
        node = lastfm_widget.get_lastfm_widget(self.parser, self.token)
        self.assertEqual(node.var_name, var_name)
        
    @mock.patch('django.template.loader.get_template')
    @mock.patch('django.template.Context')
    def test_lastfm_widget_node(self, get_template, Context):
        """
        Test if the template node contains the correct template variables.
        
        """
        class ContextMock(dict):
            autoescape = object()
        context = ContextMock()
        template = get_template.return_value
    
        var_name = 'widgets'
        node = lastfm_widget.LastfmWidgetNode(var_name)
        node.render(context)     
        
        self.assertTrue(var_name in context)
        widget = context[var_name]
        self.assertTrue('title' in widget)
        self.assertTrue('content' in widget)
