from os.path import dirname, join

from setuptools import setup, find_packages



version = '0.1'

setup(
    name = 'cmsmenu-redirect',
    version = version,
    description = "Django CMS Menu Plugin for Django Contrib Redirects",
    long_description = open(join(dirname(__file__), 'README')).read() + "\n" + 
                       open(join(dirname(__file__), 'HISTORY')).read(),
    classifiers = [
        "Framework :: Django",
        "Development Status :: 4 - Beta",
        #"Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Framework :: Django",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules"],
    keywords = 'django cms plugin menu',
    author = 'Benjamin Liles',
    author_email = 'ben@ltwebdev.com',
    url = 'https://github.com/benliles/cmsmenu-redirect',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'setuptools',
        'django-cms>=2.1.0',],
)
