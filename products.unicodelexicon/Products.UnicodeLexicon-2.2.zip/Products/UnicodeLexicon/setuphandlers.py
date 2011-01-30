
from zope.component import queryMultiAdapter
from Products.GenericSetup.utils import parseString
from Products.GenericSetup.utils import ExpatError
from Products.GenericSetup.interfaces import IBody

from Products.CMFCore.utils import getToolByName
from Products.UnicodeLexicon.lexicon import UnicodeLexicon

class _extra(object):
    pass


class ZCTextIndexSetup(object):
    """Updates ZCTextIndexes to use Unicode aware lexicons
    """

    def __init__(self, catalog, context):
        self.indexes = []
        self.catalog = catalog
        self.context = context

    def run(self):
        self._readConfig()
        self._setupIndexes()

    def _readConfig(self):
        """Reads ZCTextIndex configuration from catalog.xml
        """
        importer = queryMultiAdapter((self.catalog, self.context), IBody)
        if importer is not None:
            filename = '%s%s' % (importer.name, importer.suffix)
            body = self.context.readDataFile(filename)
            if body is not None:
                try:
                    dom = parseString(body)
                except ExpatError, e:
                    raise ExpatError('%s: %s' % (filename, e))

                node = dom.documentElement
                for child in node.childNodes:
                    if child.nodeName != 'index':
                        continue
                    if child.hasAttribute('deprecated'):
                        continue

                    index_name = str(child.getAttribute('name'))
                    index_type = str(child.getAttribute('meta_type'))

                    if index_type != 'ZCTextIndex':
                        continue

                    extra = _extra()
                    for sub in child.childNodes:
                        if sub.nodeName == 'extra':
                            name = str(sub.getAttribute('name'))
                            value = str(sub.getAttribute('value'))
                            setattr(extra, name, value)
                        elif sub.nodeName == 'indexed_attr':
                            value = str(sub.getAttribute('value'))
                            setattr(extra, 'doc_attr', value)
                    if not extra.__dict__:
                        extra = None

                    self.indexes.append((index_name, index_type, extra))

    def _setupIndexes(self):
        """Sets up ZCTextIndexes

        Indexes will be replaced and reindexed if necessary.
        """
        added_indexes = []

        for name, type, extra in self.indexes:
            try:
                index = self.catalog._catalog.getIndex(name)
            except KeyError:
                pass
            else:
                indextype = index.__class__.__name__
                if indextype == type:
                    lexicon = index.getLexicon()
                    if (isinstance(lexicon, UnicodeLexicon) and
                        lexicon.getId() == extra.lexicon_id):
                        continue
                self.catalog.delIndex(name)

            self.catalog.addIndex(name, type, extra=extra)
            added_indexes.append(name)

        if len(added_indexes) and len(self.catalog):
            self.catalog.manage_reindexIndex(added_indexes, self.catalog.REQUEST)


def importUnicodeLexicon(context):
    site = context.getSite()
    logger = context.getLogger('unicodelexicon')
    catalog = getToolByName(site, 'portal_catalog', None)

    if catalog is None or context.readDataFile('unicodelexicon.txt') is None:
        logger.info('Nothing to import.')
        return

    ZCTextIndexSetup(catalog, context).run()
    logger.info('Unicode lexicon imported.')

