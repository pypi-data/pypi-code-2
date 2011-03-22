# -*- coding: utf-8 -*-

from pylons import request
import formencode.validators
from formencode import Invalid

def valid(self, form=None, validators=None, 
            post_only=True, state_factory=None):
    if post_only:
        params = request.POST.copy()
    else:
        params = request.params.copy()

    errors = {}

    state = None
    if state_factory:
        state = state_factory()

    if form:
        try:
            self.form_result = form.validate(params, state=state)
        except Invalid, e:
            self.validation_exception = e
            errors = e.error_dict

    if validators:
        if isinstance(validators, dict):
            if not hasattr(self, 'form_result'):
                self.form_result = {}
            for field, validator in validators.iteritems():
                try:
                    self.form_result[field] = \
                        validator.to_python(
                                decoded[field] or None, state)
                except Invalid, error:
                    errors[field] = error
    if errors:
        self.errors = errors
        return False
    return True
