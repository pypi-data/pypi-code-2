# -*- coding: utf-8 -*-

from unittest import TestCase, defaultTestLoader, main
from DateTime import DateTime
from Missing import MV
from zope.component import provideUtility

from collective.solr.interfaces import ISolrConnectionConfig
from collective.solr.manager import SolrConnectionConfig
from collective.solr.manager import SolrConnectionManager
from collective.solr.tests.utils import getData, fakehttp
from collective.solr.search import Search
from collective.solr.queryparser import quote


class QuoteTests(TestCase):

    def testQuoting(self):
        # http://lucene.apache.org/java/2_3_2/queryparsersyntax.html
        self.assertEqual(quote(''), '')
        self.assertEqual(quote(' '), '')
        self.assertEqual(quote('foo'), 'foo')
        self.assertEqual(quote('foo '), 'foo')
        self.assertEqual(quote('"foo"'), '"foo"')
        self.assertEqual(quote('"foo'), '\\"foo')
        self.assertEqual(quote('foo"'), 'foo\\"')
        self.assertEqual(quote('foo bar'), '(foo bar)')
        self.assertEqual(quote('"foo bar" bah'), '("foo bar" bah)')
        self.assertEqual(quote('\\['), '\\[')
        self.assertEqual(quote(')'), '\)')
        self.assertEqual(quote('"(foo bar)" bah'), '("\\(foo bar\\)" bah)')
        self.assertEqual(quote('"(foo\\"bar)" bah'), '("\\(foo\\"bar\\)" bah)')
        self.assertEqual(quote('"foo bar"'), '"foo bar"')
        self.assertEqual(quote('"foo bar'), '(\\"foo bar)')
        self.assertEqual(quote('foo bar what?'), '(foo bar what?)')
        self.assertEqual(quote('[]'), '')
        self.assertEqual(quote('()'), '')
        self.assertEqual(quote('{}'), '')
        self.assertEqual(quote('...""'), '...\\"\\"')
        self.assertEqual(quote('\\'), '\\\\') # Search for \ has to be quoted
        self.assertEqual(quote('\?'), '\?')
        self.assertEqual(quote('john@foo.com'), 'john@foo.com')
        self.assertEqual(quote('http://machine/folder and item and some/path and and amilli3*'),
                               '(http\://machine/folder and item and some/path and and amilli3*)')
        self.assertEqual(quote('"[]"'), '"\[\]"')
        self.assertEqual(quote('"{}"'), '"\{\}"')
        self.assertEqual(quote('"()"'), '"\(\)"')
        self.assertEqual(quote('foo and bar and 42"*'), '(foo and bar and 42\\"\\*)')
        # Can't use ? or * as beginning of new query
        self.assertEqual(quote('"fix and it"*'), '"fix and it"')
        self.assertEqual(quote('"fix and it"?'), '"fix and it"')
        self.assertEqual(quote('foo and bar and [foobar at foo.com]*'),
                               '(foo and bar and \[foobar at foo.com\])')

    def testQuotingWildcardSearches(self):
        self.assertEqual(quote('te?t'), 'te?t')
        self.assertEqual(quote('test*'), 'test*')
        self.assertEqual(quote('test**'), 'test*')
        self.assertEqual(quote('te*t'), 'te*t')
        self.assertEqual(quote('?test'), 'test')
        self.assertEqual(quote('*test'), 'test')

    def testQuotingFuzzySearches(self):
        self.assertEqual(quote('roam~'), 'roam~')
        self.assertEqual(quote('roam~0.8'), 'roam~0.8')

    def testQuotingProximitySearches(self):
        self.assertEqual(quote('"jakarta apache"~10'), '"jakarta apache"~10')

    def testQuotingRangeSearches(self):
        self.assertEqual(quote('[* TO NOW]'), '[* TO NOW]')
        self.assertEqual(quote('[1972-05-11T00:00:00.000Z TO *]'),
                               '[1972-05-11T00:00:00.000Z TO *]')
        self.assertEqual(quote('[1972-05-11T00:00:00.000Z TO 2011-05-10T01:30:00.000Z]'),
                               '[1972-05-11T00:00:00.000Z TO 2011-05-10T01:30:00.000Z]')
        self.assertEqual(quote('[20020101 TO 20030101]'),
                               '[20020101 TO 20030101]')
        self.assertEqual(quote('{Aida TO Carmen}'), '{Aida TO Carmen}')
        self.assertEqual(quote('{Aida TO}'), '{Aida TO *}')
        self.assertEqual(quote('{TO Carmen}'), '{* TO Carmen}')

    def testQuotingBoostingTerm(self):
        self.assertEqual(quote('jakarta^4 apache'), '(jakarta^4 apache)')
        self.assertEqual(quote('jakarta^0.2 apache'), '(jakarta^0.2 apache)')
        self.assertEqual(quote('"jakarta apache"^4 "Apache Lucene"'),
                               '("jakarta apache"^4 "Apache Lucene")')

    def testQuotingOperatorsGrouping(self):
        self.assertEqual(quote('+return +"pink panther"'),
                               '(+return +"pink panther")')
        self.assertEqual(quote('+jakarta lucene'), '(+jakarta lucene)')
        self.assertEqual(quote('"jakarta apache" -"Apache Lucene"'),
                               '("jakarta apache" -"Apache Lucene")')
        self.assertEqual(quote('"jakarta apache" NOT "Apache Lucene"'),
                               '("jakarta apache" NOT "Apache Lucene")')
        self.assertEqual(quote('"jakarta apache" OR jakarta'),
                               '("jakarta apache" OR jakarta)')
        self.assertEqual(quote('"jakarta apache" AND "Apache Lucene"'),
                               '("jakarta apache" AND "Apache Lucene")')
        self.assertEqual(quote('(jakarta OR apache) AND website'),
                               '((jakarta OR apache) AND website)')
        self.assertEqual(quote('(a AND (b OR c))'), '(a AND (b OR c))')
        self.assertEqual(quote('((a AND b) OR c)'), '((a AND b) OR c)')

    def testQuotingEscapingSpecialCharacters(self):
        self.assertEqual(quote('-+&&||!^~:'), '\\-\\+\\&&\\||\\!\\^\\~\\:')
        # Only quote * and ? if quoted
        self.assertEqual(quote('"*?"'), '"\\*\\?"')
        # also quote multiple occurrences
        self.assertEqual(quote(':'), '\\:')
        self.assertEqual(quote(': :'), '(\\: \\:)')
        self.assertEqual(quote('foo+ bar! nul:'), '(foo\\+ bar\\! nul\\:)')

    def testUnicode(self):
        self.assertEqual(quote('foø'), 'fo\xc3\xb8')
        self.assertEqual(quote('"foø'), '\\"fo\xc3\xb8')
        self.assertEqual(quote('whät?'), 'wh\xc3\xa4t?')
        self.assertEqual(quote('"whät?"'), '"wh\xc3\xa4t\?"')
        self.assertEqual(quote('"[ø]"'), '"\[\xc3\xb8\]"')
        self.assertEqual(quote('[ø]'), '\\[\xc3\xb8\\]')
        self.assertEqual(quote('"foø*"'), '"fo\xc3\xb8\*"')
        self.assertEqual(quote('"foø bar?"'), '"fo\xc3\xb8 bar\?"')
        self.assertEqual(quote(u'john@foo.com'), 'john@foo.com')

    def testSolrSpecifics(self):
        # http://wiki.apache.org/solr/SolrQuerySyntax
        self.assertEqual(quote('"recip(rord(myfield),1,2,3)"'),
                               '"recip\(rord\(myfield\),1,2,3\)"') # Seems to be ok to quote function
        self.assertEqual(quote('[* TO NOW]'), '[* TO NOW]')
        self.assertEqual(quote('[1976-03-06T23:59:59.999Z TO *]'),
                               '[1976-03-06T23:59:59.999Z TO *]')
        self.assertEqual(quote('[1995-12-31T23:59:59.999Z TO 2007-03-06T00:00:00Z]'),
                               '[1995-12-31T23:59:59.999Z TO 2007-03-06T00:00:00Z]')
        self.assertEqual(quote('[NOW-1YEAR/DAY TO NOW/DAY+1DAY]'),
                               '[NOW-1YEAR/DAY TO NOW/DAY+1DAY]')
        self.assertEqual(quote('[1976-03-06T23:59:59.999Z TO 1976-03-06T23:59:59.999Z+1YEAR]'),
                               '[1976-03-06T23:59:59.999Z TO 1976-03-06T23:59:59.999Z+1YEAR]')
        self.assertEqual(quote('[1976-03-06T23:59:59.999Z/YEAR TO 1976-03-06T23:59:59.999Z]'),
                               '[1976-03-06T23:59:59.999Z/YEAR TO 1976-03-06T23:59:59.999Z]')


class QueryTests(TestCase):

    def setUp(self):
        provideUtility(SolrConnectionConfig(), ISolrConnectionConfig)
        self.mngr = SolrConnectionManager()
        self.mngr.setHost(active=True)
        conn = self.mngr.getConnection()
        fakehttp(conn, getData('schema.xml'))   # fake schema response
        self.mngr.getSchema()                   # read and cache the schema
        self.search = Search()
        self.search.manager = self.mngr

    def tearDown(self):
        self.mngr.closeConnection()
        self.mngr.setHost(active=False)

    def bq(self, *args, **kw):
        query = self.search.buildQuery(*args, **kw)
        return ' '.join(query.values())

    def testSimpleQueries(self):
        bq = self.bq
        self.assertEqual(bq('foo'), '+foo')
        self.assertEqual(bq('foo*'), '+foo*')
        self.assertEqual(bq('foo!'), '+foo\\!')
        self.assertEqual(bq('(foo)'), '+foo')
        self.assertEqual(bq('(foo...'), '+foo...')
        self.assertEqual(bq('foo bar'), '+(foo bar)')
        self.assertEqual(bq('john@foo.com'), '+john@foo.com')
        self.assertEqual(bq(name='foo'), '+name:foo')
        self.assertEqual(bq(name='foo*'), '+name:foo*')
        self.assertEqual(bq(name='foo bar'), '+name:(foo bar)')
        self.assertEqual(bq(name='john@foo.com'), '+name:john@foo.com')
        self.assertEqual(bq(name=' '), '') # Whitespace is removed
        self.assertEqual(bq(name=''), '')

    def testMultiValueQueries(self):
        bq = self.bq
        self.assertEqual(bq(('foo', 'bar')), '+(foo OR bar)')
        self.assertEqual(bq(('foo', 'bar*')), '+(foo OR bar*)')
        self.assertEqual(bq(('foo bar', 'hmm')), '+("foo bar" OR hmm)')
        self.assertEqual(bq(('foø bar', 'hmm')), '+("fo\xc3\xb8 bar" OR hmm)')
        self.assertEqual(bq(('"foo bar"', 'hmm')), '+("foo bar" OR hmm)')
        self.assertEqual(bq(name=['foo', 'bar']), '+name:(foo OR bar)')
        self.assertEqual(bq(name=['foo', 'bar*']), '+name:(foo OR bar*)')
        self.assertEqual(bq(name=['foo bar', 'hmm']), '+name:("foo bar" OR hmm)')

    def testMultiArgumentQueries(self):
        bq = self.bq
        self.assertEqual(bq('foo', name='bar'), '+foo +name:bar')
        self.assertEqual(bq('foo', name=('bar', 'hmm')),
            '+foo +name:(bar OR hmm)')
        self.assertEqual(bq('foo', name=('foo bar', 'hmm')),
            '+foo +name:("foo bar" OR hmm)')
        self.assertEqual(bq(name='foo', cat='bar'), '+name:foo +cat:bar')
        self.assertEqual(bq(name='foo', cat=['bar', 'hmm']),
            '+name:foo +cat:(bar OR hmm)')
        self.assertEqual(bq(name='foo', cat=['foo bar', 'hmm']),
            '+name:foo +cat:("foo bar" OR hmm)')
        self.assertEqual(bq('foo', name=' '), '+foo')
        self.assertEqual(bq('foo', name=''), '+foo')

    def testInvalidArguments(self):
        bq = self.bq
        self.assertEqual(bq(title='foo'), '')
        self.assertEqual(bq(title='foo', name='bar'), '+name:bar')
        self.assertEqual(bq('bar', title='foo'), '+bar')

    def testUnicodeArguments(self):
        bq = self.bq
        self.assertEqual(bq(u'foo'), '+foo')
        self.assertEqual(bq(u'foø'), '+fo\xc3\xb8')
        self.assertEqual(bq(u'john@foo.com'), '+john@foo.com')
        self.assertEqual(bq(name=['foo', u'bar']), '+name:(foo OR bar)')
        self.assertEqual(bq(name=['foo', u'bär']), '+name:(foo OR b\xc3\xa4r)')
        self.assertEqual(bq(name='foo', cat=(u'bar', 'hmm')), '+name:foo +cat:(bar OR hmm)')
        self.assertEqual(bq(name='foo', cat=(u'bär', 'hmm')), '+name:foo +cat:(b\xc3\xa4r OR hmm)')
        self.assertEqual(bq(name=u'john@foo.com', cat='spammer'), '+name:john@foo.com +cat:spammer')

    def testQuotedQueries(self):
        bq = self.bq
        self.assertEqual(bq('"foo"'), '+"foo"')
        self.assertEqual(bq('foo'), '+foo')
        self.assertEqual(bq('"foo*"'), '+"foo\*"')
        self.assertEqual(bq('foo*'), '+foo*')
        self.assertEqual(bq('"+foo"'), '+"\+foo"')
        self.assertEqual(bq('+foo'), '+foo')
        self.assertEqual(bq('"foo bar"'), '+"foo bar"')
        self.assertEqual(bq('foo bar'), '+(foo bar)')
        self.assertEqual(bq('"foo bar?"'), '+"foo bar\?"')
        self.assertEqual(bq('foo bar?'), '+(foo bar?)')
        self.assertEqual(bq('-foo +bar'), '+(-foo +bar)')
        self.assertEqual(bq('"-foo +bar"'), '+"\-foo \+bar"')
        self.assertEqual(bq(name='"foo"'), '+name:"foo"')
        self.assertEqual(bq(name='"foo bar'), '+name:(\\"foo bar)')
        self.assertEqual(bq(name='"foo bar*'), '+name:(\\"foo bar\\*)')
        self.assertEqual(bq(name='-foo', timestamp='[* TO NOW]'),
            '+timestamp:[* TO NOW] +name:-foo')
        self.assertEqual(bq(name='"john@foo.com"'), '+name:"john@foo.com"')
        self.assertEqual(bq(name='" "'), '+name:" "')
        self.assertEqual(bq(name='""'), '+name:\\"\\"')

    def testComplexQueries(self):
        bq = self.bq
        self.assertEqual(bq('foo', name='"herb*"', cat=(u'bär', '"-hmm"')),
            '+foo +name:"herb\*" +cat:(b\xc3\xa4r OR "\-hmm")')
        self.assertEqual(bq('foo', name='herb*', cat=(u'bär', '-hmm')),
            '+foo +name:herb* +cat:(b\xc3\xa4r OR -hmm)')

    def testBooleanQueries(self):
        bq = self.bq
        self.assertEqual(bq(inStock=True), '+inStock:true')
        self.assertEqual(bq(inStock=False), '+inStock:false')

    def testBooleanCriteriaQuoting(self):
        bq = self.bq
        self.assertEqual(
            bq(inStock=[1, True, '1', 'True']),
            '+inStock:true')
        self.assertEqual(
            bq(inStock=[0, '', False, '0', 'False', None, (), [], {}, MV]),
            '+inStock:false')
        self.assertEqual(bq(inStock=True), '+inStock:true')
        self.assertEqual(bq(inStock=1), '+inStock:true')
        self.assertEqual(bq(inStock='0'), '+inStock:false')
        self.assertEqual(bq(inStock=[True, False]), '')
        self.assertEqual(bq(inStock=[1, MV]), '')

    def testLiterateQueries(self):
        bq = self.bq
        self.assertEqual(bq(name=set(['bar'])), '(bar)')
        self.failUnless(bq(name=set(['foo', 'bar'])) in
            ['(foo OR bar)', '(bar OR foo)'])
        self.failUnless(bq(name=set(['foo!', '+bar:camp'])) in
            ['(foo! OR +bar:camp)', '(+bar:camp OR foo!)'])


class InactiveQueryTests(TestCase):

    def testUnavailableSchema(self):
        provideUtility(SolrConnectionConfig(), ISolrConnectionConfig)
        search = Search()
        search.manager = SolrConnectionManager()
        self.assertEqual(search.buildQuery('foo'), {})
        self.assertEqual(search.buildQuery(name='foo'), {})


class SearchTests(TestCase):

    def setUp(self):
        provideUtility(SolrConnectionConfig(), ISolrConnectionConfig)
        self.mngr = SolrConnectionManager()
        self.mngr.setHost(active=True)
        self.conn = self.mngr.getConnection()
        self.search = Search()
        self.search.manager = self.mngr

    def tearDown(self):
        self.mngr.closeConnection()
        self.mngr.setHost(active=False)

    def testSimpleSearch(self):
        schema = getData('schema.xml')
        search = getData('search_response.txt')
        request = getData('search_request.txt')
        output = fakehttp(self.conn, schema, search)    # fake responses
        query = self.search.buildQuery(id='[* TO *]')
        results = self.search(query, rows=10, wt='xml', indent='on').results()
        normalize = lambda x: sorted(x.split('&'))      # sort request params
        self.assertEqual(normalize(output.get(skip=1)), normalize(request))
        self.assertEqual(results.numFound, '1')
        self.assertEqual(len(results), 1)
        match = results[0]
        self.assertEqual(match.id, '500')
        self.assertEqual(match.name, 'python test doc')
        self.assertEqual(match.popularity, 0)
        self.assertEqual(match.sku, '500')
        self.assertEqual(match.timestamp,
            DateTime('2008-02-29 16:11:46.998 GMT'))


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    main(defaultTest='test_suite')
