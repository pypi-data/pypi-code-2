"""
`megrok.pagetemplate` allows you to register IPageTemplate components as
multiadapter. It adapts a view and a request. As any adapting component,
it can be registered using a name. This name allows you to register several
templates for a given view, without conflict.

   >>> import grokcore.component.testing


Let's create a page template component, as we did previously. The only change
here will be to add the 'name' directive.

   >>> from zope.pagetemplate.interfaces import IPageTemplate
   
   >>> class Template(megrok.pagetemplate.PageTemplate):
   ...     megrok.pagetemplate.view(View)
   ...     megrok.pagetemplate.name('first')
   ...     megrok.pagetemplate.template('test')

   >>> grokcore.component.testing.grok_component('one', Template)
   True


As it's registered, we can not query it::

   >>> from zope.publisher.browser import TestRequest
   >>> from zope.component import queryMultiAdapter
   
   >>> request = TestRequest()
   >>> view = View(Context(), request)
   >>> pt = queryMultiAdapter((view, request), IPageTemplate, name='first')
   >>> print pt
   <megrok.pagetemplate.components.ViewPageTemplate object at ...>


Querying it without a name lead to an error, if no template is registered
for u''::

   >>> print queryMultiAdapter((view, request), IPageTemplate)
   None


Now, we can register a second template, for the same view/request couple::

   >>> class AnotherTemplate(megrok.pagetemplate.PageTemplate):
   ...     megrok.pagetemplate.view(View)
   ...     megrok.pagetemplate.name('second')
   ...     megrok.pagetemplate.template('test')

   >>> grokcore.component.testing.grok_component('two', AnotherTemplate)
   True


We verify we can query both::

   >>> pt1 = queryMultiAdapter((view, request), IPageTemplate, name='first')
   >>> print pt1
   <megrok.pagetemplate.components.ViewPageTemplate object at ...>

   >>> pt2 = queryMultiAdapter((view, request), IPageTemplate, name='second')
   >>> print pt2
   <megrok.pagetemplate.components.ViewPageTemplate object at ...>


We try out convenient function::

   >>> same = megrok.pagetemplate.getPageTemplate(view, request, name='first')
   >>> print same.template
   <test template in ...tests/templates/test.pt>

"""

import grokcore.view
import megrok.pagetemplate

megrok.pagetemplate.templatedir("templates")


class Context(grokcore.view.Context):
    """A context.
    """


class View(grokcore.view.View):
    """A very simple view.
    """
    grokcore.view.context(Context)

    def render(self):
        return u"Nothing here"
