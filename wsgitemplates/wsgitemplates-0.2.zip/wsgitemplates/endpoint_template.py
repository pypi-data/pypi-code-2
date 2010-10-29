from paste.script.templates import var

from base import BaseTemplate

class Endpoint(BaseTemplate):
    summary = "A template for WSGI applications"
    _template_dir = "templates/endpoint"
    required_templates = 'wsgi_package',

    entrypoint_type = "paste.app_factory"
        
    vars = [
        var('entrypointname', 'The name of the application being created.' 
                              ' (lowercase letters only, no special chars)'),
        ]

