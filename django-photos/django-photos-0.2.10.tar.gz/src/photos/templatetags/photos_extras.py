from django import template

from templatetag_sugar.register import tag
from templatetag_sugar.parser import Name, Variable, Constant, Optional, Model

register = template.Library()

@tag(register, [Variable(), Variable(), Constant('as'), Name()])
def get_previous(context, album, photo, asvar):
    prev = None
    for tmp in album.get_photos():
        if tmp == photo:
            context[asvar] = prev
            return ''
        else:
            prev = tmp
    
    return ''

@tag(register, [Variable(), Variable(), Constant('as'), Name()])
def get_next(context, album, photo, asvar):
    flag = False
    for tmp in album.get_photos():
        if flag == True:
            context[asvar] = tmp
            return ''
        if tmp == photo:
            flag = True
                
    return ''

@tag(register, [Constant('as'), Name()])
def get_photos(context, asvar):
    context[asvar] = Photos.objects.filter(display=True)
    return ''

@tag(register, [Constant('as'), Name()])
def get_albums(context, asvar):
    context[asvar] = Albums.objects.filter(display=True)
    return ''