from zope.formlib import form

from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel.widgets import MultiCheckBoxColumnsWidget as _MultiCheckBoxWidget


from slc.clicksearch import ClickSearchMessageFactory as _
from slc.clicksearch.interfaces import IClickSearchConfiguration

def MultiCheckBoxWidget(field, request):
    widget = _MultiCheckBoxWidget(field, request)
    return widget 

class ClickSearchConfigurationForm(ControlPanelForm):
    form_fields = form.Fields(IClickSearchConfiguration)
    form_fields['search_metadata'].custom_widget = MultiCheckBoxWidget 
    form_fields['sort_indexes'].custom_widget = MultiCheckBoxWidget 

    form_name = _(u"Click Search settings form")
    label = _(u"Configuration Settings for Click Search")
    description = _(u"")

