#!/usr/bin/env python

import os
import sys
import urllib2

from odict import OrderedDict
from ConfigParser import ConfigParser
from ConfigParser import InterpolationMissingOptionError
from ConfigParser import MissingSectionHeaderError
from ConfigParser import NoOptionError
from StringIO import StringIO

def file_pointer(resource):
    """returns a file-like object given a string"""
    # XXX could go in utils.py 

    if not isinstance(resource, basestring):
        # assume resource is already a file-like object
        return resource

    if os.path.exists(resource):
        return file(resource)
    if sum([resource.startswith(http) for http in 'http://', 'https://']):
        return urllib2.urlopen(resource)
    return StringIO(resource)


class ConfigMunger(ConfigParser):
    """combine configuration from .ini files"""
    
    def __init__(self, *conf, **kw):
        ConfigParser.__init__(self, defaults=kw.get('defaults',{}),
                              dict_type=OrderedDict)
        self.optionxform = str
        self.read(*conf)
    
    def __getitem__(self, section):
        """
        return an object with __getitem__ defined appropriately
        to allow referencing like self['foo']['bar']
        """
        return dict(self.items(section))

    def get(self, section, option, default=None, raw=False, vars=None):
        try:
            value = ConfigParser.get(self, section, option, raw, vars)
        except NoOptionError:
            return default
        return value

    def set(self, section, option, value):
        if section not in self.sections():
            self.add_section(section)
        ConfigParser.set(self, section, option, value)

    def move_section(self, section, newname):
        if self.has_section(section):
            _section = self[section]
            self.remove_section(section)
        else:
            _section = {}
        self.read({newname: _section})
    
    def dict(self):
        """return a dictionary of dictionaries; 
        the outer with keys of section names;
        the inner with keys, values of the section"""
        return dict([(section, self[section])
                     for section in self.sections()])

    def read(self, *ini):
        for _ini in ini:
            if isinstance(_ini, dict):
                for section, contents in _ini.items():
                    for option, value in contents.items():
                        self.set(section, option, value)
            elif isinstance(_ini, list) or isinstance(_ini, tuple):

                # ensure list or tuple of 3-tuples
                assert len([option for option in _ini
                            if isinstance(option, tuple) 
                            and len(option) == 3])

                for section, option, value in _ini:
                    self.set(section, option, value)                
            else:
                fp = file_pointer(_ini)
                try:
                    self.readfp(fp)
                except MissingSectionHeaderError:
                    fp.seek(0)
                    fp = StringIO("[DEFAULTS]\n" + fp.read())
                    self.readfp(fp)
            
    def missing(self):
        """returns missing variable names"""
        missing = set()        

        for section in self.sections():
            for key, val in self.items(section, raw=True):
                try:
                    self.get(section, key)
                except InterpolationMissingOptionError, e:
                    missing.add(e.reference)
        return missing

    def tuples(self):
        """
        return options in format appropriate to trac:
        [ (section, option, value) ]
        """
        options = []
        for section in self.sections():
            options.extend([(section,) + item 
                            for item in self.items(section)])
        return options

    def write(self, fp=sys.stdout, raw=False, sorted=True, vars=None):
        sections = self.sections()
        if sorted:
            sections.sort()

        for section in sections:
            print >> fp, '[%s]' % section
            options = self.options(section)
            if sorted:
                options.sort()
            for option in options:
                print >> fp, "%s = %s" % (option, self.get(section, option, raw=raw, vars=vars))
            if section != sections[-1]:
                print >> fp

if __name__ == '__main__':
    import sys
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--missing', action="store_true", default=False,
                      help="list missing template variables")
    munger = ConfigMunger()
    options, args = parser.parse_args()
    munger.read(*args)
    if options.missing:
        for missing in munger.missing():
            print missing
    else:
        munger.write(sys.stdout)
