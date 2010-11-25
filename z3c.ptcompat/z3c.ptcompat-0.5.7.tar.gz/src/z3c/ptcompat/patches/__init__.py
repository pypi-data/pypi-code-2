"""Loading this module will monkey-patch ZPT template classes such
that they render using Chameleon.

Since many templates are instantiated at module-import, we patch using
a duck-typing strategy.

We replace the ``__get__``-method of the ViewPageTemplateFile
class. This allows us to return a Chameleon template instance,
transparent to the calling class.
"""

from zope.app.pagetemplate.viewpagetemplatefile import BoundPageTemplate
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile as \
     ZopeViewPageTemplateFile

from z3c.pt.pagetemplate import ViewPageTemplateFile

_marker = object()

def get_bound_template(self, instance, type):
    if instance is None:
        return self
        
    template = getattr(self, '_template', _marker)
    if template is _marker:
        self._template = template = ViewPageTemplateFile(self.filename)

    return template.bind(instance)

ZopeViewPageTemplateFile.__get__ = get_bound_template
