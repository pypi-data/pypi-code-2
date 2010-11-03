"""
Core property implementations.
"""

import basemodel

"""
Model Property Types
"""

class Property(object):
    """
    Descriptor for model properties (to be included in the class declaration).
    """
    def __init__(self, proptype, default=None, **kwargs):
        self._proptype = proptype
        self._metadata = kwargs
        self._metadata["default"] = default
        self._metadata["type"] = proptype
        if issubclass(proptype, basemodel.SubscribableModel):
            self._reference = True
            self._prevval = None
        else:
            self._reference = False
        # self.name = None # XXX has to be set externally !!

    def __getattr__(self, name):
        try:
            return self._metadata[name]
        except:
            return None

    def __set__(self, obj, val):
        if self._reference and not isinstance(val, str):
            prevval = None
            if len(obj._references[self.name]):
                prevval = obj._references[self.name][0]
            if val:
                # unref and unsubscribe previous
                if prevval:
                    obj._references[self.name].remove(prevval)
                    prevval._referencedby[self.name].remove(obj)
                obj._references[self.name].append(val)
                val._referencedby[self.name].append(obj)
            elif prevval:
                if self.persistent:
                    return # keep it!
                obj._references[self.name].remove(prevval)
                prevval._referencedby[self.name].remove(obj)
        obj.setProperty(self.name, val)

    def invalidate(self):
        pass

    def __get__(self, obj, objtype=None):
        if not obj:  # class access
            return self
        else: # instance access
            try:
                return obj.getProperty(self.name)
            except:
                return self.default


class Color(Property):
    def __init__(self, default=[0,0,0], **kwargs):
        Property.__init__(self, list, default, **kwargs)

class Color4(Property):
    def __init__(self, default=[0,0,0,0], **kwargs):
        Property.__init__(self, list, default, **kwargs)

class Vector2(Property):
    def __init__(self, default=[0,0], **kwargs):
        Property.__init__(self, list, default, **kwargs)

class Vector3(Property):
    def __init__(self, default=[0,0,0], **kwargs):
        Property.__init__(self, list, default, **kwargs)

class Vector4(Property):
    def __init__(self, default=[0,0,0,1], **kwargs):
        Property.__init__(self, list, default, **kwargs)

class SingleChoice(Property):
    def __init__(self, proptype=str, default="", options=[], **kwargs):
        Property.__init__(self, proptype, default, **kwargs)
        self._options = options

class PropertyFrom(Property):
    def __init__(self, default="", **kwargs):
        Property.__init__(self, str, default, **kwargs)

class Link(Property):
    def __init__(self, *args, **kwargs):
        Property.__init__(self, str, *args, **kwargs)

class Date(Property):
    def __init__(self, *args, **kwargs):
        Property.__init__(self, float, *args, **kwargs)

class DateTime(Property):
    def __init__(self, *args, **kwargs):
        Property.__init__(self, float, *args, **kwargs)

class Password(Property):
    def __init__(self, default="", **kwargs):
        Property.__init__(self, str, default, **kwargs)

class File(Property):
    def __init__(self, options=[], default="", *args, **kwargs):
        Property.__init__(self, str, default, *args, **kwargs)
        self._options = options

