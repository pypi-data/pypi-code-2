"""
Templates that are not associated with a view class will provoke an
error:

  >>> from zope.testing.loggingsupport import InstalledHandler
  >>> handler = InstalledHandler('grokcore.view')

  >>> grok.testing.grok(__name__)
  >>> print handler
  grokcore.view WARNING
      Found the following unassociated template(s) when grokking
      'grokcore.view.tests.view.unassociated': index.  Define view
      classes inheriting from grok.View to enable the template(s).

Also templates of modules named equally as the package name the module
resides in, should be found without error or warning. We check this
with the local package `modequalspkgname`::

  >>> handler.clear() # Make sure no old log msgs are stored...

  >>> pkg = __name__.rsplit('.', 1)[0] + '.modequalspkgname'
  >>> grok.testing.grok(pkg) is None
  True

No log messages were emitted:

  >>> handler.records
  []

  >>> handler.uninstall()

"""
import grokcore.view as grok

class Mammoth(grok.Context):
    pass
