from Acquisition import aq_inner
from OFS.SimpleItem import SimpleItem
from plone.app.contentrules.browser.formhelper import NullAddForm
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from slc.outdated import Outdated
from zope.component import adapts
from zope.component.interfaces import IObjectEvent
from zope.interface import implements, Interface

from LinguaPlus import MessageFactory as _

class Outdater(object):
    """Wrapper to expose the outdated property referencing a context.
    """
    outdated = Outdated()
    def __init__(self, context):
        self.context = context

class IOutdateAction(Interface):
    """Describe the 0 configuration parameters for outdating.
    """

class OutdateAction(SimpleItem):
    """Persistent (nothing to save though)
    """
    implements(IOutdateAction, IRuleElementData)

    element = 'LinguaPlus.Outdate'

    @property
    def summary(self):
        return _(u"Mark translations as outdated.")

class OutdateActionExecutor(object):
    """Outdate all translations of canonical content. No effect if the
    content is not canonical.
    """
    implements(IExecutable)
    adapts(Interface, IOutdateAction, IObjectEvent)

    def __init__(self, context, element, event):
        """
        context: Object on which the rule is defined e.g. the site root
        element: OutdateAction (contains any configuration for the action)
        event: IObjectEvent that triggered the action
        """
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object

        if not obj.isCanonical():
            return True
        
        translations = obj.getTranslations()
        for lang in translations:
            document, state = translations[lang]
            # don't outdate self:
            if document == obj:
                # reindex self.event.object?
                continue
            outdater = Outdater(aq_inner(document))
            outdater.outdated = True
            # extra reindexObject() per http://plone.org/documentation/manual/
            #   plone-community-developer-documentation/content/manipulating:
            outdater.context.reindexObject()
            outdater.context.reindexObject(idxs=["outdated"])

        return True

class OutdateAddForm(NullAddForm):
    """Degenerate add form for 'outdate translations' action.
    """
    def create(self):
        return OutdateAction()

