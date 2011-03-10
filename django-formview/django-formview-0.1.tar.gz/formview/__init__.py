from django.forms import ModelForm
from django.http import HttpResponse

class FormView(object):
  """
  FormView encapsulates the typical flow connecting a view to a ModelForm.
  """

  def __init__(self, model, template_name, 
               fields = None, 
               exclude = None, 
               widgets = None,
               item_id_field = "pk",
               extra_template_args = {}):
    self.model = model
    self.template_name = template_name
    self.fields = fields
    self.exclude = exclude
    self.widgets = widgets
    self.item_id_field = item_id_field
    self.extra_template_args = extra_template_args


  # Overridable
  def make_default_instance(self, request):
    return None

  # Overridable
  def success(self, request, form):
    from playfi.util import success_response
    form.save()
    return success_response()

  # Overridable
  def pre_setup_check(self, request, item_id):
    return None

  # Overridable
  def post_setup_check(self, request, item_id, form, instance):
    return None

  # Overridable
  def make_model_form(self, data = None, files = None, instance = None, request = None):
    form_view = self

    class MyModelForm(ModelForm):
      class Meta:
        model = form_view.model
        if form_view.fields:
          fields = form_view.fields
        if form_view.exclude:
          exclude = form_view.exclude
        if form_view.widgets:
          widgets = form_view.widgets

    return MyModelForm(data = data, files = files, instance = instance)


  # Overridable
  def _response(self, template, context, request):
    return HttpResponse(self._to_string(template, context, request))

  # Overridable
  def _to_string(self, template, context, request):
    from django.template.loader import render_to_string
    from django.template.context import RequestContext

    return render_to_string(template,
                            context,
                            context_instance = RequestContext(request))

  # Overridable
  def extra_context(self, request, item_id):
    return {}


  # Overridable
  def is_valid(self, request):
    return self.form.is_valid()


  def to_response(self, request, item_id = None):
    return self._execute(request, item_id, method = self._response)

  def __call__(self, request, item_id = None):
    return self.to_response(request, item_id)

  def to_string(self, request, item_id = None):
    return self._execute(request, item_id, method = self._to_string)

  def _execute(self, request, item_id, method):
    r = self.pre_setup_check(request, item_id)
    if r != None:
      return r

    if request.method == "POST":
      self.instance = self.model.objects.get(**{self.item_id_field: item_id}) \
                      if item_id \
                      else self.make_default_instance(request)

      self.form = self.make_model_form(request = request,
                                       data = request.POST, 
                                       files = request.FILES, 
                                       instance = self.instance)
    else:
      if item_id:
        self.instance = self.model.objects.get(**{self.item_id_field: item_id})
        self.form = self.make_model_form(request = request, instance = self.instance)
      else:
        self.instance = self.make_default_instance(request)
        self.form = self.make_model_form(request = request, instance = self.instance)

    r = self.post_setup_check(request, item_id, self.form, self.instance)
    if r != None:
      return r

    if request.method == "POST" and self.is_valid(request):
      return self.success(request, self.form)
    else:
      return method(self.template_name,
                    dict(form = self.form,
                         instance = self.instance,
                         **dict(self.extra_template_args,
                                **self.extra_context(request, item_id))),
                    request)

