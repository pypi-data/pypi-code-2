import os
import ConfigParser
from zope.interface import implements
from z3c.appconfig.interfaces import IAppConfig

def checkInitialised(func):
    def wrapper(self, *args, **kw):
        if not self._initialized:
            config=os.environ.get("APPCONFIG")
            if config:
                self.loadConfig(config)
            self._initialized=True
        return func(self, *args, **kw)
    return wrapper


class AppConfig(dict):
    implements(IAppConfig)

    _initialized = False

    def loadConfig(self, input, clear=False):
        parser=ConfigParser.SafeConfigParser()
        if isinstance(input, basestring):
            input=open(input)
        parser.readfp(input)

        if clear:
            dict.clear(self)

        for section in parser.sections():
            for (name, value) in parser.items(section):
                dict.setdefault(self, section, {})[name]=value

    # Wrap access methods to make sure environment config is loaded last
    __contains__ = checkInitialised(dict.__contains__)
    __iter__ = checkInitialised(dict.__iter__)
    __len__ = checkInitialised(dict.__len__)
    __repr__ = checkInitialised(dict.__repr__)
    __str__ = checkInitialised(dict.__str__)
    __sizeof__ = checkInitialised(dict.__sizeof__)
    copy = checkInitialised(dict.copy)
    get = checkInitialised(dict.get)
    has_key = checkInitialised(dict.has_key)
    items = checkInitialised(dict.items)
    iteritems = checkInitialised(dict.iteritems)
    iterkeys = checkInitialised(dict.iterkeys)
    itervalues = checkInitialised(dict.itervalues)
    keys = checkInitialised(dict.keys)
    values = checkInitialised(dict.values)

    # Disable any modifications
    def __setitem__(self, *args, **kw):
        raise NotImplementedError
    __delitem__= __setitem__
    clear = __setitem__
    pop = __setitem__
    popitem = __setitem__
    setdefault = __setitem__
    update = __setitem__

