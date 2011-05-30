# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='django-migrate-mail',
    version='0.1.6',
    author='Mikhail Sayapin',
    author_email='mikhail.sayapin@gmail.com',
    url='http://bitbucket.org/msayapin/gmailcopy',
    description='Copy Gmail messages to another Gmail account.',
    zip_safe=False,

    packages=['migrate_mail', 'migrate_mail.utils', 'migrate_mail.migrations'],
    install_requires=[
        'Django>=1.2',
        'South>=0.7',
        'gdata-python-client>=2.0.4',
        'pytils>=0.2',
    ],
)