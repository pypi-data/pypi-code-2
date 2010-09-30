# -*- coding: utf-8 -*-
""" build_mo command
"""
import os
from os.path import join
from setuptools import Command
try:
    from msgfmt import Msgfmt
except:
    from collective.releaser.msgfmt import Msgfmt

from collective.releaser.base import display

class build_mo(Command):
    """Msgfmt"""
    description = "Build msgfmt .mo files from their .po sources"
    user_options = []

    def initialize_options(self):
        """init options"""
        pass

    def finalize_options(self):
        """finalize options"""
        pass

    def run(self):
        """runner"""
        self.find_locales(os.getcwd())

    def find_locales(self, path):
        """find 'locales' directories and compiles .po files
        note: Django uses 'locale' (singular form)
        """
        for directory in os.listdir(path):
            dir_path = join(path, directory)
            if not os.path.isdir(dir_path):
                continue

            if directory in ('locales', 'locale'):
                self.compile_po(dir_path)
            else:
                self.find_locales(dir_path)

    def compile_po(self, path):
        """path is a locales directory, find ??/LC_MESSAGES/*.po and compiles
        them into .mo
        """
        for language in os.listdir(path):
            lc_path = join(path, language, 'LC_MESSAGES')
            if os.path.isdir(lc_path):
                for domain_file in os.listdir(lc_path):
                    if domain_file.endswith('.po'):
                        file_path = join(lc_path, domain_file)
                        display("Building .mo for %s" % file_path)
                        mo_file = join(lc_path, '%s.mo' % domain_file[:-3])
                        mo_content = Msgfmt(file_path, name=file_path).get()
                        mo = open(mo_file, 'wb')
                        mo.write(mo_content)
                        mo.close()

