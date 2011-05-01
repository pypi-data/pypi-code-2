##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: ClassGen.py 238387 2011-04-30 19:58:15Z hathawsh $
"""

from copy import deepcopy
from AccessControl import ClassSecurityInfo
from Products.Archetypes.ClassGen import ClassGenerator as ATClassGenerator
try:
    from Products.LinguaPlone.utils import registerType as _registerType
except ImportError:
    from Products.Archetypes.ArchetypeTool import registerType as _registerType

from Products.Archetypes.utils import insert_zmi_tab_after

from Products.CMFCore import permissions
from Products.CompositePack.composite import packcomposite
from Products.CompositePack import CPpermissions

def isCPMethod(m):
    return getattr(m, '__cp_method__', False)

class ClassGenerator(ATClassGenerator):

    def generateClass(self, klass):
        # We are going to assert a few things about the class here
        # before we start, set meta_type, portal_type based on class
        # name, but only if they are not set yet
        if (not getattr(klass, 'meta_type', None) or
            'meta_type' not in klass.__dict__):
            klass.meta_type = klass.__name__
        if (not getattr(klass, 'portal_type', None) or
            'portal_type' not in klass.__dict__):
            klass.portal_type = klass.__name__
        klass.archetype_name = getattr(klass, 'archetype_name',
                                       self.generateName(klass))

        self.checkSchema(klass)
        self.addMethods(klass)
        self.addOptions(klass)

    def addMethods(self, klass):
        if not klass.__dict__.has_key('security'):
            security = klass.security = ClassSecurityInfo()
        else:
            security = klass.security
        if hasattr(klass, 'design_view') and not isCPMethod(klass.design_view):
            raise TypeError, ("CompositePack cannot override design_view "
                              "method of class %s" % klass.__name__)
        if hasattr(klass, 'cp_view') and not isCPMethod(klass.cp_view):
            raise TypeError, ("CompositePack cannot override cp_view "
                              "method of class %s" % klass.__name__)
        for name, method in packcomposite.methods.items():
            old_method = getattr(klass, name, None)
            if isCPMethod(old_method):
                continue
            if old_method is not None:
                old_name = '__cp_%s__' % name
                setattr(klass, old_name, old_method)
            setattr(klass, name, method)
        security.declareProtected(CPpermissions.DesignCompo, 'design_view')
        security.declareProtected(permissions.View, 'cp_view')

    def addOptions(self, klass):
        klass.manage_options = insert_zmi_tab_after('Dublin Core', 
                                   {'label':'Composite',
                                    'action':'manage_composite_contents'},
                                   klass.manage_options)
_cg = ClassGenerator()
generateClass = _cg.generateClass

# The one below, copied from ATContentTypes
def updateActions(klass, actions):
    """Merge the actions from a class with a list of actions
    """
    kactions = deepcopy(getattr(klass, 'actions', ()))
    aids  = [action.get('id') for action in actions]
    actions = list(actions)

    for kaction in kactions:
        kaid = kaction.get('id')
        if kaid not in aids:
            actions.append(kaction)

    return tuple(actions)

def registerType(klass, package=None):
    """Overrides the AT registerType add composable features"""
    # Generate composable methods
    generateClass(klass)
    # Merge in packcomposite actions
    klass.actions = updateActions(klass, packcomposite.actions)
    # Pass on to the regular AT registerType
    _registerType(klass, package)
