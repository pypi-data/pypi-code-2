from zope.interface import classProvides
from zope.interface import implements

from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.utils import defaultMatcher

from Products.LinguaPlone.interfaces import ITranslatable
from Products.LinguaPlone.interfaces import ILanguageIndependentFields
from Products.LinguaPlone.public import AlreadyTranslated


class TranslationLinker(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.portal = transmogrifier.context

        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.canonicalkey = defaultMatcher(options, 'canonical-key', name,
                                           'canonicalTranslation')
        self.translationkey = defaultMatcher(options, 'translation-key', name,
                                             'translationOf')

    def __iter__(self):
        defered_links = []
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            if not pathkey:
                yield item; continue

            path = item[pathkey]
            if isinstance(path, unicode):
                path = path.encode('ascii')

            obj = self.portal.unrestrictedTraverse(path.lstrip('/'), None)
            if obj is None:
                yield item; continue

            canonicalkey = self.canonicalkey(*item.keys())[0]
            if canonicalkey and item[canonicalkey] == True:
                if ITranslatable.providedBy(obj):
                    obj.setCanonical()

            translationkey = self.translationkey(*item.keys())[0]
            if translationkey:
                canonicalpath = item[translationkey]
                canonical = self.portal.unrestrictedTraverse(canonicalpath.lstrip('/'), None)
                if canonical is None:
                    defered_links.append((path, canonicalpath))
                else:
                    if ITranslatable.providedBy(obj) and ITranslatable.providedBy(canonical):
                        try:
                            obj.addTranslationReference(canonical)
                        except AlreadyTranslated:
                            pass
                        ILanguageIndependentFields(canonical).copyFields(obj)

            yield item

        for path, canonicalpath in defered_links:
            obj = self.portal.unrestrictedTraverse(path.lstrip('/'), None)
            if obj is None:
                continue
            canonical = self.portal.unrestrictedTraverse(canonicalpath.lstrip('/'), None)
            if canonical is None:
                continue
            if ITranslatable.providedBy(obj) and ITranslatable.providedBy(canonical):
                try:
                    obj.addTranslationReference(canonical)
                except AlreadyTranslated:
                    pass
                ILanguageIndependentFields(canonical).copyFields(obj)
