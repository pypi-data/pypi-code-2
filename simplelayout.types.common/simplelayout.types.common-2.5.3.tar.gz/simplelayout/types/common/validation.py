from Products.validation.config import validation
from Products.validation.interfaces.IValidator import IValidator

class HandleEmptyTextFieldValidator:

    __implements__ = IValidator

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kw):
        if value == '':
            field = kw['field']
            instance = kw['instance']
            
            field.set(instance, 'DELETE_FILE')
        return 1

validators = [HandleEmptyTextFieldValidator('handleEmptyTextField')]

for validator in validators:
    validation.register(validator)
