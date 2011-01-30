# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

def read(*rnames):
    p = os.path.join(os.path.dirname(__file__) 
                             , "src"
                             , "docs"
                             , *rnames)
    return open(p).read()


version = "0.1"

long_description = (
    read('README.txt')
    + '\n' + 
    read('CHANGES.txt')
#    + '\n'  +
#    'Detailed Documentation\n'
#    '======================\n'
#    + '\n' +
#    read('src', 'buildout', 'removeaddledeggs', 'docu.txt')
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    read('TODOS.txt')
    + '\n' 

)

entry_point = 'buildout.removeaddledeggs:install'
entry_points = {"zc.buildout.extension": ["default = %s" % entry_point]}

setup(name='buildout.removeaddledeggs',
      version=version,
      description="Removes unneeded eggs automatically from file system",
      long_description=long_description,
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      license='GPL',
      keywords='buildout extension egg remove',
      author='Benjamin Hedrich',
      author_email='kiwisauce@pagenotfound.de',
      url='http://svn.plone.org/svn/collective/buildout/buildout.removeaddledeggs',
      packages=find_packages('src'),
      package_dir = {'':'src'},
      namespace_packages=['buildout'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'
                        ],
      entry_points=entry_points,
      )
