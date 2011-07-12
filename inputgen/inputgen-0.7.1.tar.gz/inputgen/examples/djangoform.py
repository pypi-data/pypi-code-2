"""
An example involving the validation of a Django Form object.  This example
requires that you have Django installed: http://www.djangoproject.com/
"""

from django.conf import settings
settings.configure()

from django import forms

import inputgen


class MyForm(forms.Form):

    name = forms.CharField(max_length=10)
    age = forms.IntegerField(min_value=0, max_value=10)



class FormExample(inputgen.TestCase):

    @staticmethod
    def repOK(factory):
        form = factory.form
        form.data = {'name': factory.name, 'age': factory.age}
        form.is_bound = True
        form._errors = None
        return form.is_valid()

    @staticmethod
    def fin():
        f = inputgen.Factory(enable_iso_breaking=False)
        form = f.create(MyForm, init=True)
        f.set('form', form)

        names = ['fred', 'bob', 'areallylongname']
        ages = [-3, 0, 3 , 99, 1000, '     5554   ', '5', 'notanumber']
        f.set('name', names)
        f.set('age', ages)
        return f

    def run_method(self, factory):
        pass


if __name__ == "__main__":
    import unittest
    unittest.main()
