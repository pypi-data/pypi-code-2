from zope.formlib import form
from interfaces import IDemoContent
from z3c.widget.autocomplete.widget import AutoCompleteWidget

class DemoEditForm(form.EditForm):
    
    form_fields = form.Fields(IDemoContent)
    form_fields['country'].custom_widget=AutoCompleteWidget
