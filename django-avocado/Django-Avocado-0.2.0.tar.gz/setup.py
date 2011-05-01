import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Django-Avocado",
    version = "0.2.0",
    author = "Thomas Weholt",
    author_email = "thomas@weholt.org",
    description = ("Delicious delayed and cached database-logging for django."),
    license = "GPL v.3",
    keywords = "cached logging database django",
    url = "https://bitbucket.org/weholt/django-avocado",
    install_requires = ['django', 'dse'],
    zip_safe = False,
    classifiers = ["Development Status :: 2 - Pre-Alpha",
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
    packages = ['avocado'],
    include_package_data=True,
    package_data = {
        'avocado': [
            'templates/avocado/*.html',
        ]
    },
    
    long_description=read('README.txt'),
)
