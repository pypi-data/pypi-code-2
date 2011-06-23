from Products.Five.browser import BrowserView
from teamrubber.theoracle.interfaces import ICategory
from zope.interface import implements
from AccessControl import getSecurityManager
from AccessControl.Permission import Permission

class User(BrowserView):
    implements(ICategory)
    title = "User"
    
    def __init__(self,context,request):
        self.oracle = context
        self.context = self.oracle.context
        self.request = request
    # This is all provided at the Zope level.
    
    def getAuthenticatedUser(self):
        sm = getSecurityManager()
        user = sm.getUser()
        return user
    
    def getUserName(self):
        return self.getAuthenticatedUser().getUserName()
    
    def getValidRoles(self):
        chain = self.request.get("PARENTS",self.context.aq_chain)
        for parent in chain:
            if hasattr(parent,'valid_roles'):
                return parent.valid_roles()
        return []
    
    def getRoles(self):
        user = self.getAuthenticatedUser()
        return ", ".join(user.getRoles())
    
    def getRolesInContext(self):
        user = self.getAuthenticatedUser()
        return ", ".join(user.getRolesInContext(self.context))

    def getPAS(self):
        """ Attempt to get the user folder the authenticated user is provided by """
        user = self.getAuthenticatedUser()
        try:
            container = user.aq_parent
            return "/".join(container.getPhysicalPath())
        except:
            pass
        return "Unknown"

    def getPermissions(self):

        # I'm not sure if we're allowed to trust request["PARENTS"]
        if hasattr(self.context,'getPhysicalRoot'):
            root = self.context.getPhysicalRoot()
        else:
            root = self.request["PARENTS"][-1]
        
        possible = root.possible_permissions()
        check = getSecurityManager().checkPermission

        result = {}
        acquired_permissions = possible
        depth = 0
        for parent in self.request["PARENTS"]:
            next = []
            for permission in acquired_permissions:
                p = Permission(permission,(),parent)
                roles = p.getRoles(default=[])
                for role in roles:
                    current = result.get(permission,{})
                    if role not in current:
                        current[role] = depth
                    result[permission] = current
                
                if isinstance(roles,list):
                    next.append(permission)
            depth += 1
            acquired_permissions = next
        
        for permission in result:
            result[permission]['___VALID'] = check(permission,self.context)
        
        return result
        