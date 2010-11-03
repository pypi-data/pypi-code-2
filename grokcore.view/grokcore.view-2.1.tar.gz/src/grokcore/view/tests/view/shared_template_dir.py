"""
When modules share a template directory, templates that have not been
associated with any view class of a given module issue a log message
with level ``logging.WARNING`` to a ``grokcore.view`` logger:

  >>> from zope.testing.loggingsupport import InstalledHandler
  >>> handler = InstalledHandler('grokcore.view')

  >>> import shared_template_dir_fixture

  >>> handler.clear()  # Make sure no old log msgs are stored...
  >>> grok.testing.grok(__name__)
  >>> print handler
  grokcore.view WARNING
      Found the following unassociated template(s) when grokking
      'grokcore.view.tests.view.shared_template_dir': food,
      unassociated.  Define view classes inheriting from grok.View to
      enable the template(s).
  
  >>> handler.clear()  # Make sure no old log msgs are stored...
  >>> grok.testing.grok(shared_template_dir_fixture.__name__)
  >>> print handler
  grokcore.view WARNING
        Found the following unassociated template(s) when grokking
      'grokcore.view.tests.view.shared_template_dir_fixture':
      cavepainting, unassociated.  Define view classes inheriting from
      grok.View to enable the template(s).

  >>> handler.uninstall()

"""
import grokcore.view as grok


grok.templatedir("shared_templates")

class Mammoth(grok.Context):
    pass

class CavePainting(grok.View):
    pass
