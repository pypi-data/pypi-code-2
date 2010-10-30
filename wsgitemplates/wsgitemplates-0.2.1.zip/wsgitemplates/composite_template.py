from paste.script.templates import var

from base import BaseTemplate

class Composite(BaseTemplate):
    summary = "A template for WSGI composites"
    _template_dir = "templates/composite"
    required_templates = 'wsgi_package',
    
    entrypoint_type = "paste.composite_factory"

    vars = [
        var('entrypointname', 'The name of the composite being created.' 
                              ' (lowercase letters only, no special chars)'),
        ]

    
