import os
import sys
from optparse import OptionParser
from random import choice

from django.core.management.commands import startproject, startapp

from jinja2 import Template, Environment, PackageLoader

base_dir = os.getcwd()
src_dir = os.path.join(base_dir, 'src')

def create_directory_structure():
    """ Create the directory structure for our project """
    
    # first we need a src directory
    if not os.path.exists(src_dir):
        os.mkdir(src_dir)
        
def create_project(project_name):
    """ Create the django project """
    
    print("Creating project %s in %s" % (project_name, src_dir))
    
    proposed_directory = os.path.join(src_dir, project_name.upper())
    
    if os.path.exists(proposed_directory):
        # project dir already exists, we can't do anything
        return proposed_directory
    
    # project creation needs to be in the src_dir
    os.chdir(src_dir)
    
    # create project holding dir
    os.mkdir(project_name.upper())
    os.chdir(proposed_directory)
    
    # use django to start the project
    project = startproject.Command()
    project.handle_label(project_name)
    
    print("Created project")
    
    installed_directory =  os.path.join(proposed_directory, project_name)
    
    # we don't want the default settings.py
    print("Removing default setup.py to be replaced with new")
    os.remove(os.path.join(installed_directory, 'settings.py'))
    
    os.chdir(base_dir)
    
    # return the path to the project dir
    return installed_directory

def create_app(project_dir, app_name):
    """ Create an app in a project """
    
    # get where we're creating the app
    app_dir = os.path.join(project_dir, app_name)
    
    if os.path.exists(app_dir):
        print("App %s already exists at %s" %(app_name, app_dir))
        return app_dir
    
    print("Create app %s at %s" % (app_name, app_dir))
    
    app = startapp.Command()
    app.handle_label(app_name, project_dir)
    
    print("Created app %s" % app_name)
    
    return app_dir
    
def generate_secret():
    """ Generate a secret for the django settings file 
    
    Returns a 50 char string of the secret
    """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return ''.join([choice(chars) for i in range(50)])

def generate_installed_apps(options):
    """ Generate a nice list of the installed apps that we can put into the settings template """
    
    # make this into a pretty string that can be appended to the list in the settings.py
    apps = ['    \''+ options.project + '.' +x.strip()+'\'' for x in options.apps.split(',')]
    
    return ',\n'.join(apps)
    
def create_file(path, template, template_vars):
        """ Create a file on the filesystem
        
        Arguments:
        path - Path to the file to create
        template - Path to the template file
        template_vars - Variables to use in the template as a dictionary
        
        Returns a path to the created file"""
        
        print("Creating %s from template %s" % (path, template))
        
        template_environment = Environment(loader=PackageLoader('isotoma.django.bootstrap', 'templates'))
        
        # get the template from the loader (and directory)
        loaded_template = template_environment.get_template(template)
        
        # render the template given the data that we have
        rendered_template = loaded_template.render(template_vars)
        
        # save the rendered template where we were told to
        output_file = open(path, 'w')
        output_file.write(rendered_template)
        output_file.close()
        
        # return a path to the file
        return path

def create_project_files(project_dir, options):
    """ Create the files that we need in the project directory, settings.py etc """
    
    # get the template variables that we'll need
    template_vars = {'secret': generate_secret(),
                'app_fqn': generate_installed_apps(options),
                'project_name': options.project,
                }
    
    create_file(os.path.join(project_dir, 'settings.py'), 'settings.tmpl', template_vars)
    create_file(os.path.join(project_dir, 'staging.py'), 'staging.tmpl', template_vars)
    create_file(os.path.join(project_dir, 'production.py'), 'production.tmpl', template_vars)
    
    # Create the static directory
    os.makedirs(os.path.join(project_dir, 'static'))
    # Create the templates directory
    os.makedirs(os.path.join(project_dir, 'templates'))
    
    # create the project urls file
    create_file(os.path.join(project_dir, 'urls.py'), 'urls.tmpl', template_vars)
    
    # create the manifest for the egg
    create_file(os.path.join(project_dir, '../MANIFEST.in'), 'MANIFEST.tmpl', template_vars)
    
    # create the setup.py for the project egg
    create_file(os.path.join(project_dir, '../setup.py'), 'setup.tmpl', template_vars)
    
def validate_options(options):
    """ Validate the options that have been given """
    
    # project is required
    if options.project == None:
        print "Project is a required parameter"
        sys.exit(1)
        
    if options.apps == None:
        print("Please specify at least one app")
        sys.exit(1)
        
    # if we get here, everything looks okay
    return True

def main():
    
    # Parse the command line arguments
    parser = OptionParser()
    parser.add_option("-p", "--project", action="store", dest = "project", help = "Name of the project that you want to create")
    parser.add_option("-a", "--apps", action="store", dest = "apps", help = "Comma separated list of apps to create")
    
    (options, args) = parser.parse_args()
    
    # check we have sane values here
    validate_options(options)
    
    # create the directory structure
    create_directory_structure()
    
    # now we need a normal django project that we can modify
    project_dir = create_project(options.project)
    
    # create the apps that were given
    for app in options.apps.split(','):
        create_app(project_dir, app)
        
    # create the files that we need in the project
    create_project_files(project_dir, options)
    