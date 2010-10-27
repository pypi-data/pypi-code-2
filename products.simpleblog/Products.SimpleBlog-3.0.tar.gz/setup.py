from setuptools import setup, find_packages
import os

version = '3.0'

setup(
    name='Products.SimpleBlog',
    version=version,
    description=("SimpleBlog is an easy to use Plone "
                 "based weblog application."),
    long_description=(open("README.txt").read() + "\n" +
                      open(os.path.join("docs", "HISTORY.txt")).read()),
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    author='Danny Bloemendaal',
    author_email='danny.bloemendaal@informaat.nl',
    url='ttps://svn.plone.org/svn/collective/SimpleBlog/',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        ],
    )
