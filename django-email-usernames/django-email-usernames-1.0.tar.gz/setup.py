#/usr/bin/env python
import os
from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

version_tuple = __import__('email_usernames').VERSION
if len(version_tuple) == 3:
    version = "%d.%d.%d" % version_tuple
else:
    version = "%d.%d" % version_tuple[:2]

setup(
    name = "django-email-usernames",
    version = version,
    description = "Piggy back on django-registration and add email-based usernames.",
    author = "hakanw",
    author_email = "",
    url = "http://bitbucket.org/hakanw/django-email-usernames/",
    packages = find_packages(),
    package_data = {
        'email_usernames': [
            'templates/email_usernames/*.html',
        ]
    },
    zip_safe = True,
    classifiers = ['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
)


