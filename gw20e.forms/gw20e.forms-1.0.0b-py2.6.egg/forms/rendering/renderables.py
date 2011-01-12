from gw20e.forms.interfaces import IRenderable
from zope.interface import implements


class Renderable(object):

    """ Base class for controls """

    implements(IRenderable)

    def __init__(self, id, **props):

        self.id = id
        self.type = self.__class__.__name__.lower()


class Text(Renderable):

    def __init__(self, id, text, **props):

        Renderable.__init__(self, id, **props)
        self.text = text
    

class Submit(Renderable):

    implements(IRenderable)


    def __init__(self, id, label, **props):

        Renderable.__init__(self, id, **props)
        self.label = label
