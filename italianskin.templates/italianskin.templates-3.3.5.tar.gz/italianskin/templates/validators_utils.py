from zope.interface import implements
from Products.Five.browser import BrowserView

from italianskin.templates.interfaces import IValidatorView
from italianskin.templates.config import VALIDATOR_URL

class ValidatorView(BrowserView):
    """ """
    implements(IValidatorView)

    def validateURL(self):
        return VALIDATOR_URL % {'URL':self.context.absolute_url(),}
