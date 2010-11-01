from zope.traversing.namespace import view
from zope.publisher.interfaces import Unauthorized

class principal(view):

    """a principal namespace"""
    
    def traverse(self, name, ignored):
        self.request.shiftNameToApplication()
        pid = self.request.principal.id
        if name != pid:
            raise Unauthorized("++principal++%s" % name)
        return self.context
