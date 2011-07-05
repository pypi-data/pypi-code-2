from agatsuma.adaptations.abclasses import ABCMeta, abstractmethod

class AbstractSettingsProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def load(self, serialized_settings):
        pass

    @abstractmethod
    def dump(self, settings):
       pass
