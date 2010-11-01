"""
Warnings are sent on ``logging.WARNING`` level to a logger named
``grokcore.view``. By default this messages will not be displayed, as
the logger level is set to ``logging.ERROR`` immediately before the
first warning happens (so apps have time to prepare the logger if they
want to do so).

The logger is initialized immediately before the first warning
happens:

  >>> import logging
  >>> logger = logging.getLogger('grokcore.view')
  >>> logger.level == logging.NOTSET
  True

  >>> grok.testing.grok(__name__)
  >>> logger.level == logging.ERROR
  True
  
If we set our own logging handler or tweak the logger level, this
won't be overridden when the next warning happens:

  >>> logger.level = logging.CRITICAL
  >>> grok.testing.grok(__name__)
  >>> logger.level == logging.CRITICAL
  True

The logger really gets messages:

  >>> from zope.testing.loggingsupport import InstalledHandler
  >>> handler = InstalledHandler('grokcore.view')
  >>> handler.clear() # Make sure there are no old msgs stored...

  >>> grok.testing.grok(__name__)
  >>> print handler
  grokcore.view WARNING
      Found the following unassociated template(s) when grokking
      'grokcore.view.tests.view.warning_msgs': club.  Define view
      classes inheriting from grok.View to enable the template(s).

Restore logging machinery:

  >>> handler.uninstall()
  >>> logger.level = logging.ERROR

"""
import grokcore.view as grok

class Mammoth(grok.Context):
    pass

club = grok.PageTemplate("""\
<html><body><h1>GROK CLUB MAMMOTH!</h1></body></html>
""")
