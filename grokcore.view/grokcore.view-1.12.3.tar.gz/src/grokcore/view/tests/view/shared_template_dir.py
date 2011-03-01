"""
When modules share a template directory, templates that have not been associated with any view class of a given module issue a UserWarning:

  >>> from grokcore.view.testing import warn
  >>> import warnings
  >>> saved_warn = warnings.warn
  >>> warnings.warn = warn

  >>> import shared_template_dir_fixture

  >>> grok.testing.grok(__name__)
  From grok.testing's warn():
  ...UserWarning: Found the following unassociated template(s) when grokking
  'grokcore.view.tests.view.shared_template_dir': food, unassociated.  Define view classes inheriting from
  grok.View to enable the template(s)...

  >>> grok.testing.grok(shared_template_dir_fixture.__name__)
  From grok.testing's warn():
  ...UserWarning: Found the following unassociated template(s) when grokking
  'grokcore.view.tests.view.shared_template_dir_fixture': cavepainting, unassociated.  Define view classes inheriting from
  grok.View to enable the template(s)...

"""
import grokcore.view as grok


grok.templatedir("shared_templates")

class Mammoth(grok.Context):
    pass

class CavePainting(grok.View):
    pass
