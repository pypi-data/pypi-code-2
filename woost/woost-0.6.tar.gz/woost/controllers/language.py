#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import cherrypy
from cocktail.translations import (
    get_language,
    set_language
)
from cocktail.controllers import try_decode
from cocktail.controllers.parameters import set_cookie_expiration
from woost.models import Site, Language
from woost.controllers.module import Module


class LanguageModule(Module):

    cookie_duration = 60 * 60 * 24 * 15 # 15 days

    def __init__(self, *args, **kwargs):
        Module.__init__(self, *args, **kwargs)
        
    def process_request(self, path):

        language = path.pop(0) if path and path[0] in Language.codes else None
        cherrypy.request.language_specified = (language is not None)

        if language is None:
            language = get_language() or self.infer_language()
        
        cherrypy.response.cookie["language"] = language
        cookie = cherrypy.response.cookie["language"]
        cookie["path"] = "/"
        set_cookie_expiration(cookie, seconds = self.cookie_duration)

        set_language(language)
    
    def infer_language(self):
        # TODO: Parse language headers
        cookie = cherrypy.request.cookie.get("language")
        return cookie.value if cookie else Site.main.default_language

    def translate_uri(self, path = None, language = None):

        qs = u""

        if path is None:
            path = cherrypy.request.path_info
            qs = cherrypy.request.query_string
        
        if isinstance(path, str):
            path = try_decode(path)

        if isinstance(qs, str):
            qs = try_decode(qs)

        if language is None:
            language = get_language()

        path_components = path.strip("/").split("/")
        if path_components and path_components[0] in Language.codes:
            path_components.pop(0)

        path_components.insert(0, language)
        return u"/" + u"/".join(path_components) + (u"?" + qs if qs else u"")

