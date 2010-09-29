
from paste.deploy.converters import asbool
from paste.script.templates import BasicPackage, var

class BlastOffPackage(BasicPackage):
    _template_dir = 'template'
    summary = "A Pylons template providing a working site skeleton configured with SQLAlchemy, mako, repoze.who, ToscaWidgets and SchemaBot."
    egg_plugins = ['PasteScript', 'Pylons']
    vars = [
        var(
            'sqlalchemy_url',
            'The SQLAlchemy URL of the database',
            default='sqlite:///%(here)s/development.db'
        ),
        var(
            'use_schemabot',
            'Enable database schema version control using SchemaBot',
            default=True
        ),
        var(
            'email_confirmation',
            'True/False: New users must click activation link from confirmation email',
            default=True
        ),
        var(
            'rum_admin',
            'True/False: Add database admin interface (using RUM) at /admin',
            default=True
        ),
        var(
            'default_user',
            'Default username to create, password will match username (leave blank for no default user)',
            default=''
        ),
    ]
    
    def pre(self, command, output_dir, vars):
        """Called before template is applied."""
        vars['email_confirmation'] = asbool(vars.get('email_confirmation', 'false'))
        vars['use_schemabot'] = asbool(vars.get('use_schemabot', 'false'))
        vars['rum_admin'] = asbool(vars.get('rum_admin', 'false'))
    

