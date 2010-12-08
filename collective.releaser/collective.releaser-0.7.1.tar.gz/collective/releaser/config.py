# -*- coding: utf-8 -*-
import os
import ConfigParser
from StringIO import StringIO
from distutils.dist import Distribution

_marker = object()

class MultiConfig(dict):

    def __init__(self, files=None):
        if files is None:
            return
        for f in files:
            if not os.path.isfile(f):
                continue
            self._update(self._ini_to_dict(f))

    def _update_section(self, s1, s2):
        for k, v in s2.items():
            if k.endswith('+'):
                key = k.rstrip(' +')
                s2[key] = "\n".join(s1.get(key, "").split('\n') +
                        s2[k].split('\n'))
                del s2[k]
            elif k.endswith('-x'):
                key = k.rstrip(' -')
                s2[key] = "\n".join([v for v in s1.get(key, "").split('\n')
                                    if v not in s2[k].split('\n')])
                del s2[k]
        s1.update(s2)
        return s1

    def _update(self, other):
        for section in other:
            if section in self:
                self[section] = self._update_section(self[section],
                                                     other[section])
            else:
                self[section] = other[section]

    def _ini_to_dict(self, filename):
        fp = open(filename)
        base = os.path.dirname(filename)
        result = {}
        parser = ConfigParser.RawConfigParser()
        parser.optionxform = lambda s: s
        parser.readfp(fp)
        for section in parser.sections():
            options = dict(parser.items(section))
            result[section] = options
        return result

    def get_option(self, section, option, default=_marker):
        section = self.get_section(section)
        try:
            return section[option]
        except KeyError, e:
            if default is _marker:
                raise
            else:
                return default

    def get_section(self, section):
        return self[section]

    def get_sections(self):
        return self.keys()

    def get_options(self, section):
        return self.get_section(section).keys()


class DistutilsMultiConfig(MultiConfig):

    def __init__(self, files=None):

        home = os.path.expanduser('~')
        dist = Distribution()
        pypirc = os.path.join(home, '.pypirc')
        pypirc2 = os.path.join(home, 'pypirc')
        files = [pypirc, pypirc2] + dist.find_config_files()
        super(DistutilsMultiConfig, self).__init__(files)


