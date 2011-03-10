from zope import schema
from plone.directives import form


class IPersonalTagsDemoStorage(form.Schema):
    """
    Persistent Storage for Personal Tags Demo
    """
    data = schema.Dict(title=u'Data')

    

