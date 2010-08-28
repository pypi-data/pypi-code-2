from paste.script import templates
from paste.script import pluginlib
from tempita import paste_script_template_renderer

class Template(templates.Template):
    """Override template class so we can use shabti_* vars in templates
    """
    def pre(self, command, output_dir, vars):
        command.run_command = pluginlib.egg_info_dir = lambda *args, **kwargs: ''
        project = vars['project']
        if project.startswith('django-'):
            vars['egg'] = project.split('-', 1)[1]
            vars['package'] = project.split('-', 1)[1]
        vars['version'] = '0.1'
        vars['description'] = '%s project' % project
        vars['long_description'] = ''
        vars['author'] = ''
        vars['author_email'] = ''
        vars['license_name'] = 'GPL'
        vars['keywords'] = 'django'
        vars['url'] = ''
        vars['zip_safe'] = False

class DjangoProjectTemplate(Template):
    required_templates = []
    _template_dir = 'templates/project'
    summary = 'Django project template'
    template_renderer = staticmethod(paste_script_template_renderer)

class DjangoAppTemplate(Template):
    required_templates = []
    _template_dir = 'templates/app'
    summary = 'Django pluggable app template'
    template_renderer = staticmethod(paste_script_template_renderer)


