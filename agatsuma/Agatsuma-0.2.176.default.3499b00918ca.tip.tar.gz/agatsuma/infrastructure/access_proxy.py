
class DictAccessProxy(object):
    def __init__(self, source_dict):
        object.__setattr__(self, '_DictAccessProxy__dict', source_dict)

    def __getattr__(self, name):
        stored_dict = object.__getattribute__(self, '_DictAccessProxy__dict')
        if name in stored_dict:
            return stored_dict[name]
        else:
            return object.__getattribute__(self, name)

    def __repr__(self):
        return str("<Dict proxy: %s>" % self.__dict)

class SettingsGroupProxy(DictAccessProxy):
    def __init__(self, source_dict, group_name, readonly_list, types, comments, update_callback):
        DictAccessProxy.__init__(self, source_dict)
        self.__readonly_list = readonly_list
        self.__groupName = group_name
        self.__types = types
        self.__comments = comments
        self.__update_callback = update_callback

    def __setattr__(self, name, value):
        sdict = object.__getattribute__(self, '_DictAccessProxy__dict')
        if name in sdict:
            if name in self.__readonly_list:
                raise Exception("Option '%s.%s' is read-only" % (self.__group_name, name))
            elif name in self.__types and type(value) != self.__types[name]:
                raise Exception("Option '%s.%s' must have type %s, but %s tried to assign" %
                                (self.__group_name,
                                 name,
                                 self.__types[name],
                                 type(value),
                                )
                               )
            else:
                sdict[name] = value # dict is reference to original dict
                self.__update_callback()
        else:
            object.__setattr__(self, name, value)

    def to_dict(self):
        ret = {}
        sdict = object.__getattribute__(self, '_DictAccessProxy__dict')
        ret.update(sdict)
        return ret
    
    def __repr__(self):
        return str("<Settings group '%s': %s>" % (self.__group_name, self.__dict))
