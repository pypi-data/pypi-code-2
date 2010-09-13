'''A django abstract model and form for handling extra content in a model.'''
VERSION = (0, 1)
 
def get_version():
    if len(VERSION) == 3:
        v = '%s.%s.%s' % VERSION
    else:
        v = '%s.%s' % VERSION[:2]
    return v
 
__version__ = get_version()
__license__  = "BSD"
__author__   = "Luca Sbardella"
__contact__  = "luca.sbardella@gmail.com"
__homepage__ = "http://github.com/lsbardel/django-extracontent"



def content(name):
    from django.contrib.contenttypes.models import ContentType
    res = ContentType.objects.filter(model = name.lower())
    if res.count() == 1:
        return res[0]
    else:
        raise ValueError