from paste.script.templates import var

from base import BaseTemplate

class Middleware(BaseTemplate):
    summary = "A template for WSGI filters"
    _template_dir = "templates/middleware"
    required_templates = 'wsgi_package',

    entrypoint_type = "paste.filter_factory"

    vars = [
        var('entrypointname', 'The name of the middleware filter being created.' 
                              ' (lowercase letters only, no special chars)'),
        ]

