from unittest import TestCase, defaultTestLoader, main
from zope.component import provideUtility, getGlobalSiteManager
from zope.publisher.browser import TestRequest
from collective.solr.tests.utils import getData
from collective.solr.interfaces import ISolrConnectionConfig
from collective.solr.manager import SolrConnectionConfig
from collective.solr.parser import SolrResponse
from collective.solr.browser.facets import SearchFacetsView
from collective.solr.browser.facets import facetParameters, convertFacets
from urllib import unquote


class Dummy(object):
    """ dummy class that allows setting attributes """

    def __init__(self, **kw):
        self.__dict__.update(kw)


class FacettingHelperTest(TestCase):

    def testConvertFacets(self):
        fields = dict(portal_type=dict(Document=10,
            Folder=3, Event=5, Topic=2))
        info = convertFacets(fields)
        # the info should consist of 1 dict with `field` and `counts` keys
        self.assertEqual([sorted(i) for i in info], [['counts', 'title']] * 1)
        # next let's check the field names
        self.assertEqual([i['title'] for i in info], ['portal_type'])
        # and the fields contents
        types, = info
        self.assertEqual(types['title'], 'portal_type')
        self.assertEqual([(c['name'], c['count']) for c in types['counts']], [
            ('Document', 10),
            ('Event', 5),
            ('Folder', 3),
            ('Topic', 2),
        ])

    def testConvertFacetResponse(self):
        response = SolrResponse(getData('facet_xml_response.txt'))
        fields = response.facet_counts['facet_fields']
        info = convertFacets(fields)
        # the info should consist of 2 dicts with `field` and `counts` keys
        self.assertEqual([sorted(i) for i in info], [['counts', 'title']] * 2)
        # next let's check the field names
        self.assertEqual([i['title'] for i in info], ['cat', 'inStock'])
        # and the fields contents
        cat, inStock = info
        self.assertEqual(cat['title'], 'cat')
        self.assertEqual([(c['name'], c['count']) for c in cat['counts']], [
            ('search', 1),
            ('software', 1),
            ('electronics', 0),
            ('monitor', 0),
        ])
        self.assertEqual(inStock['title'], 'inStock')
        self.assertEqual([(c['name'], c['count']) for c in inStock['counts']], [
            ('true', 1),
        ])

    def testFacetParameters(self):
        context = Dummy()
        request = {}
        # with nothing set up, no facets will be returned
        self.assertEqual(facetParameters(context, request), ([], {}))
        # setting up the regular config utility should give the default value
        cfg = SolrConnectionConfig()
        provideUtility(cfg, ISolrConnectionConfig)
        self.assertEqual(facetParameters(context, request), ([], {}))
        # so let's set it...
        cfg.facets = ['foo']
        self.assertEqual(facetParameters(context, request), (['foo'], {}))
        # override the setting on the context
        context.facet_fields = ['bar']
        self.assertEqual(facetParameters(context, request), (['bar'], {}))
        # and again via the request
        request['facet.field'] = ['foo', 'bar']
        self.assertEqual(facetParameters(context, request),
            (['foo', 'bar'], {}))
        # clean up...
        getGlobalSiteManager().unregisterUtility(cfg, ISolrConnectionConfig)

    def testFacetDependencies(self):
        context = Dummy()
        request = {}
        cfg = SolrConnectionConfig()
        provideUtility(cfg, ISolrConnectionConfig)
        # dependency info can be set via the configuration utility...
        cfg.facets = ['foo:bar']
        self.assertEqual(facetParameters(context, request),
            (['foo:bar'], dict(foo=['bar'])))
        # overridden on the context
        context.facet_fields = ['bar:foo']
        self.assertEqual(facetParameters(context, request),
            (['bar:foo'], dict(bar=['foo'])))
        # and via the request
        request['facet.field'] = ['foo:bar', 'bar:foo']
        self.assertEqual(facetParameters(context, request),
            (['foo:bar', 'bar:foo'], dict(foo=['bar'], bar=['foo'])))
        # white space shouldn't matter
        request['facet.field'] = ['foo : bar', 'bar  :foo']
        self.assertEqual(facetParameters(context, request),
            (['foo : bar', 'bar  :foo'], dict(foo=['bar'], bar=['foo'])))
        # clean up...
        getGlobalSiteManager().unregisterUtility(cfg, ISolrConnectionConfig)

    def testFacetLinks(self):
        context = Dummy(facet_fields=['portal_type'])
        request = {'foo': 'bar'}
        fields = dict(portal_type=dict(Document=10, Folder=3, Event=5))
        info = convertFacets(fields, context, request)
        # let's check queries for the one and only facet field
        self.assertEqual(len(info), 1)
        counts = info[0]['counts']
        self.assertEqual(len(counts), 3)
        params = lambda query: sorted(map(unquote, query.split('&')))
        self.assertEqual(counts[0]['name'], 'Document')
        self.assertEqual(params(counts[0]['query']), [
            'foo=bar', 'fq=portal_type:"Document"'])
        self.assertEqual(counts[1]['name'], 'Event')
        self.assertEqual(params(counts[1]['query']), [
            'foo=bar', 'fq=portal_type:"Event"'])
        self.assertEqual(counts[2]['name'], 'Folder')
        self.assertEqual(params(counts[2]['query']), [
            'foo=bar', 'fq=portal_type:"Folder"'])

    def testFacetLinksWithSelectedFacet(self):
        context = Dummy()
        request = {'foo': 'bar', 'facet.field': 'bar'}
        fields = dict(foo=dict(private=2, published=4))
        info = convertFacets(fields, context, request)
        self.assertEqual(len(info), 1)
        counts = info[0]['counts']
        self.assertEqual(len(counts), 2)
        params = lambda query: sorted(map(unquote, query.split('&')))
        self.assertEqual(counts[0]['name'], 'published')
        self.assertEqual(params(counts[0]['query']), [
            'facet.field=bar', 'foo=bar', 'fq=foo:"published"'])
        self.assertEqual(counts[1]['name'], 'private')
        self.assertEqual(params(counts[1]['query']), [
            'facet.field=bar', 'foo=bar', 'fq=foo:"private"'])

    def testFacetLinksWithMultipleFacets(self):
        context = Dummy()
        request = {'facet.field': ['foo', 'bar']}
        fields = dict(foo=dict(Document=10, Folder=3, Event=5),
            bar=dict(private=2, published=4))
        info = convertFacets(fields, context, request)
        self.assertEqual(len(info), 2)
        # check the facets for 'bar'
        bars = info[1]['counts']
        self.assertEqual(len(bars), 2)
        params = lambda query: sorted(map(unquote, query.split('&')))
        self.assertEqual(params(bars[0]['query']), [
            'facet.field=foo', 'fq=bar:"published"'])
        self.assertEqual(params(bars[1]['query']), [
            'facet.field=foo', 'fq=bar:"private"'])
        # and also the one for 'foo'
        foos = info[0]['counts']
        self.assertEqual(len(foos), 3)
        self.assertEqual(params(foos[0]['query']), [
            'facet.field=bar', 'fq=foo:"Document"'])
        self.assertEqual(params(foos[1]['query']), [
            'facet.field=bar', 'fq=foo:"Event"'])
        self.assertEqual(params(foos[2]['query']), [
            'facet.field=bar', 'fq=foo:"Folder"'])

    def testFacetLinksWithMultipleSelectedFacets(self):
        context = Dummy()
        request = {'facet.field': 'foo', 'fq': 'bar:private'}
        fields = dict(foo=dict(Document=3, Folder=2))
        info = convertFacets(fields, context, request)
        self.assertEqual(len(info), 1)
        counts = info[0]['counts']
        params = lambda query: sorted(map(unquote, query.split('&')))
        self.assertEqual(params(counts[0]['query']), [
            'fq=bar:private', 'fq=foo:"Document"'])
        self.assertEqual(params(counts[1]['query']), [
            'fq=bar:private', 'fq=foo:"Folder"'])

    def testSelectedFacetsInformation(self):
        request = TestRequest()
        selected = SearchFacetsView(Dummy(), request).selected
        # initially no facets are seleted
        self.assertEqual(selected(), [])
        # so let's select one...
        params = lambda query: sorted(map(unquote, query.split('&')))
        info = lambda: [(i['title'], params(i['query'])) for i in selected()]
        request.form['fq'] = 'foo:"xy"'
        self.assertEqual(info(), [
            ('foo', ['facet.field=foo']),
        ])
        # and then some more...
        request.form['fq'] = ['foo:"x"', 'bar:"y"']
        self.assertEqual(info(), [
            ('foo', ['facet.field=foo', 'fq=bar:"y"']),
            ('bar', ['facet.field=bar', 'fq=foo:"x"']),
        ])
        request.form['fq'] = ['foo:"x"', 'bar:"y"', 'bah:"z"']
        self.assertEqual(info(), [
            ('foo', ['facet.field=foo', 'fq=bah:"z"', 'fq=bar:"y"']),
            ('bar', ['facet.field=bar', 'fq=bah:"z"', 'fq=foo:"x"']),
            ('bah', ['facet.field=bah', 'fq=bar:"y"', 'fq=foo:"x"']),
        ])
        # extra parameter should be left untouched
        request.form['foo'] = 'bar'
        self.assertEqual(info(), [
            ('foo', ['facet.field=foo', 'foo=bar', 'fq=bah:"z"', 'fq=bar:"y"']),
            ('bar', ['facet.field=bar', 'foo=bar', 'fq=bah:"z"', 'fq=foo:"x"']),
            ('bah', ['facet.field=bah', 'foo=bar', 'fq=bar:"y"', 'fq=foo:"x"']),
        ])
        # an existing 'facet.field' parameter should be preserved
        del request.form['foo']
        request.form['facet.field'] = 'x'
        self.assertEqual(info(), [
            ('foo', ['facet.field=foo', 'facet.field=x', 'fq=bah:"z"', 'fq=bar:"y"']),
            ('bar', ['facet.field=bar', 'facet.field=x', 'fq=bah:"z"', 'fq=foo:"x"']),
            ('bah', ['facet.field=bah', 'facet.field=x', 'fq=bar:"y"', 'fq=foo:"x"']),
        ])

    def testSelectedFacetValues(self):
        request = TestRequest()
        selected = SearchFacetsView(Dummy(), request).selected
        info = lambda: [(i['title'], i['value']) for i in selected()]
        request.form['fq'] = 'foo:"xy"'
        self.assertEqual(info(), [('foo', 'xy')])
        request.form['fq'] = ['foo:"x"', 'bar:"y"']
        self.assertEqual(info(), [('foo', 'x'), ('bar', 'y')])
        request.form['fq'] = ['foo:"x"', 'bar:"y"', 'bah:"z"']
        self.assertEqual(info(), [('foo', 'x'), ('bar', 'y'), ('bah', 'z')])

    def testEmptyFacetField(self):
        context = Dummy()
        request = {'facet.field': 'Subject'}
        fields = dict(Subject=dict())
        info = convertFacets(fields, context, request)
        self.assertEqual(info, [])

    def testEmptyFacetFieldWithZeroCounts(self):
        request = Dummy(form={})
        fields = dict(foo={'foo': 0, 'bar': 0})
        results = Dummy(facet_counts=dict(facet_fields=fields))
        view = SearchFacetsView(Dummy(), request)
        view.kw = dict(results=results)
        self.assertEqual(view.facets(), [])

    def testFacetFieldFilter(self):
        context = Dummy()
        request = {'facet.field': 'foo'}
        fields = dict(foo={'foo': 2, 'bar': 4, '': 6, 'nil': 0})
        # without a filter all values are included
        info = convertFacets(fields, context, request)
        self.assertEqual(len(info), 1)
        self.assertEqual([(c['name'], c['count']) for c in info[0]['counts']], [
            ('', 6),
            ('bar', 4),
            ('foo', 2),
            ('nil', 0),
        ])
        # let's filter out zero counts
        filter = lambda name, count: count > 0
        info = convertFacets(fields, context, request, filter=filter)
        self.assertEqual(len(info), 1)
        self.assertEqual([(c['name'], c['count']) for c in info[0]['counts']], [
            ('', 6),
            ('bar', 4),
            ('foo', 2),
        ])
        # and also unnamed facets
        filter = lambda name, count: name and count > 0
        info = convertFacets(fields, context, request, filter=filter)
        self.assertEqual(len(info), 1)
        self.assertEqual([(c['name'], c['count']) for c in info[0]['counts']], [
            ('bar', 4),
            ('foo', 2),
        ])


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    main(defaultTest='test_suite')
