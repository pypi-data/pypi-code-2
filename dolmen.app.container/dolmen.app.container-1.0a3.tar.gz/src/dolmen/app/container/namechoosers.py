# -*- coding: utf-8 -*-

import grok
from unicodedata import normalize
from dolmen.content import IBaseContent, IContainer
from zope.container.interfaces import INameChooser

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
            if IBaseContent.providedBy(object):
                name = object.title.strip()
                ascii = normalize('NFKD', name).encode('ascii', 'ignore')
                name = ascii.replace(' ', '_').lower()
            else:
                NotImplementedError(
                    """NormalizingNameChooser can't choose a name if the
                    parameter name is omited and if the component has no
                    adapter to INameFromTitle""")

        return self._findUniqueName(name, object)
