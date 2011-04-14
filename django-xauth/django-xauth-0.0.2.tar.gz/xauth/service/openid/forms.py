from django import forms

class PrepareForm(forms.Form):
    openid_url = forms.CharField()
