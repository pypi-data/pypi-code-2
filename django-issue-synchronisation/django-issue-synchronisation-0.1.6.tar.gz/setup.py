# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='django-issue-synchronisation',
    version=__import__('issues').__version__,
    description='Issue synchronisation for django applications',
    long_description="""Synchronises different issue trackers into a django based application.""",
    author='Henning Kage',
    author_email='henning.kage@googlemail.com',
    url='http://django-issue-synchronisation.googlecode.com',
    license='GPLv3',
    platform='Any',
    packages=find_packages(),
    data_files=[('issues/fixtures', ['issues/fixtures/initial_data.json'])],
    install_requires=['Django>=1.2'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Bug Tracking'
        ],
)
