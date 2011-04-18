from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name = "django-la-facebook",
    version = "0.1.1",
    author = "pydanny",
    author_email = "pydanny@pydanny.com",
    description = "Definitive facebook auth for Django",
    long_description = open("README.rst").read(),
    license = "BSD",
    url = "http://github.com/cartwheelweb/django-la-facebook",
    packages=find_packages(),
    install_requires=["oauth2"],   
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
)
