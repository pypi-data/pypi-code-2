# external imports
from grokcore.view import view, name, template, templatedir, layer
from zope.pagetemplate.interfaces import IPageTemplate

# exposed `megrok.pagetemplate` API
from megrok.pagetemplate.utils import getPageTemplate
from megrok.pagetemplate.components import PageTemplate
