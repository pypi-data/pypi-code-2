from zope.interface import implements
from interfaces import IFormData


class FormData(object):

    implements(IFormData)

    def __init__(self):

        object.__init__(self)
        self._fields = {}


    def __getitem__(self, fieldId):

        """ Always return something... even if the data isn't
        there. This allows for a somewhat lax policy in evaluation of
        requiredness, relevance, etc.
        """

        try:
            return self._fields[fieldId].value
        except:
            return None

    def getField(self, fieldId):

        return self._fields.get(fieldId, None)


    def addField(self, field):

        self._fields[field.id] = field


    def getFields(self):

        return self._fields.keys()
