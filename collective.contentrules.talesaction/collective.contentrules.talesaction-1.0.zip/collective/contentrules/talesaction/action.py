from zope.component import adapts
from zope.event import notify
from zope.formlib import form
from zope.interface import implements, Interface
from zope.lifecycleevent import ObjectCopiedEvent
from zope import schema

from Acquisition import aq_base
import OFS.subscribers
from OFS.event import ObjectClonedEvent
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression, createExprContext
from Products.CMFPlone import utils
from Products.statusmessages.interfaces import IStatusMessage

from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.contentrules import PloneMessageFactory as PMF
from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.app.vocabularies.catalog import SearchableTextSourceBinder

from collective.contentrules.talesaction import MessageFactory as _

class ITalesExpressionAction(Interface):
    """Interface for the configurable aspects of a move action.

    This is also used to create add and edit forms, below.
    """

    tales_expression = schema.TextLine(title=_(u"TALES expression"),
                              description=_(u"The TALES Expression to execute."),
                              required=True,
                              )

class TalesExpressionAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """
    implements(ITalesExpressionAction, IRuleElementData)

    tales_expression = ''
    element = 'plone.actions.TalesExpression'

    @property
    def summary(self):
        return PMF(u"TALES expression is: ${tales_expression}",
                 mapping=dict(tales_expression=self.tales_expression))


class TalesExpressionActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, ITalesExpressionAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        object = self.event.object
        folder = self.context
        portal = getToolByName(folder, 'portal_url').getPortalObject()
        expression = self.element.tales_expression
        ec = createExprContext(folder, portal, object)
        Expression(expression)(ec)


class TalesExpressionAddForm(AddForm):
    """An add form for tales expression action.
    """
    form_fields = form.FormFields(ITalesExpressionAction)
    label = _(u"Add TALES Expression Action")
    description = _(u"Executes a TALES Expression when the rule applies.")
    form_name = PMF(u"Configure element")

    def create(self, data):
        a = TalesExpressionAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class TalesExpressionEditForm(EditForm):
    """An edit form for TALES expression actions.
    """
    form_fields = form.FormFields(ITalesExpressionAction)
    label = _(u"Edit TALES Expression Action")
    description = _(u"Executes a TALES Expression when the rule applies.")
    form_name = PMF(u"Configure element")
