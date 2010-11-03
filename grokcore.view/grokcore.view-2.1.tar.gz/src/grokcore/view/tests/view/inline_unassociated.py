"""
Inline templates that are not associated with a view class will
provoke a log message on warning level to ``grokcore.view`` logger:

  >>> from zope.testing.loggingsupport import InstalledHandler
  >>> handler = InstalledHandler('grokcore.view')
  >>> handler.clear() # Make sure there are no old msgs stored...

  >>> grok.testing.grok(__name__)
  >>> print handler
  grokcore.view WARNING
      Found the following unassociated template(s) when grokking
      'grokcore.view.tests.view.inline_unassociated': club.  Define
      view classes inheriting from grok.View to enable the
      template(s).

Restore logging machinery:

  >>> handler.uninstall()

"""
import grokcore.view as grok

class Mammoth(grok.Context):
    pass

club = grok.PageTemplate("""\
<html><body><h1>GROK CLUB MAMMOTH!</h1></body></html>
""")
