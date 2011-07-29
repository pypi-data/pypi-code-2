## -*- coding: utf-8 -*-
##
## $Id: utils.py 4 2007-06-05 12:08:58Z gael.le-mignot $
##

from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser

class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id."""
    def getId(self):
        """Return the ID of the user."""
        return self.getUserName()

def run_as_manager(self, callback, *args, **kwargs):
    """
    Run the given function as a manager user

    self must be an acquisition context able to locate acl_users
    """
    # Create Manager security context
    tmp_user = UnrestrictedUser('manager', '', ['Manager'], '')
    tmp_user = tmp_user.__of__(self.acl_users)
    old_sm = getSecurityManager()
    try:
        newSecurityManager(None, tmp_user)
        return callback(*args, **kwargs)
    finally:
        setSecurityManager(old_sm)
			
