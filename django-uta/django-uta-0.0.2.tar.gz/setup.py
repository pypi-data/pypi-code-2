import sys, os
from distutils.core import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README')).read()
version = "0.0.2"

setup(
    name = "django-uta",
    packages = ["uta"],
    version = version,
    description = "Unobtrusive Template Adapter",
    author = "Alexander Pugachev",
    author_email = "alexander.pugachev@gmail.com",
    url = "https://github.com/peroksid/django-uta",
    keywords = ["django", "templates"],
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        ],
    long_description = README
)