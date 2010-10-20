from zope.interface import implements

from Products.Archetypes import atapi
from archetypes.schemaextender.field import ExtensionField

from raptus.article.table.interfaces import IType

class StringField(ExtensionField, atapi.StringField):
    """ String Extension Field
    """

class TextField(ExtensionField, atapi.TextField):
    """ Text Extension Field
    """

class TextType(object):
    """ The text type renders plain text
    """
    implements(IType)
    def structure(self):
        return False
    def modifier(self, value):
        return value
    def field(self, name, label):
        return StringField(name,
                   required=False,
                   searchable=True,
                   storage = atapi.AnnotationStorage(),
                   widget = atapi.StringWidget(
                       description = '',
                       label=label
                   ),
               )
    def widget(self, name):
        return '<input type="text" name="%s" value="" />' % name

class LinkType(object):
    """ The link type renders a link
    """
    implements(IType)
    def structure(self):
        return True
    def modifier(self, value):
        if not value:
            return value
        return '<a href="%(url)s">%(url)s</a>' % dict(url=value)
    def field(self, name, label):
        return StringField(name,
                   required=False,
                   searchable=True,
                   storage = atapi.AnnotationStorage(),
                   default = "http://",
                   widget = atapi.StringWidget(
                       description = '',
                       label=label
                   ),
               )
    def widget(self, name):
        return '<input type="text" name="%s" value="http://" />' % name

class HTMLType(object):
    """ The html type renders html
    """
    implements(IType)
    def structure(self):
        return True
    def modifier(self, value):
        return value
    def field(self, name, label):
        return TextField(name,
                   required=False,
                   searchable=True,
                   storage = atapi.AnnotationStorage(),
                   validators = ('isTidyHtmlWithCleanup',),
                   default_output_type = 'text/x-html-safe',
                   widget = atapi.RichWidget(
                       description = '',
                       label = label,
                       rows = 25
                   ),
               )
    def widget(self, name):
        return '<textarea name="%s"></textarea>' % name
