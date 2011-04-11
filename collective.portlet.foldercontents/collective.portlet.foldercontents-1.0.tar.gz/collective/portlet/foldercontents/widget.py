from zope.app.form.browser.source import SourceInputWidget
from zope.app.form import InputWidget 
from zope.component import getMultiAdapter
from zope.schema._bootstrapinterfaces import RequiredMissing
from zope.app.form.interfaces import WidgetInputError, MissingInputError
from zope.schema.interfaces import ValidationError


def FixedErrorMessageChoiceInputWidget(field, request):
    return FixedErrorMessageSourceInputWidget(field, field.vocabulary, request)

class FixedErrorMessageSourceInputWidget(SourceInputWidget):
    """Widget that override SourceInputWidget to fix mistake in getInputValue"""
    
    def getInputValue(self):
        for name, queryview in self.queryviews:
            if name+'.apply' in self.request:
                token = self.request.form.get(name+'.selection')
                if token is not None:
                    break
        else:
            token = self.request.get(self.name)
    
        field = self.context
        
        if token is None:
            if field.required:
                err = RequiredMissing()
                # KSerge: here we add err argument to fix original widget issue
                error = MissingInputError(field.__name__, self.label, err)
                self._error = error
                raise self._error
            return field.missing_value
    
        try:
            value = self.terms.getValue(str(token))
        except LookupError:
            err = ValidationError("Invalid value id", token)
            raise WidgetInputError(field.__name__, self.label, err)
    
        # Remaining code copied from SimpleInputWidget
    
        # value must be valid per the field constraints
        try:
            field.validate(value)
        except ValidationError, err:
            self._error = WidgetInputError(field.__name__, self.label, err)
            raise self._error
    
        return value
