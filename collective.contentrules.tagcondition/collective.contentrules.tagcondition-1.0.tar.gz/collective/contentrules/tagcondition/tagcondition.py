from persistent import Persistent 
from OFS.SimpleItem import SimpleItem

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema
from zope.app.component.hooks import getSite

from zope.component.interfaces import IObjectEvent

from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 

from Acquisition import aq_inner

from collective.contentrules.tagcondition import MessageFactory as _
from collective.contentrules.tagcondition.tagparser import TagParser

class IHTMLTagCondition(Interface):
    """Interface for the configurable aspects of a tag condition.
    
    This is also used to create add and edit forms, below.
    """
    
    tags = schema.Tuple(title=_(u"Tags"),
                              description=_(u"The HTML tags to check for. Tags filtered by the HTML Filtering control panel will not apply in this list."),
                              required=True,
                              value_type=schema.TextLine(title=_(u"Tag")))
         
class HTMLTagCondition(SimpleItem):
    """The actual persistent implementation of the tag condition element.
    
    Note that we must mix in SimpleItem to keep Zope 2 security happy.
    """
    implements(IHTMLTagCondition, IRuleElementData)
    
    tags = []
    element = "collective.contentrules.tagcondition.Tag"
    
    @property
    def summary(self):
        return _(u"Object has one of the following HTML tags in its Text: ${names}", mapping=dict(names=", ".join(self.tags)))

class HTMLTagConditionExecutor(object):
    """The executor for this condition.
    
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
    adapts(Interface, IHTMLTagCondition, IObjectEvent)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        context = aq_inner(self.event.object)
        
        parser = TagParser()
        try:
            parser.feed(context.getText())
        except (AttributeError, TypeError,):
            #This object doesn't have a getText method
            return False
        tags = frozenset(parser.getTags())
        return len(tags.intersection(self.element.tags)) > 0
        
class HTMLTagAddForm(AddForm):
    """An add form for portal type conditions.
    """
    form_fields = form.FormFields(IHTMLTagCondition)
    label = _(u"Add HTML Tag Condition")
    description = _(u"A tag condition makes the rule apply only to content with certain HTML tags.")
    form_name = _(u"Configure element")
    
    def create(self, data):
        c = HTMLTagCondition()
        form.applyChanges(c, self.form_fields, data)
        return c

class HTMLTagEditForm(EditForm):
    """An edit form for portal type conditions
    """
    form_fields = form.FormFields(IHTMLTagCondition)
    label = _(u"Edit HTML Tag Condition")
    description = _(u"A tag condition makes the rule apply only to content with certain HTML tags.")
    form_name = _(u"Configure element")
