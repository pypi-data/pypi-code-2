# vim:fileencoding=utf-8
# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
#
# This installation serves as an initial generation as we didn't have
# any before this one, so it also checks for "very" old databases and
# performs initial migration if necessary.

import zope.app.zopeappgenerations
import gocept.lms.app
import zc.relation.interfaces


def evolve(context):
    root = zope.app.zopeappgenerations.getRootFolder(context)
    for candidate in root.values():
        if not isinstance(candidate, gocept.lms.app.LMS):
            continue
        # Those are very old LMS which still use zc.relation. We go
        # through all the registered URLs and check their client
        # relations and transform them to the new way (TM).
        old_site = zope.app.component.hooks.getSite()
        zope.app.component.hooks.setSite(candidate)
        try:
            urls = zope.component.getUtility(
                    gocept.lms.interfaces.IURLProvider)
            references = zope.component.getUtility(
                    zc.relation.interfaces.ICatalog, name='url_refs')
            for url in urls.values():
                url.clients = set()
                token = references.tokenizeValues([url], 'client_urls').next()
                for client in references.findRelations({'client_urls': token}):
                    url.clients.add(client)
                zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(url))
            # Uninstall zc.relation catalog
            assert candidate.getSiteManager().unregisterUtility(
                references, zc.relation.interfaces.ICatalog, name='url_refs')
            assert candidate.getSiteManager()['Catalog-2'] == references
            del candidate.getSiteManager()['Catalog-2']
        finally:
            zope.app.component.hooks.setSite(old_site)
