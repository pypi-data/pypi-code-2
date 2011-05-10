from zope.interface import alsoProvides, implementsOnly
from zope.schema.interfaces import ITitledTokenizedTerm
from zope.i18n import translate

from z3c.form.widget import FieldWidget
from z3c.form.browser.select import SelectWidget
from z3c.form.browser.orderedselect import OrderedSelectWidget
from z3c.form.browser.widget import HTMLSelectWidget, addFieldClass
from z3c.form.widget import SequenceWidget
from z3c.form.interfaces import NOVALUE

from collective.properties.interfaces import ISpecialSelectWidget, \
    ISpecialOrderedSelectWidget

class SpecialSelectWidget(SelectWidget):
    """Custom Select widget implementation.
    
    What's customized:
        * separate converter which won't break if selected value is not
          within widget terms at the moment
        * widget doesn't use term tokens only term values, we need this fix
          to make IPropertyManager selection property type work with terms
          containing non-ascii characters (token couldn't not contain it) as
          native property manager edit form support it
    """
    
    implementsOnly(ISpecialSelectWidget)

    def isSelected(self, term):
        return term.value in self.value

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        HTMLSelectWidget.update(self)
        SequenceWidget.update(self)
        addFieldClass(self)
        self.items = []
        if (not self.required or self.prompt) and self.multiple is None:
            message = self.noValueMessage
            if self.prompt:
                message = self.promptMessage
            self.items.append({
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': message,
                'selected': self.value == []
                })
        for count, term in enumerate(self.terms):
            selected = self.isSelected(term)
            id = '%s-%i' % (self.id, count)
            content = term.value
            if ITitledTokenizedTerm.providedBy(term):
                content = translate(
                    term.title, context=self.request, default=term.title)
            self.items.append(
                {'id':id, 'value':term.value, 'content':content,
                 'selected':selected})

    @property
    def displayValue(self):
        value = []
        for token in self.value:
            # Ignore no value entries. They are in the request only.
            if token == self.noValueToken:
                continue
            term = self.terms.getTermByValue(token)
            if ITitledTokenizedTerm.providedBy(term):
                value.append(translate(
                    term.title, context=self.request, default=term.title))
            else:
                value.append(term.value)
        return value

    def extract(self, default=NOVALUE):
        """See z3c.form.interfaces.IWidget."""
        if (self.name not in self.request and
            self.name+'-empty-marker' in self.request):
            return []
        value = self.request.get(self.name, default)
        if value != default:
            for token in value:
                if token == self.noValueToken:
                    continue
                try:
                    self.terms.getTerm(token)
                except LookupError:
                    return default
        return value

def SpecialSelectFieldWidget(field, request):
    """IFieldWidget factory for SelectWidget which won't break
    when selected value is not within widget terms.
    And also which doesn't use term tokens but only term values.
    """
    return FieldWidget(field, SpecialSelectWidget(request))

class SpecialOrderedSelectWidget(OrderedSelectWidget):
    """Custom Ordered-Select widget implementation.
    
    We customized it here for the same purposes we did with SelectWidget
    defined above: token to value conversion and assign custom converter.
    """
    implementsOnly(ISpecialOrderedSelectWidget)

    def getItem(self, term, count=0):
        id = '%s-%i' % (self.id, count)
        content = term.value
        if ITitledTokenizedTerm.providedBy(term):
            content = translate(
                term.title, context=self.request, default=term.title)
        return {'id':id, 'value':term.value, 'content':content}

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        HTMLSelectWidget.update(self)
        SequenceWidget.update(self)
        addFieldClass(self)
        self.items = [
            self.getItem(term, count)
            for count, term in enumerate(self.terms)]
        self.selectedItems = [
            self.getItem(self.terms.getTerm(token), count)
            for count, token in enumerate(self.value)]
        self.notselectedItems = self.deselect()

    @property
    def displayValue(self):
        value = []
        for token in self.value:
            # Ignore no value entries. They are in the request only.
            if token == self.noValueToken:
                continue
            term = self.terms.getTermByValue(token)
            if ITitledTokenizedTerm.providedBy(term):
                value.append(translate(
                    term.title, context=self.request, default=term.title))
            else:
                value.append(term.value)
        return value

    def extract(self, default=NOVALUE):
        """See z3c.form.interfaces.IWidget."""
        if (self.name not in self.request and
            self.name+'-empty-marker' in self.request):
            return []
        value = self.request.get(self.name, default)
        if value != default:
            for token in value:
                if token == self.noValueToken:
                    continue
                try:
                    self.terms.getTerm(token)
                except LookupError:
                    return default
        return value

def SpecialSequenceSelectFieldWidget(field, request):
    return FieldWidget(field, SpecialOrderedSelectWidget(request))
