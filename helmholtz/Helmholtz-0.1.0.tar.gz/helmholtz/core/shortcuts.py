#encoding:utf-8
import os
from fnmatch import fnmatch
from django.contrib.contenttypes.models import ContentType   

def get_subclasses(cls, proxies=False):
    if proxies :
        return cls.__subclasses__()
    else :
        return [k for k in cls.__subclasses__() if (k._meta.proxy == False)]

def generic_filter(entity, obj, ct_field, fk_field):
    """Returns the permissions relative to a specified object"""
    content_type = ContentType.objects.get_for_model(obj)
    kwargs = {ct_field + '__pk':content_type.id, fk_field:obj.id}
    queryset = entity.objects.filter(**kwargs)
    return queryset 

def cast_object_to_leaf_class(obj):
    """Cast an object to its actual class."""
    subclasses = get_subclasses(obj.__class__)
    has_got_subclass = False
    for subcls in subclasses :
        try :
            node = getattr(obj, subcls.__name__.lower())
            has_got_subclass = True
            break
        except :
            continue
    if has_got_subclass :
        return cast_object_to_leaf_class(node)
    else :
        return obj

def visit(arg, dirname, names) :
    path = "%s/" % (dirname) if (dirname != '/') else dirname
    for file in names :
        if fnmatch(file.lower(), arg[0].lower()) :
            arg[1].append(path + file)

def find_file(folder='/', pattern='*') :
    pathes = []
    args = [pattern, pathes]
    os.path.walk(folder, visit, args)
    return pathes

def get_class(application, model_name):
    ct = ContentType.objects.get(app_label=application, model=model_name.lower())
    return ct.model_class()

def download_status_as_html(file, user):
    status = file.download_status_key(user)
    html = {
        None: '<a href="%s">Request</a>' % file.pk,
        'requested': 'Requested',
        'refused': '<span class="warning">Refused</span>',
        'not_available': '<span class="warning">Not Available</span>',
        'all_formats':'<span class="download">DAT</span>|<span class="download">H5</span>' 
    }
    return html[status]
