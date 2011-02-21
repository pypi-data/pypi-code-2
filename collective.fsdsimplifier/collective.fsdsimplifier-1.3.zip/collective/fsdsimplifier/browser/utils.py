from Products.CMFCore.utils import _checkPermission
from Products.Five import BrowserView
from Products.FacultyStaffDirectory.interfaces.person import IPerson
from collective.fsdsimplifier.browser.interfaces import IFsdSimplifierLayer

class ActionUtilities(BrowserView):
    """Check permissions on Persons"""

    layer = IFsdSimplifierLayer
    
    def can_manage(self):
        """Check for manage permission"""
        return _checkPermission("FacultyStaffDirectory: Change Person IDs", self.context)

    def is_person(self):
        """Check if object is a Person"""
        
        return IPerson.providedBy(self.context)
    
    def hide_tabs(self):
        """Hide tabs if it's a Person and the user doesn't have permission to Change Person IDs"""
        return self.is_person() and not self.can_manage()
	
    def is_plone4(self):
        """Returns true for Plone 4 and higher"""
        try:
            import plone.app.upgrade
            p4 = True
        except ImportError: 
            p4 = False           
	
        return p4
