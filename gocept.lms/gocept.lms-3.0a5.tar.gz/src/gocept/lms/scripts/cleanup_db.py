# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import transaction
import zope.app.component.hooks
import zope.component

import gocept.lms.interfaces


lms = root['lms']
zope.app.component.hooks.setSite(lms)

bad_urls = set()

urls = zope.component.getUtility(gocept.lms.interfaces.IURLProvider)
for key, url in urls.items():
    handler = gocept.lms.interfaces.ISchemeHandler(url.url, None)
    if not(handler and handler.allow(url.url)):
        bad_urls.add(url.url)

for url in bad_urls:
    transaction.begin()
    urls = zope.component.getUtility(gocept.lms.interfaces.IURLProvider)
    url = urls.get_url(url)
    print url.url
    for client in url.clients:
        client.unregister_urls([url])
    del url.__parent__[url.__name__]
    transaction.commit()
