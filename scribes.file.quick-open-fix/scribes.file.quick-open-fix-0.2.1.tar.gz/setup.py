from setuptools import setup, find_packages
import os.path

def get_plugin_dir():
    return os.path.join(os.path.expanduser('~'), '.gnome2', 'scribes', 'plugins')

setup(
    name     = 'scribes.file.quick-open-fix',
    version  = '0.2.1',
    author   = 'Anton Bobrov',
    author_email = 'bobrov@vl.ru',
    description = 'Scribes plugin. Adds project support to stock quick open plugin',
    zip_safe   = False,
    data_files = [
        ('scribes/plugins', ['PluginFixedQuickOpen.py']),
    ],
    url = 'http://github.com/baverman/scribes-goodies',    
)
