from Products.Collage.browser.collage import CollageView
from Products.Collage.browser.views import BaseView
from collective.collage.nested import message_factory as _

class NestedCollageView(BaseView, CollageView):
    """ A nested collage view """

class NestedContentView(NestedCollageView):
    """ View to display just content (collage rows and columns)
    """
    title = _(u"Content")

class NestedFullView(NestedCollageView):
    """ View to display title, description and content
    """
    title = _(u"Full")

