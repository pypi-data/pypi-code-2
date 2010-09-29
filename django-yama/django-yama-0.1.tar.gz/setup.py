#!/usr/bin/env python
from distutils.core import setup
from itertools import chain
from functools import partial
import os


def find_files(prefix, dirs):
    ''' Find all files in the given directories '''
    cwd = os.getcwd()
    os.chdir(os.path.join(os.path.dirname(__file__), prefix))
    def _all_files(walk_entry):
        return map(partial(os.path.join, walk_entry[0]), walk_entry[2])
    files = []
    for d in dirs:
        files += chain(*[_all_files(subdir) for subdir in os.walk(d)])
    os.chdir(cwd)
    return files

setup(
    name='django-yama',
    version=__import__('yama').get_version(),
    description='A menu application for Django',
    author='Ognjen Maric',
    author_email='ognjen.maric@gmail.com',
    url='http://code.google.com/p/django-yama/',
    download_url='http://code.google.com/p/django-yama/downloads/list',
    requires=(
        'Django (>= 1.1.0)',
        'django_mptt (>= 0.3.1)', 
    ),
    platforms=['any'],
    packages=[
        'yama',
        'yama.admin',
        'yama.templatetags',
        'yama.migrations',
    ],
    package_data={'yama' : find_files('yama', ['templates', 'media']),
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
)
