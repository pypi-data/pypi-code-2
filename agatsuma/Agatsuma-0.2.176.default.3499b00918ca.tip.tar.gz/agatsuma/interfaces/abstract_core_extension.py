# -*- coding: utf-8 -*-

from agatsuma.adaptations.abclasses import ABCStrictMetaVerbose, durable_abstractmethod

class AbstractCoreExtension(object):
    __metaclass__ = ABCStrictMetaVerbose

    def init(self, core, app_directories, appConfig, kwargs):
        return (app_directories, appConfig, kwargs)

    @durable_abstractmethod
    @staticmethod
    def name():
        pass

    def additional_methods(self):
        return []

    def on_core_post_configure(self, core):
        pass

    def on_core_stop(self, core):
        pass

