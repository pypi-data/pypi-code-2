#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni

from pydenji.resourceloader import ResourceAccessError
from pydenji.config.pythonconfig import Configuration
from pydenji.userproperties.mapping import inject_properties_from
from pydenji.userproperties.overrider import override_with
from pydenji.resourceloader import ReadResource, ResourceAccessError

# this is a quickly baked class which is highly prone to change in the future.
# don't rely on its API.

class QuickConfig(object):
    def __init__(self, prop_urls=(), override_urls=(), ignore_missing=True):
        self._prop_urls = prop_urls
        self._override_urls = override_urls
        self._ignore_missing = ignore_missing

    def __call__(self, config_cls):
        return self._get_injector()(self._get_overrider()(Configuration(config_cls)))

    def _get_injector(self):
        prop_resources = []
        for prop_url in self._prop_urls:
            try:
                resource = ReadResource(prop_url)
                prop_resources.append(resource)
            except ResourceAccessError:
                if not self._ignore_missing:
                    raise
        if not prop_resources:
            return lambda x: x
        return inject_properties_from(*prop_resources)

    def _get_overrider(self):
        override_resources = []
        for override_url in self._override_urls:
            try:
                resource = ReadResource(override_url)
                override_resources.append(resource)
            except ResourceAccessError:
                if not self._ignore_missing:
                    raise
        if not override_resources:
            return lambda x: x
        return override_with(*override_resources)
        

            


