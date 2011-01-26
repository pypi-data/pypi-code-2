
from BTrees.OIBTree import OIBTree
from BTrees.IOBTree import IOBTree
from BTrees.Length import Length

from Products.GenericSetup.utils import NodeAdapterBase

from Products.UnicodeLexicon.interfaces import IUnicodeLexicon
from Products.UnicodeLexicon.pipelinefactory import element_factory


class UnicodeLexiconNodeAdapter(NodeAdapterBase):
    """Node im- and exporter for ZCTextIndex Unicode Lexicon"""

    # BBB: Zope 2.8
    # Should be zope.component.adapts(IUnicodeLexicon)
    __used_for__ = IUnicodeLexicon

    _LOGGER_ID = name = 'unicodelexicon'

    def _exportNode(self):
        """Export the object as a DOM node."""
        node = self._getObjectNode('object')
        for element in self.context._pipeline:
            group, name = self._getKeys(element)
            child = self._doc.createElement('element')
            child.setAttribute('group', group)
            child.setAttribute('name', name)
            node.appendChild(child)
        #self._logger.info('%r exported.' % self.context.getId())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node."""
        pipeline = []
        for child in node.childNodes:
            if child.nodeName == 'element':
                element = element_factory.instantiate(
                      child.getAttribute('group').encode('utf-8'),
                      child.getAttribute('name').encode('utf-8'))
                pipeline.append(element)
        self.context._pipeline = tuple(pipeline)
        # Clear lexicon
        self.context._wids = OIBTree()
        self.context._words = IOBTree()
        self.context.length = Length()
        #self._logger.info('%r imported.' % self.context.getId())

    node = property(_exportNode, _importNode)

    def _getKeys(self, element):
        for group in element_factory.getFactoryGroups():
            for name, factory in element_factory._groups[group].items():
                if factory == element.__class__:
                    return group, name

