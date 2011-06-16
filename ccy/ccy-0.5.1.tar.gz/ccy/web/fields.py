from django import forms
from ccy import period


class PeriodField(forms.CharField):
    '''A django field for entering time periods'''
    def clean(self, value):
        try:
            p = period(value)
        except:
            raise forms.ValidationError("Could not recognise period. Try 1M or 3M or 1Y and so forth.")
        value = str(p)
        return super(PeriodField,self).clean(value)
        