#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.
from inspect import getabsfile
from compiler import parseFile
from configobj import ConfigObj, Section

from pydenji.userproperties.properties import UserProperties
from pydenji.userproperties.codescraper import get_getitem_accesses
from pydenji._aop.intercept import intercept


_NO_VALUE = object()

def _get_mapping_types():
    # this is not exactly nice...
    mapping_types = [dict]
    try:
        from collections import Mapping
        mapping_types.append(Mapping)
    except:
        pass

    from UserDict import UserDict, DictMixin
    mapping_types.append(UserDict)
    mapping_types.append(DictMixin)

    return tuple(mapping_types)


def map_properties_to_obj(d, obj, map_nonexistent=False):
    for key, value in d.iteritems():
        # TODO: this is a simple check, what if "value" is a method?
        if (getattr(obj, key, _NO_VALUE) is _NO_VALUE) and not map_nonexistent:
            raise ValueError, "Object '%s' hasn't got a '%s' attribute" % (obj, key)
        setattr(obj, key, value)
    return obj

#TODO: think about a real use case for this class :-/ we might just kill it.
class ConfigObjPropertyMapper(object):
    def __init__(self, configobj_source):
        self._co = ConfigObj(configobj_source, unrepr=True)

    def __call__(self, config_cls):
        # FIXME: we'll need a utility "aop" function to intercept calls.
        original_init = config_cls.__init__
        def new_init(new_self, *args, **kwargs):
            original_init(new_self, *args, **kwargs)
            # TODO: should we let the config name to be set explicitly?
            # TODO: name is changed by our decorator right now, maybe it shouldn't.
            map_properties_to_obj(self._co[config_cls.__name__], new_self)
            
        config_cls.__init__ = new_init
        return config_cls

# TODO: this might force property redefinition. We might think about
# a "global" namespace where each and every property is globally defined,
# and might be overriden later.
class inject_properties_from(object):
    def __init__(self, base_co_src, *other_co_srcs, **kwargs):
        self._co = ConfigObj(base_co_src, unrepr=True)
        for other_src in other_co_srcs:
            self._co.merge(ConfigObj(other_src, unrepr=True))
        self._target = kwargs.pop("target_kwarg", "props")
        
    def __call__(self, config_cls):
        original_init = config_cls.__init__
        def new_init(new_self, *args, **kwargs):
            # do we need to do something like an override?
            if self._target in kwargs:
                raise ValueError, "'%s' kw args was supplied already!"
            props = UserProperties(self._get_config_dict_for(config_cls.__name__))
            kwargs[self._target] = props
            original_init(new_self, *args, **kwargs)
            self._verify_no_missing_property(new_self, props, self._target)


        config_cls.__init__ = new_init
        return config_cls

    def _verify_no_missing_property(self, config_instance, props, attr):
        difference = set(get_getitem_accesses(config_instance, attr)).difference(set(props.keys()))
        if difference:
            raise ValueError, "Some property is missing: %s" % " ".join(difference)

    def _get_config_dict_for(self, section_name):
        # we want global_dict to be a ConfigObj section in order to support merging.
        global_dict = self._co.get("global", ConfigObj(["[global]"])["global"])
        if not isinstance(global_dict, Section):
            raise TypeError, "'%s' must be a section header" % "global"

        config_dict = self._co.get(section_name, {})
        if not isinstance(config_dict, _get_mapping_types()):
            raise TypeError, "'%s' must be a section header or dict." % section_name
        global_dict.merge(config_dict)
        return global_dict





        










