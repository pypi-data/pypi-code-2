from django import forms
from formwizard.forms import FormWizard
from django.http import HttpResponse
from django.template import Template, Context
from django.contrib.auth.models import User
from django.forms.formsets import formset_factory
from django.core.files.storage import FileSystemStorage
import tempfile

temp_storage_location = tempfile.mkdtemp()
temp_storage = FileSystemStorage(location=temp_storage_location)

class Page1(forms.Form):
    name = forms.CharField(max_length=100)
    user = forms.ModelChoiceField(queryset=User.objects.all())
    thirsty = forms.NullBooleanField()

class Page2(forms.Form):
    address1 = forms.CharField(max_length=100)
    address2 = forms.CharField(max_length=100)
    file1 = forms.FileField()

class Page3(forms.Form):
    random_crap = forms.CharField(max_length=100)

Page4 = formset_factory(Page3, extra=2)

class ContactWizard(FormWizard):
    file_storage = temp_storage

    def done(self, request, storage, form_list, **kwargs):
        c = Context({'form_list': [x.cleaned_data for x in form_list], 'all_cleaned_data': self.get_all_cleaned_data(request, storage)})
        for form in self.form_list.keys():
            c[form] = self.get_cleaned_data_for_step(request, storage, form)

        c['this_will_fail'] = self.get_cleaned_data_for_step(request, storage, 'this_will_fail')
        return HttpResponse(Template('').render(c))

    def get_template_context(self, request, storage, form):
        context = super(ContactWizard, self).get_template_context(request, storage, form)
        if storage.get_current_step() == 'form2':
            context.update({'another_var': True})
        return context