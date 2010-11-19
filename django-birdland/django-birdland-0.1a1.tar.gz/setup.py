import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'django-birdland',
    version = '0.1a1',
    license = 'BSD',
    description = 'A simple blog app for Django',
    long_description = read('README'),
    author = 'Jeff Kistler',
    author_email = 'jeff@jeffkistler.com',
    url = 'https://bitbucket.org/jeffkistler/django-backlinks',
    packages = ['birdland', 'birdland.templatetags', 'birdland.views'],
    package_dir = {'': 'src'},
    package_data = {'birdland': ['fixtures/*',]},
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
