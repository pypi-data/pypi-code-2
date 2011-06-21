# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#
#from django.core.exceptions import *
#from django.conf import settings
#from django.template import RequestContext
from django.template.loader import render_to_string

#from asv_txt.models import *
from asv_utils.common import Str2Int
from asv_txt import settings as ATS

from creoleparser.dialects import create_dialect, creole11_base
from creoleparser.core import Parser as CrParser
from creoleparser import parse_args
from genshi import Markup
import re

Httpx_at_start = re.compile(r'^\s*http.?:\/\/')
Yt_search_key  = re.compile(r'[\?\/\&]v[\/\=]([\w\-]+)')
Yt_validate    = re.compile(r'([\w\-]+)')
#----------------------------------------------------------------
#----------------------------------------------------------------
def Yt_validate_key(key):
    k = Yt_validate.search(key)
    if (k):
        rv = k.group(1)
    else:
        rv = ''
    return rv
def Yt(macro,environ,*args,**kwargs):
    rv = ''
    if (len(args) < 1):
        return ''
    key = args[0]
    if (Httpx_at_start.match(key)):
        k = kwargs.get('v', None)
        if (k):
            key = Yt_validate_key(k)
        else:
            #print('YT key error: str={}'.format(key))
            return ''
    else:
        key = Yt_validate_key(key)
    rv = render_to_string('yt.html',{ 
        'CODE': key ,
        'S': {
            'w': ATS.ASV_TXT_YT_SIZE[0],
            'h': ATS.ASV_TXT_YT_SIZE[1],
        }
    })
    return Markup(rv)
#----------------------------------------------------------------
#----------------------------------------------------------------
def Img(macro,environ,*args,**kwargs):
    rv = ''
    iid = Str2Int(args[0],0)
    if (iid < 1):
        return ''
    CT = environ.get('CT',False)
    if not CT:
        return ''
    try:
        rv = CT.imgs.get(active=True, id=iid)
    except:
        return ''
    width = kwargs.get('width',kwargs.get('w',None))
    if (width):
        width=' width="{}"'.format(Str2Int(width))
    else:
        width=''
    href = kwargs.get('href',None)
    if (href):
        rv = '<a href="{}"><img src="{}" alt="{}" {}></a>'.format(href,rv.img.url, rv.alt ,width)
    else:
        rv = '<img src="{}" alt="{}" {}>'.format(rv.img.url, rv.alt ,width)
    return Markup(rv)
#----------------------------------------------------------------
#----------------------------------------------------------------
dia = create_dialect(creole11_base,
        #custom_markup = [
        #    #('[img]',ImgTroughtCT,),
        #    ('qqq','rereшка'),
        #],
        non_bodied_macros={
            'img':Img,
            'yt':Yt,
        },
)

Parse = CrParser(dialect=dia, method='html')
#----------------------------------------------------------------
#----------------------------------------------------------------

