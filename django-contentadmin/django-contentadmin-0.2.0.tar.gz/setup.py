from distutils.core import setup
from setuptools import find_packages

setup(
    name = "django-contentadmin",
    version = "0.2.0",
    packages = find_packages(),
    author = "Amine chouki",
    author_email = "surfeurX@gmail.com",
    description = "Templatetags that let you modify text and image directly in the admin",
    url = "https://bitbucket.org/surfeurx/django-contentadmin",
    install_requires=[
          "django-form-utils"
    ],
    zip_safe=False,
)
