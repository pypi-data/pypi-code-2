import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "indeed_contactForm",
    version = "1.0.1",
    url = 'http://bitbucket.org',
    license = 'GPLv2',
    description = "A very simple Contact Form for django",
    long_description = read('README'),

    author = 'Arne Weiss',
    author_email = 'arne.weiss@udo.edu',
    
    packages = find_packages('src'),
    package_dir = {'': 'src'},

    install_requires = ['setuptools'],

    classifiers = [
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
