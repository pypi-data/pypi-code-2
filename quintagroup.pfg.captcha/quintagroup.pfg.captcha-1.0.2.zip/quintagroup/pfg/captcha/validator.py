from Products.CMFCore.utils import getToolByName
from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator
from zope.interface import implements

from Products.CMFPlone.utils import safe_hasattr

class CaptchaValidator:

    implements(IValidator)

    name = 'CaptchaValidator'
    title = ""
    description = ""

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):

        form  = kwargs.get('instance')
        portal = getToolByName(form, 'portal_url').getPortalObject()
        result = portal.captcha_validator()
        if result.status == 'failure':
            return ("%(problem)s" % {'problem' : result.errors['key'][0]})
        else:
            return 1

validation.register(CaptchaValidator('isCaptchaCorrect'))
