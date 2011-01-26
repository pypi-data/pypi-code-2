
from Products.ZCTextIndex import PipelineFactory


class OrderedMapping(dict):

    def __init__(self):
        dict.__init__(self)
        self.__order = []

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        if key not in self.__order:
            self.__order.append(key)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.__order.remove(key)

    def keys(self):
        return list(self.__order)


class PipelineElementFactory(PipelineFactory.PipelineElementFactory):

    def __init__(self):
        self._groups = OrderedMapping()

    def registerFactory(self, group, name, factory):
        if self._groups.has_key(group) and \
           self._groups[group].has_key(name):
            raise ValueError('ZCTextIndex lexicon element "%s" '
                             'already registered in group "%s"'
                             % (name, group))

        elements = self._groups.get(group)
        if elements is None:
            elements = self._groups[group] = OrderedMapping()
        elements[name] = factory

    def getFactoryGroups(self):
        return self._groups.keys()

    def getFactoryNames(self, group):
        return self._groups[group].keys()


element_factory = PipelineElementFactory()

