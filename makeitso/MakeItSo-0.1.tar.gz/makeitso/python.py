#!/usr/bin/env python

"""
python package templates for makeitso

Several components are included.
[TODO] You may use these subtemplates in any combination.

* README.txt : a README in restructured text
* examples : examples for your package
* setup.py : setup utility for the full package
* ./main.py : CLI handler for your webapp
* ./model.py : model of a persisted object
* ./template.py : a MakeItSo template for project creation
* ./tests : doctest suite for the package
* ./web.py : a webob web handler
"""

import sys
from cli import MakeItSoCLI
from optparse import OptionParser
from template import MakeItSoTemplate

class PythonPackageTemplate(MakeItSoTemplate):
  """
  python package template
  """
  name = 'python-package'
  templates = ['python_package']
  look = True

  # things that go in setup.py
  dependencies = {'web.py': ['webob'],
                  'template.py': ['MakeItSo']}
  console_scripts = {'main.py': '{{project}}.main:main',
                     'template.py': '{{project}}.template:main'
                     }
  
  def __init__(self, **kw):
    MakeItSoTemplate.__init__(self, **kw)

class PythonPackageCLI(MakeItSoCLI):
  """
  CLI front end for the python package template
  """

def main(args=sys.argv[1:]):
  cli = PythonPackageCLI(PythonPackageTemplate)
  cli(*args)

if __name__ == '__main__':
  main()  
