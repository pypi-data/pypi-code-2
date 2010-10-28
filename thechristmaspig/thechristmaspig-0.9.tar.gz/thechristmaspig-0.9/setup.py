import os

from setuptools import setup, find_packages

version = '0.9'

setup(
    name='thechristmaspig',
    version=version,
    description="Buildout recipe for Django. Sets up controls scripts and wsgi file.",
    long_description=open("README.rst").read(),
    classifiers=[
      'Framework :: Buildout',
      'Framework :: Django',
      'Topic :: Software Development :: Build Tools',
      'License :: OSI Approved :: BSD License',
      ],
    package_dir={'': 'thechristmaspig'},
    packages=find_packages('thechristmaspig'),
    keywords='',
    author='Preston Timmons',
    author_email='prestontimmons@gmail.com',
    url='http://github.com/prestontimmons/thechristmaspig',
    license='BSD',
    zip_safe=False,
    install_requires=[
      'zc.buildout',
      'zc.recipe.egg',
    ],
    entry_points="""
    # -*- Entry points: -*-
    [zc.buildout]
    default = recipe:Recipe
    """,
)
