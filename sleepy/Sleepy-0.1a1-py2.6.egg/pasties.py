from paste.script.templates import Template
from paste.deploy.converters import asbool
from tempita import paste_script_template_renderer

class SleepyTemplate( Template ):
    _template_dir = "templates/default_project"
    template_renderer = staticmethod( paste_script_template_renderer )
    summary = "Sleepy Pylons project template"
    egg_plugins = ( "PasteScript",
                    "Pylons" )
    ensure_names = ( "description",
                     "author",
                     "author_email",
                     "url" )

    def pre( self,
             command,
             output_dir,
             vars ):
        for name in self.ensure_names:
            vars.setdefault( name,
                             "" )
        vars[ "version" ] = vars.get( "version",
                                      "0.1" )
        vars[ "zip_safe" ] = asbool( vars.get( "zip_safe",
                                               "false" ))
