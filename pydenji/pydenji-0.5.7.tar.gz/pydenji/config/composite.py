#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni

from pydenji.config.pythonconfig import is_object_factory, dontconfigure
from pydenji.appcontext.aware import is_appcontext_aware

class NamingClashException(Exception):
    def __init__(self, clashing_attr, last_config):
        super(NamingClashException, self).__init__(
            "Name '%s' was configured multiple times, last in %s" % (
            clashing_attr, last_config)
        )

class CompositeConfig(object):
    def __init__(self, configs):
        # this resembles appcontext method.
        # TODO: check whether we could refactor it someway.
        # TODO: cyclomatic complexity is increasing dramatically in this method.
        # we'll need to split it into smaller pieces someday.
        for config in configs:
            for attr in dir(config):
                value = getattr(config, attr)
                if is_object_factory(value):
                    if not attr.startswith("_"):
                        # public factory, check for naming clashes.
                        if getattr(self, attr, None) is not None:
                            # TODO: it would probably be good to know
                            # where it was configured.
                            raise NamingClashException(attr, config)
                        setattr(self, attr, value)
                    else:
                        # private factory, prevent naming clashes.
                        # TODO: maybe we could just make them random or sequential?
                        setattr(self, "_pydenji__%s_%s" % (config.__class__.__name__, attr), value)

        # retain reference in order to set app context.
        self._pydenji__CONFIGURATIONS = configs

    @dontconfigure
    def set_app_context(self, context):
        for config in self._pydenji__CONFIGURATIONS:
            if is_appcontext_aware(config):
                    config.set_app_context(context)



    
    