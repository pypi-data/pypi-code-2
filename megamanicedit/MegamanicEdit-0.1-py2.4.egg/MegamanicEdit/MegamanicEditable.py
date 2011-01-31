from zope.interface import implements
from interfaces import MegamanicEditableObject

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class MegamanicEditable:
    implements(MegamanicEditableObject)

    security = ClassSecurityInfo()

    security.declarePublic('isMegamanicEditable')
    def isMegamanicEditable(self, object=None):
        "Yes it is."
        if object is None: object = self
        # Why portal_interfaces doesn't see the implementation is beyond me.
        return MegamanicEditableObject.implementedBy(object.__class__)

    security.declarePublic('getMegamanicEditableFields')
    def getMegamanicEditableFields(self):
        """Returns names of the fields we can edit."""
        return ('title', 'description')

    security.declarePublic('megamanicHackRequest')
    def megamanicHackRequest(self, object):
        """Hacks the request so we can edit things."""
        object_name = object.getId()
        request = self.REQUEST
        request.set('megamanic_edit_hack_request', [])

        for key in request.form.keys():
            if key.startswith(object_name):
                field_name = key[len(object_name)+1:]
                request.form[field_name] = request[key]
                request['megamanic_edit_hack_request'].append(field_name)

    security.declarePublic('megamanicHackRequestClear')
    def megamanicHackRequestClear(self):
        """Clears the request after modifying it to edit things."""
        for name in self.REQUEST.get('megamanic_edit_hack_request', []):
            del request.form[name]

InitializeClass(MegamanicEditable)
