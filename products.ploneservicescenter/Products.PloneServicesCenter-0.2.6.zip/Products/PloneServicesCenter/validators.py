from zope.interface import implements

from Products.validation.interfaces.IValidator import IValidator


class IndustriesValidator:
    implements(IValidator)

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        if len([v for v in value if v]) > 2:
            return 'Please select at most two industries'
        return True
