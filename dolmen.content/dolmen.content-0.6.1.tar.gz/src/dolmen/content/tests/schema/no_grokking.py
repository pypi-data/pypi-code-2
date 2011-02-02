"""
To Grok or not to grok
======================

The use of the `schema` directive works without any grokking.
A simple example :

  >>> from dolmen.content import schema
  >>> from zope.interface import Interface
  >>> from zope.schema import TextLine, Int

  >>> class IMySchema(Interface):
  ...   mystr = TextLine(title=u"A string", default=u"Boo")
  ...   number = Int(title=u"A simple number", default=1)

  >>> class Content(object):
  ...   schema(IMySchema)
  
  >>> IMySchema.implementedBy(Content)
  True

  >>> obj = Content()
  >>> obj.mystr
  u'Boo'
  >>> obj.number
  1
  
"""
