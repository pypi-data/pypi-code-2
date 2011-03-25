# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='django-teagarden',
    version=__import__('teagarden').__version__,
    description='Database planning, visualization and code generation',
    long_description="""Teagarden is a django based webapplication used for
    database planning and modelling during the software development process.
    With Teagarden, software developers and database architects can create
    database tables, fields, constraints and relations without specifying the
    database system they want to use for their project. Teagarden aims to be a
    database development platform and documenation tool, but can also create the
    final SQL statements and compares the specific, productive database against
    the modelling metadata schema.""",
    author='Henning Kage',
    author_email='henning.kage@googlemail.com',
    url='http://django-teagarden.googlecode.com',
    license='GPL3',
    packages=find_packages(),
    install_requires=[
        'Django==1.3',],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
        ],
)
