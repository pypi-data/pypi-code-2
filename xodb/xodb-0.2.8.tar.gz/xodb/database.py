from __future__ import absolute_import

import time
import string
import xapian

from operator import itemgetter
from functools import partial
from json import dumps, loads

from xapian import Query, QueryParser, UnimplementedError, DocNotFoundError

from . import snowball
from .exc import ValidationError


RETRY_LIMIT = 3


default_parser_flags = (QueryParser.FLAG_PHRASE |
                        QueryParser.FLAG_BOOLEAN |
                        QueryParser.FLAG_LOVEHATE |
                        QueryParser.FLAG_SPELLING_CORRECTION |
                        QueryParser.FLAG_BOOLEAN_ANY_CASE |
                        QueryParser.FLAG_WILDCARD)


def _schema_name(schema):
    return "%s.%s" % (schema.__module__, schema.__name__)


def defaults(head, limit=0, mlimit=0, klimit=1.0, kmlimit=1.0):
    return (head, limit, mlimit, klimit, kmlimit)


def _lookup_schema(name):
    modname, expr = name.rsplit('.', 1)
    local_name = modname.split('.')[-1]
    mod = __import__(modname, {}, {}, local_name)
    return eval(expr, mod.__dict__)


def _prefix(name):
    return (u'X%s:' % name.upper()).encode('utf-8')


class Record(object):

    def __init__(self, schema):
        self._xodb_schema = schema

    def __getattr__(self, name):
        try:
            return self._xodb_schema[name].value
        except KeyError:
            raise AttributeError(name)

    def __repr__(self):
        return repr(self._xodb_schema)


def record_factory(database, record):
    return Record(record)


class LanguageDecider(xapian.ExpandDecider):
    """
    A Xapian ExpandDecider that decide which terms to keep and which
    to discard when expanding a query using the "suggest" syntax.  As
    a place to start, we throw out:

      - Terms that don't begin with an uppercase letter or digit.
        This filters prefixed terms and stemmed forms.

      - Terms shorter than min_length chars, which are likely irrelevant

      - Stopwords for the given language.  Default is english, pass
        None for the language argument if no stopping is desired.
    """

    min_length = 5
    nostart = unicode(string.uppercase + string.digits)

    def __init__(self, language="en", filter=None, stems=None):
        super(LanguageDecider, self).__init__()
        if language in snowball.stoppers:
            self.stopper = snowball.stoppers[language]
            self.stemmer = xapian.Stem(language)
        else:
            self.stopper = lambda(term): False
            self.stemmer = xapian.Stem("none")
        self.stems = tuple(self.stemmer(t) for t in stems) if stems else ()

    def __call__(self, term):
        term = term.decode("utf-8")
        if (term[0] in self.nostart or
            len(term) < self.min_length or
            self.stopper(term) or
            '_' in term or
            self.stemmer(term) in self.stems):
            return False
        return True


class PrefixDecider(xapian.ExpandDecider):

    __slots__ = ['prefix']

    def __init__(self, prefix):
        super(PrefixDecider, self).__init__()
        self.prefix = (u'X%s:' % prefix.upper()).encode('utf-8')

    def __call__(self, term):
        return term.startswith(self.prefix)


class MultipleValueRangeProcessor(xapian.ValueRangeProcessor):
    """Value range processor for multiple prefixes.

    :param map: a dict of prefix to value number pairs.

    :param serializer: optional callable to serialize the arguments into
                       the same form as the corresponding values are stored.
                       Typically xapian.sortable_serialise for floats,
                       str.lower for strings.
    """

    def __init__(self, map, serializer=None):
        self.map = map
        self.serializer = serializer or (lambda x: x)
        xapian.ValueRangeProcessor.__init__(self)

    def __call__(self, begin, end):
        for prefix, value in self.map.items():
            if begin.startswith(prefix + ':'):
                return (value,
                        self.serializer(begin[len(prefix) + 1:]),
                        self.serializer(end))
        return (xapian.BAD_VALUENO, begin, end)


class Database(object):
    """An xodb database.

    :param db_or_path: A path to file, or a xapian.Database object
    that backs this Database instance.

    :param writable: Open database in writable mode.

    :param overwrite: If writable is True, overwrite the existing
    database with a new one.

    :param spelling: If True, write spelling correction data to the
    database.

    :param replicated: If True, the database is opened read-only in
    replication mode (reopen() is never called, see xapian ticket
    #434)

    """

    record_factory = record_factory

    relevance_prefix = "_XODB_RP_"
    boolean_prefix = "_XODB_BP_"
    value_prefix = "_XODB_VALUE_"
    value_sort_prefix = "_XODB_VALUESORT_"
    value_count_name = "_XODB_COUNT_"
    backend = None

    def __init__(self, path,
                 writable=True,
                 overwrite=False,
                 spelling=True,
                 replicated=False):
        self.db_path = path
        self._writable = writable
        self._overwrite = overwrite
        self.spelling = spelling
        self.replicated = replicated

        if isinstance(path, basestring):
            if writable:
                if replicated:
                    raise TypeError("replication cannot be used with "
                                    "writable databases")
                if overwrite:
                    flags = xapian.DB_CREATE_OR_OVERWRITE
                else:
                    flags = xapian.DB_CREATE_OR_OPEN
                self.backend = xapian.WritableDatabase(path, flags)
            else:
                self.backend = xapian.Database(path)
        elif isinstance(path, xapian.Database):
            if replicated:
                raise TypeError("replication can only be used "
                                "if a database path is provided.")
            self.backend = self.db_path

        self.relevance_prefixes = {}
        self.boolean_prefixes = {}
        self.values = {}
        self.value_sorts = {}
        self.type_map = {}
        self.refresh_metadata()

    def close(self):
        self.backend.close()

    def flush(self):
        self.backend.flush()

    def map(self, otype, schema):
        """Map a type to a schema."""
        self.type_map[otype] = schema

    def schema_for(self, otype):
        """Get the schema for a given type, or one of its
        superclasses."""
        for base in otype.__mro__:
            if base in self.type_map:
                return self.type_map[base]
        raise TypeError("No schema defined for %s" % repr(otype))

    def _get_value_count(self):
        return int(self.backend.get_metadata(self.value_count_name))

    def _set_value_count(self, count):
        self.backend.set_metadata(self.value_count_name, str(count))

    value_count = property(_get_value_count, _set_value_count)

    def check_prefix(self, name, boolean=False):
        prefixes = set(self.relevance_prefixes.keys())
        prefixes.union(self.boolean_prefixes.keys())
        if name not in prefixes:
            upped = _prefix(name)
            if boolean:
                self.add_boolean_prefix(name, upped)
            else:
                self.add_prefix(name, upped)

    def add_prefix(self, key, value):
        """Add a prefix mapping to the database.
        """
        self.relevance_prefixes[key] = value
        self.backend.set_metadata(self.relevance_prefix + key, value)

    def add_boolean_prefix(self, key, value):
        """Add a boolean prefix mapping to the database.
        """
        self.boolean_prefixes[key] = value
        self.backend.set_metadata(self.boolean_prefix + key, value)

    def add_value(self, name, sort=None):
        """Add a value mapping to the database.
        """
        if name in self.values:
            return self.values[name]
        value_count = self.value_count + 1
        self.value_count = value_count
        self.values[name] = value_count
        self.backend.set_metadata(self.value_prefix + name, str(value_count))
        if sort:
            self.value_sorts[name] = sort
            self.backend.set_metadata(self.value_sort_prefix + name, sort)
        return value_count

    def __len__(self):
        """ Return the number of documents in this database. """
        self.backend.reopen()
        return self.backend.get_doccount()

    def allterms(self, prefix=""):
        self.backend.reopen()
        for t in self.backend.allterms(prefix):
            yield t.term

    def get(self, docid, default=None):
        """ Get a document with the given docid, or the default value if
        no such document exists.
        """
        try:
            return self[docid]
        except DocNotFoundError:
            return default

    def __getitem__(self, docid):
        return self.backend.get_document(docid)

    def __delitem__(self, docid):
        self.backend.delete_document(docid)

    def __setitem__(self, docid, document):
        doc = self.get(docid)
        if doc is None:
            self.backend.add_document(document)
        else:
            self.backend.replace_document(docid, document)

    def __contains__(self, docid):
        return True if self.get(docid) else False

    def add(self, *objs, **kw):
        """Add an object to the database by transforming it into a
        xapian document.  It's type or one of its base types must be
        mapped to a schema before an object can be added here.

        :params objs: One or more mapped objects to add.

        :param validate: Validated the schema before the object is
        added.  Default: True

        Returns a list of xapan documents that were added to the
        database.
        """
        added = []
        validate = kw.pop('validate', True)
        for obj in objs:
            if isinstance(obj, xapian.Document):
                self.backend.add_document(obj)
                added.append(obj)
                continue
            doc = self.to_document(obj, validate=validate)
            self.backend.add_document(doc)
            added.append(doc)
        return added

    def to_document(self, obj, validate=True):
        if hasattr(obj, '__xodb_schema__'):
            schema_type = obj.__xodb_schema__
        else:
            schema_type = self.schema_for(type(obj))
        schema = schema_type.from_defaults()
        schema.update_by_object(obj)

        if validate and not schema.validate():
            invalid = []
            for child in schema.all_children:
                if not child.valid:
                    invalid.append(child)
            raise ValidationError("Elements of %s did not validate %s:" %
                                  (schema.__class__.__name__,
                                   list((c.name, c.value)
                                        for c in invalid)))

        doc = self.doc_from_dict(schema.memo.dict)
        return doc

    def doc_from_dict(self, data):
        """
        """
        doc = xapian.Document()

        for term_tup in data.get('terms', ()):
            term = None
            typ = None
            wdfinc = 1
            if len(term_tup) > 2:
                term, typ, wdfinc = term_tup
            else:
                term, typ = term_tup
            if ':' in term:
                prefix, _, value = term.partition(':')
                self.check_prefix(prefix, typ)
                term = 'X%s:%s' % (prefix.upper(), value)
            doc.add_term(term, wdfinc)
                
        for post in data.get('posts', ()):
            pass

        for text_dict in data.get('texts', ()):
            lang = text_dict.get('lang')
            tg = xapian.TermGenerator()
            tg.set_database(self.backend)
            tg.set_document(doc)
            spelling = text_dict.get('spell', True)
            if spelling:
                tg.set_flags(xapian.TermGenerator.FLAG_SPELLING)
            if lang in snowball.stoppers:
                tg.set_stemmer(xapian.Stem(lang))
                tg.set_stopper(snowball.stoppers[lang])
            if text_dict.get('post', True):
                index_text = tg.index_text
            else:
                index_text = tg.index_text_without_positions
            text = text_dict.get('text')
            if text:
                prefix = text_dict.get('prefix')
                if prefix:
                    self.check_prefix(prefix)
                    prefix = 'X%s:' % prefix.upper()
                    index_text(text, 1, prefix)
                else:
                    index_text(text)

        for val_tuple in data.get('values', ()):
            name, value, typ = val_tuple
            if name in self.values:
                valno = self.values[name]
            else:
                valno = self.add_value(name, typ)
            if typ in ('integer',):
                value = xapian.sortable_serialise(value)
            doc.add_value(valno, value)

        data = data.get('data')
        if data:
            doc.set_data(data)
        return doc

    def reopen(self):
        if not self.replicated:
            self.backend.reopen()
        else:
            # replication does not support the reopen() method, so the
            # db must be explicitly closed and reopened.
            assert self.db_path, ("Must provide a db path when "
                                  "using replication.")
            self.close()
            self.backend = xapian.Database(self.db_path)
        self.refresh_metadata()

    def refresh_metadata(self):
        """Reopen the database, refresing the local connection's view
        of the prefix and value data.
        """
        try:
            keys = self.backend.metadata_keys()
        except UnimplementedError:
            # Inmemory backends don't expose metadata, so just return
            # since they can't persist anything anyway!
            return

        self.relevance_prefixes.clear()
        self.boolean_prefixes.clear()
        self.values.clear()
        self.value_sorts.clear()

        for k in keys:
            if k.startswith(self.relevance_prefix):
                prefix = k[len(self.relevance_prefix):]
                self.relevance_prefixes[prefix] = self.backend.get_metadata(k)
            elif k.startswith(self.boolean_prefix):
                prefix = k[len(self.boolean_prefix):]
                self.boolean_prefixes[prefix] = self.backend.get_metadata(k)
            elif k.startswith(self.value_prefix):
                value = k[len(self.value_prefix):]
                self.values[value] = int(self.backend.get_metadata(k))
            elif k.startswith(self.value_sort_prefix):
                value = k[len(self.value_sort_prefix):]
                self.value_sorts[value] = self.backend.get_metadata(k)

        try:
            # hit the property to refresh this value
            count = self.value_count
            count = count # pyflakes
        except ValueError:
            if self._writable:
                self.value_count = 0

    def begin(self):
        if self._writable:
            self.backend.reopen()
            self.backend.begin_transaction()

    def cancel(self):
        if self._writable:
            self.backend.cancel_transaction()

    def commit(self):
        if self._writable:
            self.backend.commit_transaction()

    def prepare_query_parser(self, language=None,
                             default_op=Query.OP_AND):
        qp = QueryParser()
        qp.set_database(self.backend)
        qp.set_default_op(default_op)

        if self.relevance_prefixes:
            for key, value in self.relevance_prefixes.items():
                qp.add_prefix(key, value)
        if self.boolean_prefixes:
            for key, value in self.boolean_prefixes.items():
                qp.add_boolean_prefix(key, value)
        if self.value_sorts:
            # First add numeric values ranges
            qp.add_valuerangeprocessor(MultipleValueRangeProcessor(
                dict(((k, self.values[k])
                      for k, v in self.value_sorts.items() if v == 'integer')),
                lambda s: xapian.sortable_serialise(float(s)),
            ))
            # Then string and date
            qp.add_valuerangeprocessor(MultipleValueRangeProcessor(
                dict(((k, self.values[k])
                      for k, v in self.value_sorts.items() if v != 'integer')),
            ))
        if language in snowball.stoppers:
            qp.set_stemmer(xapian.Stem(language))
            qp.set_stopper(snowball.stoppers[language])
            qp.set_stemming_strategy(QueryParser.STEM_SOME)
        return qp

    def querify(self, query,
                language=None,
                translit='translit/long',
                default_op=Query.OP_AND,
                parser_flags=default_parser_flags):
        """Return a query object, constructed from a string, query
        object, or mixed sequence of any number of strings, query
        objects, or subsequences of the same form.

        If 'query' is a xapian query object, it is returned unchanged.
        If it's a string, it is parsed with xapian's query parser and
        returned.  If it is a sequence, a new query is constructed
        with the 'default_op' operator and the sequence is iterated
        into the new query, recursively querify on each item of the
        sequence.
        """
        if isinstance(query, Query):
            return query
        if isinstance(query, basestring):
            if query == "":
                return Query("")
            else:
                query = query.lower()
                if translit:
                    query = query.encode(translit)
                qp = self.prepare_query_parser(language, default_op)
                return qp.parse_query(query, parser_flags)
        else:
            return reduce(partial(Query, default_op),
                          (self.querify(q,
                                        language,
                                        translit,
                                        default_op,
                                        parser_flags) for q in query))

    def query(self, query,
              offset=0,
              limit=0,
              order=None,
              reverse=False,
              language=None,
              check=0,
              translit='translit/long',
              match_decider=None,
              match_spy=None,
              document=False,
              echo=False,
              parser_flags=default_parser_flags,
              default_op=Query.OP_AND):
        """
        Query the database with the provided string or xapian Query
        object.  A string is passed into xapians QueryParser first to
        generate a Query object.
        """
        self.reopen()

        enq = xapian.Enquire(self.backend)
        if echo:
            print "Parsing query."
        query = self.querify(query, language, translit,
                             default_op, parser_flags)
        if echo:
            print "Done parsing query: %s" % str(query)
        enq.set_query(query)

        limit = limit or self.backend.get_doccount()

        if echo:
            start = time.time()
            print "Fetching mset..."
        mset = self._build_mset(enq, offset, limit, order, reverse,
                                check, match_decider, match_spy)
        if echo:
            print "Fetched mset in %s" % str(time.time() - start)
        return self._return_objects(mset, document=document)

    def count(self,
              query="",
              language=None,
              echo=False,
              translit='translit/long',
              parser_flags=default_parser_flags,
              default_op=Query.OP_AND):
        """
        Query the database with the provided string or xapian Query
        object.  A string is passed into xapians QueryParser first to
        generate a Query object.
        """
        self.reopen()
        query = self.querify(query, language, translit, default_op, parser_flags)
        if echo:
            print str(query)
        enq = xapian.Enquire(self.backend)
        enq.set_query(query)

        mset = self._build_mset(enq)
        return mset.size()

    def facet(self, query,
              prefix='facet',
              estimate=True,
              language=None,
              limit=0,
              mlimit=0,
              klimit=1.0,
              kmlimit=1.0,
              echo=False):
        """Get facet suggestions for the query, then the query with
        each suggested facet, asking xapian for an estimated count of
        each sub-query.
        """
        if estimate:
            counter = self.estimate
        else:
            counter = self.count

        results = {}
        suggestions = self.suggest(query,
                                   prefix=prefix,
                                   language=language,
                                   limit=limit,
                                   mlimit=mlimit,
                                   klimit=klimit,
                                   kmlimit=kmlimit,
                                   echo=echo)
        for facet in suggestions:
            q = self.querify([query, facet])
            if echo:
                print str(q)
            else:
                results[facet] = counter(q, language=language)
        return results

    def expand(self, query, expand,
               language=None,
               echo=False,
               translit='translit/long',
               default_op=Query.OP_AND,
               parser_flags=default_parser_flags):

        q = self.querify(query, language, translit, default_op, parser_flags)
        results = {}
        head, tail = expand[0], expand[1:]
        if isinstance(head, tuple):
            args = head
        else:
            args = (head,)
        head, limit, mlimit, klimit, kmlimit = defaults(*args)

        r = self.facet(
            q, prefix=head, language=language, echo=echo,
            limit=limit, mlimit=mlimit,
            klimit=klimit, kmlimit=kmlimit).items()

        for name, score in r:
            if tail:
                subq = self.querify([q, name])
                r = self.expand(
                    subq, tail, language, echo,
                    default_op, parser_flags)
                results[(name, score)] = r
            else:
                results[(name, score)] = score
        return results

    def estimate(self, query,
                 limit=0,
                 klimit=1.0,
                 language=None,
                 translit='translit/long',
                 check_at_least=None,
                 default_op=Query.OP_AND,
                 parser_flags=default_parser_flags):
        """Estimate the number of documents that will be yielded with the
        given query.

        Limit tells the estimator the minimum number of documents to
        consider.  A zero limit means check all documents in the db."""
        self.reopen()
        enq = xapian.Enquire(self.backend)

        if limit == 0:
            limit = int(self.backend.get_doccount() * klimit)

        query = self.querify(query, language, translit,
                             default_op, parser_flags)

        enq.set_query(query)
        if check_at_least is not None:
            mset = enq.get_mset(0, 0, limit)
        else:
            mset = enq.get_mset(0, 0, limit)
            
        return mset.get_matches_estimated()

    def term_freq(self, term):
        """
        Return a count of the number of documents indexed for a given
        term.  Useful for testing.
        """
        self.backend.reopen()
        return self.backend.get_termfreq(term)

    def describe_query(self, query,
                       language=None,
                       default_op=Query.OP_AND):
        """
        Describe the parsed query.
        """
        qp = self.prepare_query_parser(language, default_op)
        q = qp.parse_query(query, default_parser_flags)
        return str(q)

    def spell(self, query,
              language=None):
        """
        Suggest a query string with corrected spelling.
        """
        self.backend.reopen()
        qp = self.prepare_query_parser(language)
        qp.parse_query(query, QueryParser.FLAG_SPELLING_CORRECTION)
        return qp.get_corrected_query_string().decode('utf8')

    def suggest(self, query,
                offset=0,
                limit=0,
                moffset=0,
                mlimit=0,
                klimit=1.0,
                kmlimit=1.0,
                translit='translit/long',
                language=None,
                prefix=None,
                decider=None,
                score=False,
                echo=False,
                default_op=Query.OP_AND,
                parser_flags=default_parser_flags):
        """
        Suggest terms that would possibly yield more relevant results
        for the given query.
        """
        self.reopen()
        enq = xapian.Enquire(self.backend)

        query = self.querify(query, language, translit, default_op, parser_flags)

        if mlimit == 0:
            mlimit = int(self.backend.get_doccount() * kmlimit)

        if echo:
            print str(query)
        enq.set_query(query)

        mset = self._build_mset(enq, offset=moffset, limit=mlimit)

        rset = xapian.RSet()
        for m in mset:
            if hasattr(m, 'docid'): # 1.1
                docid = m.docid
            else:
                docid = m[xapian.MSET_DID] # 1.0
            rset.add_document(docid)

        if prefix is not None:
            decider = PrefixDecider(prefix)

        if decider is None:
            decider = LanguageDecider(language)

        if limit == 0:
            limit = int(self.backend.get_doccount() * klimit)

        eset = enq.get_eset(limit, rset, xapian.Enquire.INCLUDE_QUERY_TERMS,
                            1.0, decider)

        for item in eset.items:
            val = item[0].decode('utf8')
            if prefix and val.startswith('X%s:' % prefix.upper()):
                suffix = val[len(prefix) + 2:]
                if ' ' in suffix:
                    val = '%s:"%s"' % (prefix, suffix)
                else:
                    val = '%s:%s' % (prefix, suffix)
            if score:
                yield (val, item[1])
            else:
                yield val

    def _build_mset(self, enq,
                    offset=0,
                    limit=None,
                    order=None,
                    reverse=False,
                    check=None,
                    match_decider=None,
                    match_spy=None):
        if order is not None:
            if isinstance(order, basestring):
                try:
                    order = self.values[order]
                except KeyError:
                    raise ValueError("There is no sort name %s" % order)
            enq.set_sort_by_value(order, reverse)

        if limit is None:
            limit = self.backend.get_doccount()

        if check is None:
            check = limit + 1

        tries = 0
        while True:
            try:
                mset = enq.get_mset(
                    offset, limit, check, None, match_decider, match_spy)
                break
            except xapian.DatabaseModifiedError:
                if tries > RETRY_LIMIT:
                    raise
                self.reopen()
                tries += 1
        return mset

    def _return_objects(self, mset, document=False):
        for record in mset:
            if hasattr(record, 'document'):  # 1.1
                doc = record.document
            else:
                doc = record[xapian.MSET_DOCUMENT] # 1.0
            if document:
                yield doc
            else:
                data = doc.get_data()
                typ, data = loads(data)
                yield self.record_factory(_lookup_schema(typ).from_flat(data))


def jsonrpc_wrapper(f):
    def w(database, *args, **kw):
        # unstupidify the way the jsonrpc spec calls us
        if not args:
            args = []
            for k in kw:
                try:
                    i = int(k)
                except ValueError:
                    continue
                args.append((i, kw.pop(k)))
            args.sort(key=itemgetter(0))
            args = tuple(a[1] for a in args)
        return f(database, *args, **kw)
    return w


class JSONDatabase(object):
    """
    Thunk layer on top of database that returns json data.
    """

    def jsonify_record(database, record):
        return record.flatten()

    def __init__(self, database):
        database.record_factory = self.jsonify_record
        self._database = database

    @jsonrpc_wrapper
    def query(self, *args, **kw):
        return list(self._database.query(*args, **kw))

    @jsonrpc_wrapper
    def suggest(self, *args, **kw):
        return list(self._database.query(*args, **kw))

    @jsonrpc_wrapper
    def facet(self, *args, **kw):
        return self._database.facet(*args, **kw)

    @jsonrpc_wrapper
    def expand(self, *args, **kw):
        return self._database.expand(*args, **kw)

    @jsonrpc_wrapper
    def count(self, *args, **kw):
        return self._database.count(*args, **kw)
