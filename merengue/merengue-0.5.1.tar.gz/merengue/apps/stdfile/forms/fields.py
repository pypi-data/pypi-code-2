from django import forms

from stdfile.forms.widgets import RemovableFileFormWidget


class RemovableFileFormField(forms.MultiValueField):

    widget = RemovableFileFormWidget
    field = forms.FileField
    is_image = False

    def __init__(self, *args, **kwargs):
        fields = [self.field(*args, **kwargs), forms.BooleanField(required=False)]
        # Compatibility with form_for_instance
        if kwargs.get('initial'):
            initial = kwargs['initial']
        else:
            initial = None
        self.widget = self.widget(is_image=self.is_image, initial=initial)
        super(RemovableFileFormField, self).__init__(fields, label=kwargs.pop('label'),
                                                     help_text=kwargs.pop('help_text'), required=False)

    def compress(self, data_list):
        return data_list


class RemovableImageFormField(RemovableFileFormField):
    field = forms.ImageField
    is_image = True
