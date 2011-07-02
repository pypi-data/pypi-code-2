'''
Administration panel.
'''
import os
from gae import forms
from gae.pages import Pages
from apps.user import login_required

"""
TODO: hide in SelfReferenceProperty option reference to current object
"""
def _load_config(app_name, model_name):
    """Load model configuration"""
    module = __import__("apps.%s.admin" % app_name, {}, {}, ["admin"])
    # create instance
    return getattr(module, model_name)()

def _models_list(app_name):
    admin_path = "apps.%s.admin" % app_name
    package = __import__(admin_path, {}, {}, ["admin"])
    models = [model for model in dir(package) if hasattr(getattr(package, model), "__module__") and getattr(package, model).__module__.startswith(admin_path)]
    # set real model name
    for index, model_name in enumerate(models):
        # load model
        config = _load_config(app_name, model_name)
        models[index] = (model_name, hasattr(config, "name") and config.name or model_name)
    return models

@login_required('admin')
def apps_list(app):
    '''
    Show list of applications with enabled administrative interface and all models in each application.
    '''
    # get list of all applications with admin.py file
    apps = [appname for appname in os.listdir('apps') if os.path.isdir(os.path.join('apps', appname)) and os.path.exists(os.path.join('apps', appname, 'admin.py'))]
    apps_models = []
    # get list of all models in each application
    for app_name in apps:
        apps_models.append((app_name, _models_list(app_name)))
    return app.render("admin/apps_list", {
        'apps': apps_models,
        })

@login_required('admin')
def models_list(app, app_name):
    '''
    Show list of objects in specified application.
    '''
    return app.render('admin/models_list', {
        'managed_app': app_name,
        'models': _models_list(app_name),
        })

@login_required('admin')
def model_records(app, app_name, model_name):
    '''
    Show list of records in model.

    Args:
      obj - type of objects for list
    Return:
      items_pages - count of all pages
      items - articles list on current page
    '''
    # load model
    config = _load_config(app_name, model_name)
    inline_form = config.forms[2]
    model = inline_form.Meta.model
    fields = [{'name': field_name, 'type': getattr(model, field_name).__class__.__name__[0:-8]} for field_name in inline_form().fields.keys()]
    items = model.all() # get list of records
    return app.render('admin/model_records', {
        'managed_app': app_name,
        'model': model_name,
        'model_name': hasattr(config, "name") and config.name or model_name,
        'records': Pages(items, 20),
        'fields': fields
        })

@login_required('admin')
def create_record(app, app_name, model_name):
    # load model
    config = _load_config(app_name, model_name)
    Form = config.forms[0]
    Model = Form.Meta.model
    # handle form
    if app.request.POST:
        # filled form
        form = Form(data=app.request.POST)
        if form.is_valid():
            if hasattr(config, "before_save"):
                config.before_save()
            record = form.save()
            if hasattr(config, "after_save"):
                config.after_save(record)
            return app.redirect("go back")
    # empty form
    else:
        form = Form()
    # render page
    return app.render('admin/create_record', {
        'managed_app': app_name,
        'model': model_name,
        'model_name': hasattr(config, "name") and config.name or model_name,
        'form': form,
        })

@login_required('admin')
def edit_record(app, app_name, model_name, record_key):
    # load model
    config = _load_config(app_name, model_name)
    Form = config.forms[0]
    Model = Form.Meta.model
    # get record object
    record = Model.get(record_key)
    # record not found
    if record is None:
        return app.error(404)
    # handle form
    if app.request.POST:
        # filled form
        form = Form(data=app.request.POST, instance=record)
        if form.is_valid():
            if hasattr(config, "before_change"):
                config.before_change(record)
            form.save()
            if hasattr(config, "after_change"):
                config.after_change(record)
            return app.redirect("go back")
    # empty form
    else:
        form = Form(instance=record)
    # render page
    return app.render('admin/edit_record', {
        'managed_app': app_name,
        'model': model_name,
        'model_name': hasattr(config, "name") and config.name or model_name,
        'record': record,
        'form': form,
        })

@login_required('admin')
def delete_record(app, app_name, model_name, record_key=None):
    if record_key is None:
        # get records id from POST request
        record_keys = app.request.get_all("record_key")
    else:
        # use one record key passed to query string
        record_keys = [record_key]
    try:
        # load model and get record from this model
        config = _load_config(app_name, model_name)
        Form = config.forms[0]
        Model = Form.Meta.model
    except AttributeError:
        record = None
    # delete each specified record
    for record_key in record_keys:
        record = Model.get(record_key)
        if record is not None:
            if hasattr(config, "before_delete"):
                config.before_delete(record)
            record.delete()
            if hasattr(config, "after_delete"):
                config.after_delete()
    return app.redirect("go back")