import logging
import transaction
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('Products.PyConBrasil: setuphandlers')

def isNotOurProfile(context):
    return context.readDataFile("pyconbrasil.txt") is None

def addToListProperty(context, out, propertySheet, property, value):
    """Add the given value to the list in the given property"""
    current = list(propertySheet.getProperty(property))
    if value not in current:
        current.append(value)
        propertySheet.manage_changeProperties(**{property : current})

    print >> out, "Added %s to %s" % (value, property)

def addFormControllerAction(context, out, controller, template, status,
                                contentType, button, actionType, action):
    """Add the given action to the portalFormController"""
    controller.addFormAction(template, status, contentType,
                                button, actionType, action)
    print >> out, "Added action %s to %s" % (action, template)

def handle_form_controllers(context):

    if isNotOurProfile(context):
        return

    out = StringIO()
    site = context.getSite()
    controller = getToolByName(site, 'portal_form_controller')
    addFormControllerAction(site, out, controller, 'validate_integrity',
                            'success', 'Imprensa', None, 'traverse_to', 'string:imprensa_save')
    addFormControllerAction(site, out, controller, 'validate_integrity',
                            'success', 'Inscricao', None, 'traverse_to', 'string:inscricao_save')
    addFormControllerAction(site, out, controller, 'validate_integrity',
                            'success', 'PalestraRelampago', None, 'traverse_to', 'string:palestra_relampago_save')
    addFormControllerAction(site, out, controller, 'validate_integrity',
                            'success', 'Palestra', None, 'traverse_to', 'string:palestra_save')
    addFormControllerAction(site, out, controller, 'validate_integrity',
                            'success', 'Treinamento', None, 'traverse_to', 'string:treinamento_save')
