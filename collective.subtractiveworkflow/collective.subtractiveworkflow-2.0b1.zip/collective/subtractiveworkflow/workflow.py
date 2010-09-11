from zope.interface import implements

from AccessControl.Permission import Permission
from AccessControl.PermissionRole import rolesForPermissionOn

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.utils import ac_inherited_permissions, modifyRolesForGroup

from collective.subtractiveworkflow.interfaces import ISubtractiveWorkflowDefinition

def modifyRolesForPermission(obj, pname, roles):
    
    data = ()
    
    for permission in ac_inherited_permissions(obj, True):
        name, value = permission[:2]
        if name == pname:
            data = value
            break
    
    p = Permission(pname, data, obj)
    
    # Note: tuple = not acquired; list = acquired
    acquire = isinstance(roles, list)
    
    to_remove = set(roles)
    valid_roles = set(obj.validRoles()) - set(['Authenticated', 'Anonymous'])
    existing_roles = set([r for r in rolesForPermissionOn(pname, obj) if r and not r.endswith('_Permission')])
    
    # If we are taking away 'Anonymous', bear in mind that this implies "any role". 
    if 'Anonymous' in existing_roles and 'Anonymous' in to_remove:
        existing_roles.update(valid_roles)
        existing_roles.remove('Anonymous')
    
    # Similarly, 'Authenticated' implies "any role except Anonymous"
    if 'Authenticated' in existing_roles and 'Authenticated' in to_remove:
        existing_roles.update(valid_roles)
        existing_roles.remove('Authenticated')
    
    if acquire:
        new_roles = list(existing_roles - to_remove)
    else:
        new_roles = tuple(existing_roles - to_remove)
    
    if p.getRoles() != new_roles:
        p.setRoles(new_roles)
        return True
    
    return False

class SubtractiveWorkflowDefinition(DCWorkflowDefinition):
    """A workflow definition that takes permissions away
    """
    
    implements(ISubtractiveWorkflowDefinition)
    
    title = 'Subtractive Workflow Definition'
    
    def __init__(self, id):
        super(SubtractiveWorkflowDefinition, self).__init__(id)
    
    # Hack alert!
    
    def _executeTransition(self, ob, tdef=None, kwargs=None):
        """Execute a transition. We set a flag to defer calling
        updateRoleMappingsFor() until the event handler (see react.py) since
        we know this needs to be called eventually anyway
        """
        
        try:
            self._v_executing_transition = True
            return super(SubtractiveWorkflowDefinition, self)._executeTransition(ob, tdef, kwargs)
        finally:
            self._v_executing_transition = False
        
    def updateRoleMappingsFor(self, obj):
        """Changes the objject permissions according to the current state.
        """
        
        # Delay if we are executing a transition - the event handler will
        # do the work.
        if getattr(self, '_v_executing_transition', False):
            self._v_executing_transition = False
            # XXX: May not be right
            return True
        
        changed = False
        
        state = self._getWorkflowStateOf(obj)
        if state is None:
            return False
        
        # Update roles/permission mappings
        
        if self.permissions:
            for p in self.permissions:
                roles = []
                if state.permission_roles is not None:
                    roles = state.permission_roles.get(p, roles)
                if modifyRolesForPermission(obj, p, roles):
                    changed = 1
        
        # Update the group/local role mappings
        
        groups = self.getGroups()
        managed_roles = self.getRoles()
        
        if groups and managed_roles:
            for group in groups:
                roles = ()
                if state.group_roles is not None:
                    roles = state.group_roles.get(group, ())
                if modifyRolesForGroup(obj, group, roles, managed_roles):
                    changed = True
        
        return changed