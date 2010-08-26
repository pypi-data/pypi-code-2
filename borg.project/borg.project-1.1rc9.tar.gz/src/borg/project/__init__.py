from zope.i18nmessageid import MessageFactory
from Products.CMFCore.permissions import setDefaultRoles

ProjectMessageFactory = MessageFactory('borg.project')

setDefaultRoles("b-org: Add Project", ('Manager',))

def initialize(context):
    """Intializer called when used as a Zope 2 product."""

    pass
