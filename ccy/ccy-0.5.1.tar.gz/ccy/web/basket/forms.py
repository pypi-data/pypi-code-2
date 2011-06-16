from django import forms
from django.forms.models import BaseInlineFormSet

from ccy.basket.models import Basket, clean_ccys
    

class BasketForm(forms.ModelForm):       
    currencies = forms.CharField(max_length = 1000,
                                 label = 'currencies',
                                 help_text='comma-separated list of currencies ISO 4217 codes',
                                 widget = forms.TextInput(attrs={'class':'currencies-input'}))
    color      = forms.CharField(max_length = 10,
                                 required = False,
                                 label = 'color',
                                 widget = forms.TextInput(attrs={'class':'color-picker'}))
    
    class Meta:
        model = Basket
    
    class Media:
        css = {
            'all': ('basket/layout.css',)
        }
    
    def clean_currencies(self):
        value = clean_ccys(self.cleaned_data['currencies'])
        if not value:
            raise forms.ValidationError("No Currency specified")
        return value
    
    
class BasketFormSet(BaseInlineFormSet):
    
    def clean(self):
        super(BasketFormSet, self).clean()
        ccys = {}
        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            cd  = form.cleaned_data.get('currencies',None)
            if not cd:
                continue
            dup = []
            cd  = cd.split(',')
            for c in cd:
                if ccys.get(c):
                    dup.append(c)
                else:
                    ccys[c] = c
            if dup:
                if len(dup) == 1:
                    msg = 'Currency %s is already available in another basket' % dup[0]
                else:
                    msg = 'Currencies %s are already available in another basket' % ','.join(dup)
                    
                form._errors['currencies'] = form.error_class([msg])
        
        