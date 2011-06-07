from django.test import TestCase
from django.template.loader import render_to_string


class SmokeTest(TestCase):
    def test_django_works(self):
        """
        Django templates work.
        """
        self.assertEqual(render_to_string("uta/template.html"), "foo")

    def test_jinja2_works(self):
        self.assertEqual(
            render_to_string("uta/template.jinja2.html", {'kenny': None}), 
        u'\n    Kenny looks okay --- so far\n')
    
    def test_mako_works(self):
        self.assertEqual(
            render_to_string("uta/template.mako.html", {'kenny': None}), 
        u'\n<table>\n        \n    <tr>\n        <td>0</td>    </tr>\n\n</table>\n   \n')

    def test_haml_works(self):
        self.assertEqual(
            render_to_string("uta/template.hamlpy", {'kenny': None}), 
        '<div></div>\np\nr\no\nf\ni\nl\ne\n<div></div>\nl\ne\nf\nt\n<div></div>\nc\no\nl\nu\nm\nn\n<div></div>\nd\na\nt\ne\n2\n0\n1\n0\n<!--  -->\n0\n2\n<!--  -->\n1\n8\n<div></div>\na\nd\nd\nr\ne\ns\ns\nT\no\nr\no\nn\nt\no\n,\nO\nN\n<div></div>\nr\ni\ng\nh\nt\n<div></div>\nc\no\nl\nu\nm\nn\n<div></div>\nb\ni\no\nJ\ne\ns\ns\ne\nM\ni\nl\nl\ne\nr\n')
