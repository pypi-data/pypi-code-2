from functools import wraps

from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models import get_model
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404

from django_inline import templates_list


def _raise_error(label):
    message = 'Bad object id: "%s"' % label

    raise Exception(message) if settings.DEBUG else Http404(message)


def get_params(func):
    """
    Automatic extraction of id (label), model class and target object from
    request object. Gracefully raises 404 errors if the id is wrong.
    """
    @wraps(func)
    def decorated(request):
        # the id can be in get, post or put method
        # this has to be de-hard-coded
        id = any(getattr(request, method, {}).get('id') for method in ('GET', 'POST', 'PUT'))
        try:
            app_label, class_name, pk, field_name = id.split('.')
        except ValueError:  # if the number of items in the string is wrong
            _raise_error(id)

        model = get_model(app_label, class_name)
        if model is None:
            _raise_error(id)

        obj = get_object_or_404(model, pk=int(pk))
        return func(request, obj, field_name, id)

    return decorated


@get_params
def widget(request, obj, field_name, id):
    """
    Creates a form on the fly and renders it in a template.

    The widget is automatically generated from a model form for the model.

    You can override the template with your own. It has to be named 'inline-form.html', and can be put in templates/%app_name%/%model_name%, templates/%app_name% or templates folder (folders are searched in the given order).
    """
    class Form(forms.Form):
        id = forms.CharField(widget=forms.HiddenInput())
        value = admin.site._registry[obj.__class__].get_form(obj.pk).base_fields[field_name]

    return render_to_response(templates_list('inline-form.html', obj), {
        'form': Form(initial={'id': id, 'data': getattr(obj, field_name)}),
    })


@get_params
def update(request, obj, field_name, id):
    """
    Checks user permissions and saves the data in the model.
    """
    if request.user.has_perm('%s.can_edit' % obj.__class__.__name__):
        setattr(obj, field_name, request.POST['data'])
        obj.save()

    return HttpResponse(getattr(obj, field_name))
