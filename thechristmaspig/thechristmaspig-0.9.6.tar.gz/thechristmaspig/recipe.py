from random import choice
import logging
import os
import subprocess
import shutil

from zc.recipe.egg import Egg
import zc.buildout.easy_install

logger = logging.getLogger(__name__)


DIR = os.path.dirname(__file__)
WSGI_TEMPLATE = "".join(
    open(os.path.join(DIR, "application.wsgi")).readlines()
)
SETTINGS_TEMPLATE = "".join(
    open(os.path.join(DIR, "settings.py")).readlines()
)
URLS_TEMPLATE = "".join(
    open(os.path.join(DIR, "urls.py")).readlines()
)


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.egg = Egg(buildout, options['recipe'], options)

        options.setdefault('bin-directory',
            buildout['buildout']['bin-directory'])
        options.setdefault('project', 'project')
        options.setdefault('settings', 'settings')
        options.setdefault('create_project', 'true')
        options.setdefault('urlconf', options['project'] + '.urls')
        options.setdefault('media_root',
            "os.path.join(os.path.dirname(__file__), 'media')")
        options.setdefault('extra-paths',
            buildout["buildout"].get('extra-paths', ''))
        options.setdefault('script-name',  name)

    def install(self):
        base_dir = self.buildout['buildout']['directory']
        project_dir = os.path.join(base_dir, self.options['project'])

        extra_paths = [base_dir]
        extra_paths.extend([p.replace('/', os.path.sep) for p in
            self.options['extra-paths'].splitlines() if p.strip()])

        requirements, ws = self.egg.working_set(['thechristmaspig'])

        scripts = []

        # Create the Django management script
        scripts.extend(self.create_manage_script(extra_paths, ws))

        # Make the wsgi and fastcgi scripts if enabled
        scripts.extend(self.make_scripts(extra_paths, ws))

        if self.options['create_project'] == 'true':
            if not os.path.exists(project_dir):
                self.create_project(project_dir)
            else:
                logger.info('Skipping creating of project: %(project)s '
                    'since it exists' % self.options)

        return scripts

    def create_manage_script(self, extra_paths, ws):
        return zc.buildout.easy_install.scripts(
            [(self.options['script-name'], 'thechristmaspig.manage', 'main')],
            ws, self.options['executable'], self.options['bin-directory'],
            extra_paths = extra_paths,
            arguments= "'%s.%s'" % (self.options['project'],
                self.options['settings']))

    def create_project(self, project_dir):
        os.makedirs(project_dir)

        template_vars = {'secret': self.generate_secret()}
        template_vars.update(self.options)

        self.create_file(os.path.join(project_dir, 'urls.py'),
            URLS_TEMPLATE, template_vars)

        self.create_file(os.path.join(project_dir, 'settings.py'),
            SETTINGS_TEMPLATE, template_vars)

        # Create the media and templates directories for our project
        os.mkdir(os.path.join(project_dir, 'media'))
        os.mkdir(os.path.join(project_dir, 'templates'))

        # Add __init__.py to the project directory
        open(os.path.join(project_dir, '__init__.py'), 'w').close()

    def make_scripts(self, extra_paths, ws):
        # The scripts function uses a script_template variable hardcoded
        # in Buildout to generate the script file. Since the wsgi file
        # needs to create a callable application function rather than call
        # a script, monkeypatch the script template here.
        _script_template = zc.buildout.easy_install.script_template

        zc.buildout.easy_install.script_template = \
            zc.buildout.easy_install.script_header + WSGI_TEMPLATE

        generated = zc.buildout.easy_install.scripts(
            [('%s.wsgi' % self.options['script-name'],
                'thechristmaspig.wsgi', 'main')],
            ws, self.options['executable'], 
            self.options['bin-directory'], extra_paths = extra_paths,
            arguments= "'%s.%s'" % (self.options["project"],
                self.options['settings'])
        )

        zc.buildout.easy_install.script_template = _script_template

        return generated

    def update(self):
        self.install()

    def command(self, cmd, **kwargs):
        output = subprocess.PIPE
        if self.buildout['buildout'].get('verbosity'):
            output = None
        command = subprocess.Popen(cmd, shell=True, stdout=output, **kwargs)
        return command.wait()

    def create_file(self, file, template, options):
        if os.path.exists(file):
            return

        f = open(file, 'w')
        f.write(template % options)
        f.close()

    def generate_secret(self):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return ''.join([choice(chars) for i in range(50)])
