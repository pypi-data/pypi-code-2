import unittest
from mock import Mock, patch
import mock_db

import sparql

EIONET_RDF = 'http://rdfdata.eionet.europa.eu/eea'

def _mock_request():
    mock_request = Mock()
    mock_request.form = dict((k,'') for k in [
        'title', 'endpoint_url', 'timeout', 'query', 'arg_spec'])
    mock_request.SESSION = {}
    return mock_request

class QueryTest(unittest.TestCase):
    def setUp(self):
        from Products.ZSPARQLMethod.Method import ZSPARQLMethod
        self.method = ZSPARQLMethod('sq', "Test Method", "_endpoint_")
        self.method.endpoint_url = "http://cr3.eionet.europa.eu/sparql"
        self.mock_db = mock_db.MockSparql()
        self.mock_db.start()

    def tearDown(self):
        self.mock_db.stop()

    def test_simple_query(self):
        from sparql import IRI
        self.method.query = mock_db.GET_LANGS
        result = self.method.execute()
        self.assertEqual(result['rows'], [
            (IRI(EIONET_RDF + '/languages/en'),),
            (IRI(EIONET_RDF + '/languages/de'),),
        ])

    @patch('Products.ZSPARQLMethod.Method.threading')
    def test_timeout(self, mock_threading):
        from Products.ZSPARQLMethod.Method import QueryTimeout
        self.method.query = mock_db.GET_LANGS
        mock_threading.Thread.return_value.isAlive.return_value = True

        self.assertRaises(QueryTimeout, self.method.execute)

    @patch('Products.ZSPARQLMethod.Method.sparql')
    def test_error(self, mock_sparql):
        self.method.query = mock_db.GET_LANGS
        class MyError(Exception): pass
        mock_sparql.query.side_effect = MyError

        self.assertRaises(MyError, self.method.execute)

    def test_query_with_arguments(self):
        self.method.query = mock_db.GET_LANG_BY_NAME
        result = self.method.execute(lang_name=sparql.Literal("Danish"))

        danish_iri = sparql.IRI(EIONET_RDF+'/languages/da')
        self.assertEqual(result['rows'], [(danish_iri,)])

    def test_call(self):
        self.method.query = mock_db.GET_LANG_BY_NAME
        self.method.arg_spec = u"lang_name:n3term"
        result = self.method(lang_name='"Danish"')

        danish_iri = sparql.IRI(EIONET_RDF+'/languages/da')
        self.assertEqual(result['rows'], [(danish_iri,)])

    def test_map_and_execute(self):
        self.method.query = mock_db.GET_LANG_BY_NAME
        self.method.arg_spec = u"lang_name:n3term"
        result = self.method.map_and_execute(lang_name='"Danish"')

        danish_iri = sparql.IRI(EIONET_RDF+'/languages/da')
        self.assertEqual(result['rows'], [(danish_iri,)])


class MapArgumentsTest(unittest.TestCase):

    def _test(self, raw_arg_spec, arg_data, expected):
        from Products.ZSPARQLMethod.Method import map_arg_values, parse_arg_spec
        missing, result = map_arg_values(parse_arg_spec(raw_arg_spec), arg_data)
        self.assertEqual(missing, [])
        self.assertEqual(result, expected)
        self.assertEqual(map(type, result.values()),
                         map(type, expected.values()))

    def test_map_zero(self):
        self._test(u'', (), {})

    def test_map_one_iri(self):
        en = EIONET_RDF + '/languages/en'
        self._test(u'lang_url:iri',
                   {'lang_url': en},
                   {'lang_url': sparql.IRI(en)})

    def test_map_one_parsed_iri(self):
        en = EIONET_RDF + '/languages/en'
        self._test(u'lang_url:n3term',
                   {'lang_url': '<%s>' % en},
                   {'lang_url': sparql.IRI(en)})

    def test_map_one_literal(self):
        self._test(u'name:string',
                   {'name': u"Joe"},
                   {'name': sparql.Literal(u"Joe")})

    def test_map_one_float(self):
        en = EIONET_RDF + '/languages/en'
        self._test(u'lang_url:float',
                   {'lang_url': '1.23'},
                   {'lang_url': sparql.Literal('1.23', sparql.XSD_FLOAT)})

    def test_map_one_parsed_typed_literal(self):
        en = EIONET_RDF + '/languages/en'
        self._test(u'lang_url:n3term',
                   {'lang_url': '"12:33"^^'+sparql.XSD_TIME},
                   {'lang_url': sparql.Literal('12:33', sparql.XSD_TIME)})

    def test_map_two_values(self):
        en = EIONET_RDF + '/languages/en'
        self._test(u'name:string lang_url:n3term',
                   {'name': u"Joe", 'lang_url': '<%s>' % en},
                   {'name': sparql.Literal(u"Joe"),
                    'lang_url': sparql.IRI(en)})

class InterpolateQueryTest(unittest.TestCase):

    def _test(self, query_spec, var_data, expected):
        from Products.ZSPARQLMethod.Method import interpolate_query
        result = interpolate_query(query_spec, var_data)
        self.assertEqual(result, expected)

    def test_no_variables(self):
        self._test(u"SELECT * WHERE { ?s ?p ?u }",
                   {},
                   u"SELECT * WHERE { ?s ?p ?u }")

    def test_one_iri(self):
        onto_name = EIONET_RDF + '/ontology/name'
        self._test(u'SELECT * WHERE { ?s ${pred} "Joe" }',
                   {'pred': sparql.IRI(onto_name)},
                   u'SELECT * WHERE { ?s <%s> "Joe" }' % onto_name)

    def test_one_literal(self):
        self._test(u"SELECT * WHERE { ?s ?p ${value} }",
                   {'value': sparql.Literal("Joe")},
                   u'SELECT * WHERE { ?s ?p "Joe" }')

class CachingTest(unittest.TestCase):

    def setUp(self):
        from Products.ZSPARQLMethod.Method import ZSPARQLMethod
        self.method = ZSPARQLMethod('sq', "Test Method", "_endpoint_")
        self.method.endpoint_url = "http://cr3.eionet.europa.eu/sparql"

        from Products.StandardCacheManagers.RAMCacheManager import RAMCache
        self.cache = RAMCache()
        self.cache.__dict__.update({
            'threshold': 100, 'cleanup_interval': 300, 'request_vars': ()})
        self.method.ZCacheable_getCache = Mock(return_value=self.cache)
        self.method.ZCacheable_setManagerId('_cache_for_test')

    def test_invalidate(self):
        self.cache.ZCache_invalidate = Mock()
        self.method.manage_edit(_mock_request())
        self.cache.ZCache_invalidate.assert_called_once_with(self.method)

    @patch('Products.ZSPARQLMethod.Method.query_and_get_result')
    def test_cached_queries(self, mock_query):
        onto_name = EIONET_RDF + '/ontology/name'
        self.method.query = "SELECT * WHERE {$subject <%s> ?value}" % onto_name
        self.method.arg_spec = u"subject:iri"
        mock_query.return_value = {}

        self.method.map_and_execute(subject=EIONET_RDF + '/languages/en')
        self.method.map_and_execute(subject=EIONET_RDF + '/languages/da')
        self.method.map_and_execute(subject=EIONET_RDF + '/languages/da')
        self.method.map_and_execute(subject=EIONET_RDF + '/languages/en')
        self.method.map_and_execute(subject=EIONET_RDF + '/languages/fr')
        self.method.map_and_execute(subject=EIONET_RDF + '/languages/fr')
        self.method.map_and_execute(subject=EIONET_RDF + '/languages/fr')
        self.method.map_and_execute(subject=EIONET_RDF + '/languages/fr')
        self.method.map_and_execute(subject=EIONET_RDF + '/languages/da')

        self.assertEqual(len(mock_query.call_args_list), 3)
