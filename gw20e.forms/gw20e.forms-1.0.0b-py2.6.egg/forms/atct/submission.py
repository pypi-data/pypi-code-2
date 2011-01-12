from zope.interface import implements
from Acquisition import aq_base
from Products.Archetypes.utils import shasattr

from gw20e.forms.submission.interfaces import ISubmission


DATA_ATTR_NAME = "gw20e.forms.data"


class ATCTSubmission:

    """ Submission handler that submits data to content type.
    """

    implements(ISubmission)


    def __init__(self, context):

        """ CTSubmission uses simple attribute storage to store the
        whole data container on the context.
        """

        self._context = context


    def submit(self, data, model):

        """ Submit data. This involves storing it onto the content
        type.
        """

        try:
            setattr(aq_base(self._context), DATA_ATTR_NAME, data)            
            self._context.reindexObject()
        except:
            pass


    def retrieve(self):

        """ Restore data. """

        if not shasattr(self._context, DATA_ATTR_NAME):
            raise AttributeError(DATA_ATTR_NAME)
        return getattr(self._context, DATA_ATTR_NAME)
    
