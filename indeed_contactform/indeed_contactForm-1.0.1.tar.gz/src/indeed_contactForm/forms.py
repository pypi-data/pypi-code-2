from django import forms


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=300, label="Betreff:")
    mail = forms.EmailField(required=False, label="Mail:")
    message = forms.CharField(widget=forms.Textarea, label="Nachricht:")
