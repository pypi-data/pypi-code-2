##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""UI for browsing database schema managers

$Id:$
"""
__docformat__ = 'restructuredtext'

import transaction

import zope.component
from zope.app.generations.interfaces import ISchemaManager
from zope.app.generations.interfaces import ISchemaManager
from zope.app.generations.generations import generations_key
from zope.app.generations.generations import Context
from zope.app.renderer.rest import ReStructuredTextToHTMLRenderer

from z3c.pagelet import browser
from z3c.template.template import getPageTemplate

request_key_format = "evolve-app-%s"


class Generations(browser.BrowserPagelet):
    """GEneration management page."""

    template = getPageTemplate()

    def _getdb(self):
        # TODO: There needs to be a better api for this
        return self.request.publication.db

    def evolve(self):
        """Perform a requested evolution."""

        self.managers = managers = dict(
            zope.component.getUtilitiesFor(ISchemaManager))
        db = self._getdb()
        conn = db.open()
        try:
            generations = conn.root().get(generations_key, ())
            request = self.request
            for key in generations:
                generation = generations[key]
                rkey = request_key_format % key
                if rkey in request:
                    manager = managers[key]
                    if generation >= manager.generation:
                        return {'app': key, 'to': 0}
                    context = Context()
                    context.connection = conn
                    generation += 1
                    manager.evolve(context, generation)
                    generations[key] = generation
                    transaction.commit()
                    return {'app': key, 'to': generation}
            return None
        finally:
            transaction.abort()
            conn.close()

    def applications(self):
        """Get information about database-generation status."""
        result = []
        db = self._getdb()
        conn = db.open()
        try:
            managers = self.managers
            generations = conn.root().get(generations_key, ())
            for key in generations:
                generation = generations[key]
                manager = managers.get(key)
                if manager is None:
                    continue

                result.append({
                    'id': key,
                    'min': manager.minimum_generation,
                    'max': manager.generation,
                    'generation': generation,
                    'evolve': (generation < manager.generation
                               and request_key_format % key
                               or ''
                               ),
                    })
            return result
        finally:
            conn.close()


class GenerationDetails(object):
    r"""Show Details of a particular Schema Manager's Evolvers

    This method needs to use the component architecture, so
    we'll set it up:
    
      >>> from zope.app.testing.placelesssetup import setUp, tearDown
      >>> setUp()
    
    We need to define some schema managers.  We'll define just one:
    
      >>> from zope.app.generations.generations import SchemaManager
      >>> from zope.app.testing import ztapi
      >>> app1 = SchemaManager(0, 3, 'zope.app.generations.demo')
      >>> ztapi.provideUtility(ISchemaManager, app1, 'foo.app1')

    Now let's create the view:

      >>> from zope.publisher.browser import TestRequest
      >>> details = ManagerDetails()
      >>> details.context = None
      >>> details.request = TestRequest(environ={'id': 'foo.app1'})

    Let's now see that the view gets the ID correctly from the request:

      >>> details.id
      'foo.app1'

    Now check that we get all the info from the evolvers:

      >>> info = details.getEvolvers()
      >>> for item in info:
      ...     print sorted(item.items())
      [('from', 0), ('info', u'<p>Evolver 1</p>\n'), ('to', 1)]
      [('from', 1), ('info', u'<p>Evolver 2</p>\n'), ('to', 2)]
      [('from', 2), ('info', ''), ('to', 3)]

    We'd better clean up:

      >>> tearDown()
    """

    id = property(lambda self: self.request['id'])

    def getEvolvers(self):
        id = self.id
        manager = zope.component.getUtility(ISchemaManager, id)

        evolvers = []

        for gen in range(manager.minimum_generation, manager.generation):

            info = manager.getInfo(gen+1)
            if info is None:
                info = ''
            else:
                # XXX: the renderer *expects* unicode as input encoding (ajung)
                renderer = ReStructuredTextToHTMLRenderer(
                    unicode(info), self.request)
                info = renderer.render()
                
            evolvers.append({'from': gen, 'to': gen+1, 'info': info})

        return evolvers
