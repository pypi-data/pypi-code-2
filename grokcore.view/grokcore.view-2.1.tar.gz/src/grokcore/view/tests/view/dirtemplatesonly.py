"""
A template directory may only contain recognized template files::

  >>> from zope.testing.loggingsupport import InstalledHandler
  >>> handler = InstalledHandler('grokcore.view')
  >>> handler.clear()

  >>> grok.testing.grok(__name__)
  >>> print handler
  grokcore.view WARNING
      File 'invalid.txt' has an unrecognized extension in directory
      '...dirtemplatesonly_templates'

Files ending with '.cache' are generated on the fly by some template
engines. Although they provide no valid template filename extension,
they are ignored.

There is a 'template' ``ignored.cache`` in our template dir, which
emits no warning::

  >>> #'ignored.cache' in lastwarning
  >>> 'ignored.cache' in handler.records[0].msg
  False

The same applies to files and directories ending with '~' or starting
with a dot ('.').

Restore the logging machinery::

  >>> handler.uninstall()

"""
import grokcore.view as grok

class Mammoth(grok.Context):
    pass

class Index(grok.View):
    pass
