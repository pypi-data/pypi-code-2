# -*- coding: utf-8 -*-
from codecs import BOM
import glob
import os
from setuptools import setup, find_packages
from django_mailchimp_forms import get_version

readme_file = open(u'README')
long_description = readme_file.read()
readme_file.close()
if long_description.startswith(BOM):
    long_description = long_description.lstrip(BOM)
long_description = long_description.decode('utf-8')


setup(
    name='django-mailchimp-forms',
    version=get_version().replace(' ', '-'),
    description='Mailchimp registration framework for Django',
    long_description=long_description,
    author='Konstantinos Bairaktaris',
    author_email='kbairak@indifex.com',
    url='http://code.indifex.com/django-mailchimp-forms/',
    download_url='http://code.indifex.com/django-mailchimp-forms/downloads/',
    license = 'BSD',
    zip_safe = False,
    packages=find_packages(),
    classifiers=['Development Status :: 4 - Beta',
                'Environment :: Web Environment',
                'Framework :: Django',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: BSD License',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Software Development :: Libraries :: Python Modules',
                'Topic :: Utilities'],
    setup_requires = [
        "Django >= 1.2.3",
    ],
    install_requires = [
        "Django >= 1.2.3",
    ],
    package_data = {
        'django_addons': [
            'fixtures/*.json',
        ]
    },
)
