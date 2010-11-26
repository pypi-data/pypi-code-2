#!/usr/bin/env python
from distutils.core import setup

version='0.2.1'

setup(
    name='django-chart-tools',
    version=version,
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',

    packages=['chart_tools', 'chart_tools.templatetags'],
    package_data = {'chart_tools': ['templates/chart_tools/*.html']},

    url='http://bitbucket.org/kmike/django-chart-tools/',
    download_url = 'http://bitbucket.org/kmike/django-chart-tools/get/tip.zip',
    license = 'MIT license',
    description = """A thin wrapper around Google Chart API that tries not to invent a new language for describing charts.""",

    long_description = open('README.rst').read(),

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
