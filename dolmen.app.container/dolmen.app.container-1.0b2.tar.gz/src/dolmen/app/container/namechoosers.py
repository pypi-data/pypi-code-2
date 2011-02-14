# -*- coding: utf-8 -*-

import grokcore.component as grok
from unicodedata import normalize
from dolmen.content import IContainer
from zope.container.interfaces import INameChooser
from zope.dublincore.interfaces import IDCDescriptiveProperties

ATTEMPTS = 100


class NormalizingNameChooser(grok.Adapter):
    grok.context(IContainer)
    grok.implements(INameChooser)

    def checkName(self, name, object):
        return not name in self.context

    def _findUniqueName(self, name, object):
        if not name in self.context:
            return name

        idx = 1
        while idx <= ATTEMPTS:
            new_name = "%s_%d" % (name, idx)
            if not new_name in self.context:
                return new_name
            idx += 1

        raise ValueError(
            "Cannot find a unique name based on "
            "`%s` after %d attemps." % (name, ATTEMPTS))

    def chooseName(self, name, object):
        if not name:
            dc = IDCDescriptiveProperties(object, None)
            if dc is not None and dc.title:
                name = dc.title.strip()
                ascii = normalize('NFKD', name).encode('ascii', 'ignore')
                name = ascii.replace(' ', '_').lower()
            else:
                name = object.__class__.__name__.lower()

        return self._findUniqueName(name, object)
