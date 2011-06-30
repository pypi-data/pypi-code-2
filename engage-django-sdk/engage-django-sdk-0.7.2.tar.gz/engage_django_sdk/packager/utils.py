"""Miscellaneous utility functions"""

import os
import os.path
import json
import re

def app_module_name_to_dir(app_directory_path, app_module_name, check_for_init_pys=True):
    """The application module could be a submodule, so we may need to split each level"""
    dirs = app_module_name.split(".")
    dirpath = app_directory_path
    module_name = None
    for dirname in dirs:
        if module_name:
            module_name = module_name + "." + dirname
        else:
            module_name = dirname
        dirpath = os.path.join(dirpath, dirname)
        init_file = os.path.join(dirpath, "__init__.py")
        if check_for_init_pys and not os.path.exists(init_file):
            raise ValidationError("Missing __init__.py file for module %s" % module_name)
    return dirpath


def write_json(json_obj, filename):
    with open(filename, 'wb') as f:
        json.dump(json_obj, f)


def find_files(directory, filename_re_pattern, operation_function):
    """Find all the files recursively under directory whose names contain the specified pattern
       and run the operation_function on the fileame.
    """
    regexp = re.compile(filename_re_pattern)
    directory = os.path.abspath(os.path.expanduser(directory))
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if regexp.search(filename):
                operation_function(os.path.join(root, filename))


def get_deployed_settings_module(django_settings_module):    
    mod_comps = django_settings_module.split('.')
    if len(mod_comps)==1:
        return "deployed_settings"
    else:
        return '.'.join(mod_comps[0:-1]) + ".deployed_settings"


def import_module(qualified_module_name):
    """Import the specified module and return the contents of that module.
    For example if we have a module foo.bar containing variables x and y,
    we can do the following:
      m = import_module("foo.bar")
      print m.x, m.y
    """
    m = __import__(qualified_module_name)
    mod_comps = (qualified_module_name.split('.'))[1:]
    for comp in mod_comps:
        m = getattr(m, comp)
    return m
    
