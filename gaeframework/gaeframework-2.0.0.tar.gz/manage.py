#!/usr/bin/python
'''
Manage GAE framework projects.
'''
import os, sys, fileinput
from getopt import getopt
from shutil import copyfile, copytree

def usage(app_name):
    return """
Usage: %s <command>

Commands:
 - run [project]             : Run development server
 - deploy [project]          : Deploy project to server
 - debug [project]           : Run project shell to debug code
 - new [project]             : Create new project
 - new [project].[app]       : Create new application in given project
 - install [project].[app]   : Create symlink to common application in given project
 - test [project]            : Run tests for project
 - test [project].[app]      : Run tests for application in given project""" % app_name


def create_project(project_name):
    '''
    Create new project (if not exists)
    '''
    gae_destination = os.path.join(os.getcwd(), project_name, 'gae')
    project_dir_source = os.path.join(os.getcwd(), 'gae', 'sceleton', 'project')
    project_dir_destination = os.path.join(os.getcwd(), project_name)
    # copy project directory
    if os.path.exists(project_dir_destination):
        print '%s project already exists' % project_name
        return False
    copytree(project_dir_source, project_dir_destination)
    # create symlink to gae framework directory
    os.symlink("../gae/", gae_destination)
    # replace placeholder to project name
    replace_text(project_dir_destination, "[project_name]", project_name, recurcive=True)
    print '%s project created' % project_name
    return True


def create_app(project_name, app_name):
    '''
    Create new application (if not exists)
    '''
    app_dir_source = os.path.join(os.getcwd(), 'gae', 'sceleton', 'app')
    app_dir_destination = os.path.join(os.getcwd(), project_name, app_name)
    # copy application directory
    if os.path.exists(app_dir_destination):
        print '%s.%s application already exists' % (project_name, app_name)
        return False
    copytree(app_dir_source, app_dir_destination)
    # replace placeholder to application name
    replace_text(app_dir_destination, "[app_name]", app_name, recurcive=True)
    print '%s.%s application created' % (project_name, app_name)
    return True


def test_project(project_name):
    '''
    Run project tests
    '''
    pass


def test_app(project_name, app_name):
    '''
    Run application tests
    '''
    pass


def replace_text(path, find_me, replace_to, recurcive=False):
    '''
    Replace one text to another in all files in the given directory
    '''
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        if os.path.isdir(file_path) and not os.path.islink(file_path) and recurcive:
            replace_text(file_path, find_me, replace_to, recurcive)
        elif os.path.isfile(file_path):
            for line in fileinput.FileInput(file_path, inplace=1):
                line = line.replace(find_me, replace_to)
                sys.stdout.write(line)
    return True


def main(command, project_name, *args):
    '''
    Execute command
    '''
    if command == "run":
        os.system('appengine/dev_appserver.py %s' % project_name)
    elif command == "deploy":
        # compile templates
        # deploy to server
        os.system('appengine/appcfg.py update %s' % project_name)
    elif command == "debug":
        pass
    elif command == "new":
        try:
            project_name, app_name = project_name.split('.', 1)
            create_project(project_name)
            create_app(project_name, app_name)
        except ValueError:
            create_project(project_name)
    elif command == "test":
        try:
            project_name, app_name = project_name.split('.', 1)
            test_app(project_name, app_name)
        except ValueError:
            test_project(project_name)
    else:
        raise TypeError
    print ''
    print 'Command execution completed!'


if __name__ == '__main__':
    try:
        main(*sys.argv[1:])
    except TypeError:
        print usage(sys.argv[0])
