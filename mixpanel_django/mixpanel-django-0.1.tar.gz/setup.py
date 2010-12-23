#!/usr/bin/env python
#-*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="mixpanel_django",
    version="0.1",
    package_dir={'mixpanel_django': 'mixpanel_django'},
    include_package_data=True,
    packages=find_packages(),
    package_data = {
        'mixpanel_django': [
            'media/scripts/*.js',
            'templates/*.html',
            'example/mp_example/templates/*.html'
        ],
    },
    install_requires=['django>=1.1', 'beanstalkc>=0.2', 'httpagentparser>=0.8.2'],

    # metadata for upload to PyPI
    author="fla.sam",
    author_email="fla.sam@gmail.com",
    description="django reuseable app, it can simply track events use mixpanel API",
    license="Apache Licence 2.0",
    keywords="python django mixpanel",
    url="https://bitbucket.org/fla.sam/mixpanel_django/", 
)
