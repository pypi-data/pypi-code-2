# -*- coding: utf-8 -*-
"""
aha.recipe.gae:app_lib
------------------------
Downloads libs from PyPi them into the application lib directory,
    extending appfy.recipe.gae:app_lib
The difference to the appfy.reciep.gae:app_lib is that it adds __init__.py 
 so that the directory works as a python package.
This module imports some modules from appfy.


Example
~~~~~~~

::

  [app_lib]
  recipe = aha.recipe.gae:app_lib
  lib-directory = app/lib
  use-zipimport = false

  # Define the libraries.
  eggs =
      tipfy

  # Don't copy files that match these glob patterns.
  ignore-globs =
      *.c
      *.pyc
      *.pyo
      */test
      */tests
      */testsuite
      */django
      */sqlalchemy

  # Don't install these packages or modules.
  ignore-packages =
      distribute
      setuptools
      easy_install
      site
      pkg_resources
"""
import os

from appfy.recipe.gae import app_lib


BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(os.path.realpath(__file__))))))


class Recipe(app_lib.Recipe):

    def install_in_app_dir(self, paths):
        # call the same method of the super class.
        super(Recipe, self).install_in_app_dir(paths)
        # make __init__.py explicitry.
        open(os.path.join(self.lib_path, '__init__.py'), 'w')
