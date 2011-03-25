# django mobile_utils's setup.py
from distutils.core import setup
setup(
    name = "django_mobile_utils",
    packages = ["mobile_utils"],
    version = "0.9",
    description = "Django mobile browser utilities",
    author = "Matto Todd",
    author_email = "mattotodd@gmail.com",
    url = "http://code.msul.ly/django-mobile-utils/",
    download_url = "http://code.msul.ly/download/django_mobile_utils-0.9.tgz",
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        ],
    long_description = """\
Django utils for rendering templates for mobile browser
-------------------------------------------------------

-Middleware to detects mobile browsers
-Template Loader to load mobile templates
-Context Processor that adds mobile_browser flag


This package requires django.
"""
)