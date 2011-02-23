from Acquisition import aq_inner
from OFS.SimpleItem import SimpleItem
from zope.component import adapts
from zope.component.interfaces import ComponentLookupError
from zope.interface import Interface, implements
from zope.formlib import form

from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import ObjectWidget
from zope.app.form.browser import ListSequenceWidget

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 
from plone.contentrules.rule.interfaces import IRuleElementData, IExecutable

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from collective.contentrules.runscript.actions.interfaces import IRunScriptAction, IParamValuePair
from collective.contentrules.runscript import runscriptMessageFactory as _


#-------------------------------------
#New Widget
#-------------------------------------

class ParamValuePair:
    implements(IParamValuePair)
    def __init__(self, name=u'', value=u''):
        self.name = name
        self.value = value


paramvalue_widget = CustomWidgetFactory(ObjectWidget, ParamValuePair)
paramvaluelist_widget = CustomWidgetFactory(ListSequenceWidget,
                                         subwidget=paramvalue_widget)


#-----------------------------------
class ScriptNotFound(Exception):
    def __init__(self, script, obj_url):
        self.script = script
        self.obj_url = obj_url
    
    def __str__(self):
        return 'Could not traverse from "%s" to "%s".' % (self.obj_url, self.script)


class RunScriptAction(SimpleItem):
    """
    The implementation of the action defined in IRunScriptAction
    """
    implements(IRunScriptAction, IRuleElementData)

    script = '' #unicode paths are not allowed
    fail_on_script_not_found = True
    restricted_traverse = False
    parameters = () #how to make this a dictionary?
    
    element = 'plone.actions.RunScript'
    
    @property
    def summary(self):
        return _(u"Run script '${script}' on the object.", mapping=dict(script=self.script))


class RunScriptActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IRunScriptAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):

        obj = self.event.object
        event_title = safe_unicode(obj.Title())
        event_url = obj.absolute_url()
        
        if self.element.restricted_traverse:
            getScript = obj.restrictedTraverse
        else:
            getScript = obj.unrestrictedTraverse
        
        try:
            script = getScript(str(self.element.script))
        except AttributeError:
            if self.element.fail_on_script_not_found:
                raise ScriptNotFound(self.element.script, event_url)
                return False
            else:
                return True
        params = dict([(str(p.name), p.value) for p in self.element.parameters])
        script(**params)
            
        return True

class RunScriptAddForm(AddForm):
    """
    An add form for the RunScript action
    """
    form_fields = form.FormFields(IRunScriptAction)
    form_fields['parameters'].custom_widget = paramvaluelist_widget
    
    label = _(u"Add RunScript Action")
    description = _(u"An action that can run a script on the object")
    form_name = _(u"Configure element")

    def create(self, data):
        a = RunScriptAction()
        form.applyChanges(a, self.form_fields, data)
        return a
    
    #TODO: automatically fill parameter list. 
    # is this really usefull? what if script cant be traversed to at config time?
    # what if script is a view instead?
    #def getScriptParams(self, script_name):
    #    script.ZScriptHTML_tryParams()

class RunScriptEditForm(EditForm):
    """
    An edit form for the RunScript action
    """
    form_fields = form.FormFields(IRunScriptAction)
    form_fields['parameters'].custom_widget = paramvaluelist_widget
    
    label = _(u"Edit RunScript Action")
    description = _(u"An action that can run a script on the object")
    form_name = _(u"Configure element")
