from trac.core import *
from trac.perm import IPermissionRequestor
	
revision = "$Rev$"
url = "$URL$"

class SCMAccessRequestor(Component):
    implements(IPermissionRequestor)
	
    # IPermissionRequestor methods
    def get_permission_actions(self):
		"""Returns a list of actions defined by this component."""
		yield 'SCM_READ'
		yield 'SCM_ACCESS'

