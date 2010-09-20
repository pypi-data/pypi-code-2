import logging
from types import NoneType
import weakref

from sqlalchemy import engine_from_config, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.properties import ColumnProperty
from rumalchemy import sqlsoup
from zope.sqlalchemy import datamanager

from rum import Repository, RepositoryFactory, exceptions, repository, util,\
                transaction
from rum.genericfunctions import when
from rumalchemy.util import get_mapper, get_foreign_keys, version_id_name
from rumalchemy.fieldfactory import SAFieldFactory

__all__ = ["SARepository", "SARepositoryFactory"]

log = logging.getLogger(__name__)


class SARepositoryFactory(RepositoryFactory):
    def __init__(self, scan_modules=[], models=[], field_factory=None,
                 session_factory=None, reflect=None, engine=None, **kw):
        field_factory = SAFieldFactory(repositoryfactory=weakref.proxy(self))
        super(SARepositoryFactory, self).__init__(scan_modules, models,
                                                  field_factory)
        if not engine:
            try:
                self.engine = engine_from_config(kw)
            except KeyError:
                self.engine = None
        else:
            self.engine = engine
        if not self.engine and (reflect or not session_factory):
            raise ValueError(
                "Need to provide one of: 'sqlalchemy.url', 'engine' or "
                "'session_factory'"
                )
        if not session_factory:
            session_opts = self._get_session_opts(kw)
            session_opts['bind'] = self.engine
            self.session_factory = scoped_session(sessionmaker(**session_opts))
        else:
            self.session_factory  = util.import_string(session_factory)
        self.reflect = reflect

    def cleanup(self, app=None):
        # Cleans up session if app is full_stack or repository is not attached
        # to any app.
        if not app or app.config['full_stack']:
            if hasattr(self.session_factory, 'remove'):
                self.session_factory.remove()
            transaction.abort()

    def load_resources(self):
        """
        Aditionally loads extra resources as reflected with sqlsoup.
        """
        if self.reflect:
            self._models = self._models + self._reflect_models()
        super(SARepositoryFactory, self).load_resources()

    @staticmethod
    def _fix_soup_entity(entity):
        # sqlsoup breaks when trying to compare a MappedClass with None or a str
        # which the SingleSelectFields trigger. This is prolly a sqlsoup
        # bug since the comparation with plain-old SA mapped classes works
        # fine. Monkey-patch it with peak.rules.
        NOPE = lambda self, o: -1
        when(entity.__cmp__.im_func, (entity,NoneType))(NOPE)
        when(entity.__cmp__.im_func, (entity,basestring))(NOPE)

    def _reflect_models(self):
        # Use the scoped_session sqlsoup creates. This is suboptimal, we
        # need a way to bring the objects sqlsoup creates into our
        # session (which we can control: set to transactional, etc...)
        # If we don't use soup's session SA barfs with  a
        # 'object is already attached to session blah'
        metadata = MetaData(self.engine)
        metadata.reflect()
        # workaround: sqlalchemy does unicode names reflecting and SqlSoup
        #             doesn't like it
        for name, table in metadata.tables.iteritems():
            table.name = str(name)
            metadata.tables[table.name] = metadata.tables.pop(name)
        if self.reflect == 'all':
            table_names = metadata.tables.keys()
        else:
            table_names = self.reflect
        db = sqlsoup.SqlSoup(metadata,self.session_factory)
        entities=dict()
        for table_name in table_names:
            try:
                entities[table_name]=db.entity(table_name)
            except sqlsoup.PKNotFoundError:
                log.warn("reflection: skipping table "+table_name+ "...")
        mappers = dict((e, get_mapper(e)) for e in entities.itervalues())
        # autogenerate relations
        for table_name, entity in entities.iteritems():
            self._fix_soup_entity(entity)
            for prop in mappers[entity].iterate_properties:
                if isinstance(prop, ColumnProperty):
                    for col in prop.columns:
                        # See if the column is a foreign key
                        try:
                            fk = get_foreign_keys(col)[0]
                        except IndexError:
                            # It isn't...
                            continue
                        # It is, lookup parent mapper
                        relation_kwds=dict()
                        for parent, m in mappers.iteritems():
                            if fk.references(m.local_table):
                                if col.primary_key:
                                    relation_kwds["cascade"]='all, delete-orphan'
                                break
                        # Relate it
                        
                        assert getattr(db,table_name) is entity
# 
                        parent.relate(
                            self.names_for_resource(entity)[1],entity,
                            backref=self.names_for_resource(parent)[0],
                            **relation_kwds)
        return entities.values() 

    @staticmethod
    def _get_session_opts(opts, prefix = 'session.'):
        return dict(
            (k[len(prefix):], v)
            for (k,v) in opts.iteritems() if k.startswith(prefix)
            )



    @repository.names_for_resource.when((sqlsoup.TableClassType,))
    @repository.names_for_resource.when((sqlsoup.SelectableClassType,))
    def _strip_Mapped(next_method, self, resource):
        """
        Strips the Mapped prefix from entities reflected by sqlsoup.
        """
        funky_names = next_method(self, resource)
        def stripit(n):
            if 'mapped' in n.lower():
                return n[len('mapped'):]
            return n
        return tuple(stripit(n) for n in funky_names)


class SARepository(Repository):
    """
    A Repository that knows how to handle SA mapped classes.
    """
    def __init__(self, resource, factory, parent=None, remote_name=None,
                 parent_id=None):
        super_ = super(SARepository, self)
        super_.__init__(resource, factory, parent, remote_name, parent_id)
        self.session = self.factory.session_factory()
        self.session.autoflush = False
        log.debug("Session initialized: %r", self.session)

    @property
    def session_query(self):
        return self.session.query(self.resource)


    def get(self, id):
        """
        Returns a resource instance by id. Id could be a tuple for composite
        keys and even a string as received from the routes.
        """
        # TODO: Move id mangling logic to superclass, both here and in get_id
        if isinstance(id, basestring):
            id = self.split_id(id)
            id = [s.replace(self.slash_replacement, '/') for s in id]
        obj = self.session_query.get(id)
        if not obj:
            raise exceptions.ObjectNotFound(
                "No %r found with id %r" % (self.resource, id)
                )
        return obj
        
    def get_id(self, obj):
        m = get_mapper(obj)
        if not m:
            raise TypeError("WTF are you sending to me! %r"%(obj,))
        def _replace_slash(s):
            if isinstance(s, basestring):
                return s.replace('/', self.slash_replacement)
            return s
        pk = map(_replace_slash, m.primary_key_from_instance(obj))
        return self.composite_id_separator.join(map(unicode, pk))
    
    def select(self, query=None):
        """
        Returns an iterable that yields all  instances that match
        the criteria in ``query``. If ``query`` is ``None`` it should yield all
        possible instances.
        """
        session_query = self.session_query
        if self.remote_name:
            p_obj = self.parent_repository.get(self.parent_id)
            session_query = session_query.with_parent(p_obj, self.remote_name)
        if query:
            session_query = query.filter(session_query)
        return session_query

    def delete(self, obj):
        """
        Delete ``obj`` from the data store so it is no longer persistent.
        """
        self.session.delete(obj)
        self._set_dirty()

    def save(self, obj):
        """
        Save ``obj`` in the data store so it is persisted.
        """
        self.session.add(obj)
        self._set_dirty()

    #XXX: Perhaps promote to public function so it can be overrided?
    def _set_attrs(self, obj, data):
        log.debug("setting attributes %r on %r", data, obj)
        for k,v in data.iteritems():
            setattr(obj, k, v)
                
    def update(self, obj, data):
        """
        Update ``obj`` with ``data``. Data is a map keyed by attribute names
        with coerced and validated values from the View.
        """
        self._set_attrs(obj, data)
        self._set_dirty()

    def create(self, data):
        """
        Create a persistent new instance from ``data`` and return it.
        Data is a map keyed by attribute names with coerced and validated
        values from the View.
        """
        obj = self.resource()
        # If default values have not been provided, fill them in
        # Do not call self.defaults() blindly in order to avoid creating
        # potentially expensive objects   
        for field in self.factory.fields_for_resource(self.resource):
            if field.name not in data and field.has_default:
                data[field.name] = field.get_default()
        self._set_attrs(obj, data)
        if obj in self.session:
            # We don't want objects implicitly saved by overly smart sessions,
            # thanks
            self.session.expunge(obj)
        # If we have a parent_obj, attach obj to it
        if self.parent_obj is not None:
           self.attach_to_parent(obj)
        return obj

    def attach_to_parent(self, obj):
        #XXX This has to be more robust, what about other collection classes
        #    like setlikes, dicts, etc... perhaps the user should just subclass?
        other_side = getattr(self.parent_obj, self.remote_name)
        try:
            other_side.append(obj)
        except AttributeError:
            setattr(self.parent_obj, self.remote_name, obj)

    def join_transaction(self):
        if self.session.transaction:
            datamanager.join_transaction(self.session)
        
    def _set_dirty(self):
        if self.session.transaction:
            datamanager.mark_changed(self.session)
        self.session.flush()

SARepositoryFactory.register(
    SARepository, pred="get_mapper(resource) is not None"
    )
