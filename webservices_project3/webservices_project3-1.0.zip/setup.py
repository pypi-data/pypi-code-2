import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "webservices_project3",
    version = "1.0",
    packages = find_packages(),
    author = "Utsav Pandey, Antonio Claros Molina",
    author_email = "upandey@luc.edu",
    description = "Final Project for Web Services",
    url = "http://www.luc.edu",
    include_package_data = True
)