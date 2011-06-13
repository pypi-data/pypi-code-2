# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='django-migrate-mail',
    version='0.2.1',
    author='Mikhail Sayapin',
    author_email='mikhail.sayapin@gmail.com',
    url='http://bitbucket.org/msayapin/gmailcopy',
    description='Copy Gmail messages to another Gmail account.',
    zip_safe=False,

    packages=[
        'migrate_mail', 
        'migrate_mail.utils', 
        'migrate_mail.migrations', 
        'la_facebook',
        'la_facebook.callbacks',
        'la_facebook.templatetags',
        'la_facebook.tests',
        'la_facebook.utils',
    ],
    install_requires=[
        'Django>=1.2',
        'South>=0.7',
        'pytils>=0.2',
    ],
)