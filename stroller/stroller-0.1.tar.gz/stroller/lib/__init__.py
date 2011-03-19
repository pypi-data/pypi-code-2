# -*- coding: utf-8 -*-
import pylons, tg
from tg.i18n import get_lang
import tw.api
import tw.jquery

class IconLink(tw.api.Link):
    """
    A link to an icon.
    """
    template = """<img src="$link" alt="$alt" title="$title"/>"""
    
    params = dict(alt="Alternative text when not displaying image",
                  title="the tooltip of the image")
    
    def __init__(self, *args, **kw):
        super(IconLink, self).__init__(*args, **kw)
        self.alt = kw.get('alt')
        self.title = kw.get('alt')
        
manage_css = tw.api.CSSLink(modname = 'stroller', filename = 'static/manage.css')
style_css = tw.api.CSSLink(modname = 'stroller', filename = 'static/style.css')
confirm_css = tw.api.CSSLink(modname = 'stroller', filename = 'static/confirm.css')

def language():
    langs = []
    
    lang = get_lang()
    if lang:
        if isinstance(lang, list):
            langs.extend(lang)
        else:
            langs.append(lang)
        
    for lang in tg.request.languages:
        try:
            ltype, lsubtype = lang.split('-', 1)
        except:
            ltype, lsubtype = lang, lang
        
        if ltype != lsubtype:
            langs.append(lang)
        langs.append(ltype)
        
    langs.append(tg.config.get('default_language', 'en'))
    return langs

def stroller_url(path, *args, **kwargs):
    stroller_root = tg.config.get('stroller_root', '/shop')
    if path[0] == '/':
        path = stroller_root + path
    path = pylons.url(path, *args, **kwargs)
    return path
