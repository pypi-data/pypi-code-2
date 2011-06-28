
__version__ = '0.8.2'

import re
from itertools import groupby
from ConfigParser import RawConfigParser, DEFAULTSECT, NoOptionError, NoSectionError, DuplicateSectionError
from string import Template as StringTemplate

import yaml

def merge(D1, D2):
    d = dict(D1)
    for k, v in D2.iteritems():
        if k in d and hasattr(v, 'keys'):
            v = merge(d[k], v)
        d[k] = v
    return d

def interpolate(val, context):
    if hasattr(val, 'iteritems'):
        newval = {}
        for k, v in val.iteritems():
            newval[k] = interpolate(v, context)
        return newval
    elif hasattr(val, '__iter__'):
        return [interpolate(x, context) for x in val]
    else:
        try:
            return StringTemplate(val).safe_substitute(context)
        except TypeError:
            return val

class DubbelParser(RawConfigParser):

    yaml_loader = yaml.loader.Loader
    subsection_divider = '->'

    def split_sectname(self, sectname):
        parent, divide, sectname = sectname.rpartition('.')
        return parent, sectname

    def __init__(self, defaults=None, section_defaults=None):
        RawConfigParser.__init__(self, defaults)
        if section_defaults:
            for k, v in section_defaults.iteritems():
                self.add_section(k, v)
        self._split = re.compile('\s*%s\s*' % self.subsection_divider).split

    def _parent_sections(self, section):
        parent, sectname = self.split_sectname(section)
        while parent:
            yield parent
            parent, sectname = self.split_sectname(parent)

    def add_section(self, section, vals=None):
        RawConfigParser.add_section(self, section)
        if vals:
            self._sections[section].update(vals)
        for parent in self._parent_sections(section):
            self._sections.setdefault(parent, {})

    def _read(self, fp, fname):
        sectname = DEFAULTSECT
        for m, g in groupby(fp, lambda line: self.SECTCRE.match(line)):
            if m:
                sectname = '.'.join(self._split(m.group('header')))
            else:
                content = '\n'.join(g)
                if not content.strip():
                    continue
                vals = yaml.load(content, Loader=self.yaml_loader)
                if sectname == DEFAULTSECT:
                    self._defaults.update(vals)
                else:
                    self.add_section(sectname, vals)

    def write(self, fp):
        if self._defaults:
            yaml.dump(self._defaults, fp, default_flow_style=False)
            fp.write("\n")
        for section in sorted(self._sections):
            vals = self._sections[section]
            if vals:
                header = (' %s ' % self.subsection_divider).join(section.split('.'))
                fp.write("[%s]\n" % header)
                yaml.dump(vals, fp, default_flow_style=False)
                fp.write("\n")

    def has_option(self, section, option):
        """Check for the existence of a given option in a given section."""
        if not section or section == DEFAULTSECT:
            option = self.optionxform(option)
            return option in self._defaults
        elif section not in self._sections:
            return False
        else:
            option = self.optionxform(option)
            if option in self._sections[section]:
                return True
            parent, sectname = self.split_sectname(section)
            return self.has_option(parent, option)

    def items(self, section=None):
        try:
            d2 = self._sections[section]
        except KeyError:
            if section not in ['', None, DEFAULTSECT, DEFAULTSECT.lower()]:
                raise NoSectionError(section)
            return self._defaults.items()
        d = self._defaults.copy()
        for parent in reversed(list(self._parent_sections(section))):
            d = merge(d, self._sections[parent])
        d = merge(d, d2)
        if "__name__" in d:
            del d["__name__"]
        return d.items()

    def options(self, section=None):
        """Return a list of option names for the given section name."""
        try:
            opts = self._sections[section].copy()
        except KeyError:
            if section not in ['', None, DEFAULTSECT, DEFAULTSECT.lower()]:
                raise NoSectionError(section)
            return self._defaults.keys()
        opts.update(self._defaults)
        for parent in self._parent_sections(section):
            opts.update(self._sections[parent])
        if '__name__' in opts:
            del opts['__name__']
        return opts.keys()

    def get(self, section, option):
        try:
            return RawConfigParser.get(self, section, option)
        except NoOptionError:
            for parent in self._parent_sections(section):
                return self.get(parent, option)
            raise NoOptionError(option, section)

    def subsections(self, mainsection):
        mainsection += '.'
        return [key for key in self._sections.iterkeys() if key.startswith(mainsection)]
        
    def nodes(self, parent=''):
        if parent and not parent.startswith('.'):
            parent += '.'
        previous = ''
        for key in reversed(sorted(k for k in self._sections.iterkeys() if k.startswith(parent))):
            if not previous.startswith(key):
                yield key, dict(self.items(key))
            previous = key
        if not previous:
            yield '', dict(self.items(''))

    def optionxform(self, optionstr):
        return optionstr

    # interpolation
    def fill(self, **context):
        """
        Return a new DubbelParser instance with the interpolated values
        """
        new_parser = DubbelParser()
        new_parser._defaults = self._get_interpolated_section('', context)
        for section in sorted(self._sections):
            new_parser._sections[section] = self._get_interpolated_section(section, context)
        return new_parser

    def _get_interpolated_section(self, section, context):
        if section == '':
            defaults = dict(self._defaults)
            defaults.update(context)
            return interpolate(defaults, defaults)
        else:
            raw = interpolate(self._sections[section], context)
            raw = interpolate(raw, raw)
            parent = section.rpartition('.')[0]
            return interpolate(raw, self._get_interpolated_section(parent, context))

class SafeDubbelParser(DubbelParser):

    yaml_loader = yaml.loader.SafeLoader


