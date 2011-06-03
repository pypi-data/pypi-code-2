import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    name = "django-mailmodel",
    version = "0.1",
    packages = find_packages(),
    author = "Amine Chouki",
    author_email = "surfeurX@gmail.com",
    description = "Reusable app for sharing objects by email",
    url = "http://bitbucket.org/surfeurX/django-mailmodel",
    include_package_data = True,
    install_requires=[
          "recaptcha-client"
    ]
)
