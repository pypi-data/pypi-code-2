from zope.interface import implements
from gw20e.forms.interfaces import IControlGroup
from gw20e.forms.formview import RenderableContainer
from renderables import Renderable


class Group(RenderableContainer, Renderable):

    def __init__(self, id, label="", **props):

        RenderableContainer.__init__(self)
        Renderable.__init__(self, id, **props)

        self.label = label


class FlowGroup(Group):

    """ Implement a grouping component that makes it's content flow,
    either horizontally or vertically. Possible orientations:
    h (horizontal), v (vertical).
    """

    implements(IControlGroup)

    def __init__(self, id, label="", orientation="v", **props):


        Group.__init__(self, id, label=label, **props)

        self.orientation = orientation


class GridGroup(RenderableContainer, Renderable):

    """ Implement a grouping component that lays out it's component
    in a strict grid.
    """

    implements(IControlGroup)

    def __init__(self, id, label="", cols=3, **props):

        Group.__init__(self, id, label=label, **props)

        self.cols = cols


class CardGroup(RenderableContainer, Renderable):

    """ Implement a grouping component that makes it's contents
    available as 'cards', where only one is visible at one given time.
    """

    implements(IControlGroup)

    def __init__(self, id, label="", **props):

        Group.__init__(self, id, label=label, **props)

class StepGroup(RenderableContainer, Renderable):

    implements(IControlGroup)

    def __init__(self, id, label="", **props):

        Group.__init__(self, id, label=label, **props)
