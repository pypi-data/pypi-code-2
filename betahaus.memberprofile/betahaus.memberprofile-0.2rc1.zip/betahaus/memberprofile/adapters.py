from zope.component import adapts
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from Products.CMFPlone.interfaces import IPloneSiteRoot

from betahaus.memberprofile.interfaces import IMemberProfileSettingsAdapter, IProfileComplete  
from betahaus.memberprofile.config import DEFAULT_SETTINGS  
from betahaus.memberprofile.content.interfaces import IMemberProfile
    
class MemberProfileSettingsAdapter(object):
    """ Persistent storage for Member profile settings
    """
    implements(IMemberProfileSettingsAdapter)
    adapts(IPloneSiteRoot)

    def __init__(self, context):
        """Init fetches status updates or creates an annotation storage for them if they don't exist.
        """
        KEY = 'betahaus.memberprofile-settings'
        self.context = context

        annotations = IAnnotations(context)
        settings = annotations.get(KEY)
        
        if settings is None:
            settings = annotations[KEY] = PersistentDict()
            for k in DEFAULT_SETTINGS:
                settings[k] = DEFAULT_SETTINGS[k]

        self.settings = settings

    def get(self, key):
        """ Return value of key. Return None if it doesn't exist.
        """
        return self.settings.get(key, None)
        
    def set(self, key, value):
        """ Set key to value.
        """
        self.settings[key] = value
        

class MemberProfileCompleteAdapter(object):
    """Adapter for checking whether or not a profile is complete.
    If the profile is not complete the user will on login be redirected to the edit form of the profile.
    """
    
    implements(IProfileComplete)
    adapts(IMemberProfile)

    def __init__(self, context):
        self.context = context
    
    def is_complete(self):
        data_accessors = ['getFirstname',
                          'getLastname',
                          ]
        for field in data_accessors:
            if not getattr(self.context, field)():
                return False
        return True
                