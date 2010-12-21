# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

# config exceptions
class ConfigAttributeMissing(Exception):
    def __init__(self, section, attribute):
        self.section = section
        self.attribute = attribute
        Exception.__init__(self, self.__repr__())

    def __call__(self, section, attribute):
        self.__init__(section, attribute)
                
    def __repr__(self):
        return 'Section: "%s", attribute: "%s" is missing' % (self.section, self.attribute)

# worker exceptions
class WorkerNotConfigured(Exception): pass
class WorkerTimeout(Exception): pass

