"""
`megrok.pagetemplate` uses the default grokcore.view template registry
to handle the registration of the templates.

Let's verify the behavior expected from our component :

  >>> import grokcore.component.testing

We create a pagetemplate with no template defined.
  
  >>> class AnotherTemplate(megrok.pagetemplate.PageTemplate):
  ...     megrok.pagetemplate.view(AnotherView)

  >>> grokcore.component.testing.grok_component('fail', AnotherTemplate)
  Traceback (most recent call last):
  ...
  ConfigurationExecutionError: <class 'martian.error.GrokError'>: Pagetemplate <class 'megrok.pagetemplate.tests.notemplate.AnotherTemplate'> has no associated template or 'render' method.
  ...

During the component registration process, the template registry complains.
The template is not defined. It fails. Everything's fine.

Now, we'll try creating a pagetemplate with an explicit template defined.
Yet, the template doesn't exist : we except another failure.

  >>> class YetAnotherTemplate(megrok.pagetemplate.PageTemplate):
  ...     megrok.pagetemplate.view(AnotherView)
  ...     megrok.pagetemplate.template('doesnt_exist')

  >>> grokcore.component.testing.grok_component('fail', YetAnotherTemplate)
  Traceback (most recent call last):
  ...
  ConfigurationExecutionError: <class 'martian.error.GrokError'>: Pagetemplate <class 'megrok.pagetemplate.tests.notemplate.YetAnotherTemplate'> has no associated template or 'render' method.
  ...

The template registry is not fooled by the template directive. It works.

"""

import grokcore.view
import megrok.pagetemplate

megrok.pagetemplate.templatedir("templates")


class AnotherContext(grokcore.view.Context):
    """A context.
    """


class AnotherView(grokcore.view.View):
    """A very simple view.
    """
    grokcore.view.context(AnotherContext)

    def render(self):
        return u'nothing here to be seen !'
