from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django import forms
from haystack.forms import ModelSearchForm, model_choices

overrides = {'cms.title': _('Page')}
overrides.update(getattr(settings, 'CMS_FACETSEARCH_LABEL_OVERRIDES', {}))

def override_model_choices(site=None):
    choices = model_choices(site=site)
    new_choices = []
    for k, v in choices:
        new_choices.append((k, overrides.get(k, v)))
    return sorted(new_choices, key=lambda x: x[1])

class CmsFacetSearchModelForm(ModelSearchForm):

    selected_facets = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.selected_facets = kwargs.pop("selected_facets", [])
        super(CmsFacetSearchModelForm, self).__init__(*args, **kwargs)
        self.fields['models'] = forms.MultipleChoiceField(choices=override_model_choices(), required=False, label=_('Search In'), 
widget=forms.CheckboxSelectMultiple)

    def search(self):
        sqs = super(CmsFacetSearchModelForm, self).search()
        
        if hasattr(self, 'cleaned_data') and self.cleaned_data['selected_facets']:
            sqs = sqs.narrow(self.cleaned_data['selected_facets'])
        
        return sqs.models(*self.get_models())


