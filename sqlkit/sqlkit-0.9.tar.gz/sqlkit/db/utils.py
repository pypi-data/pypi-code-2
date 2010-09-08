# Copyright (C) 2005-2010, Sandro Dentella <sandro@e-den.it>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
.. _register_utils:

Utilities
=========

Hooks and Layout are the core for any customization. If you customize a
Mask, chances are you would like to use that customization, any time you open
that table, or you may need several different customization (eg. employees,
manager may share some fields and differ on other fields).

The following utilities give you the possibility to register Hooks and Layout
to make them available to any sqlwidget to which no Hook/Layout is passed.

Each time you register a hook/layout/class you can specify a nickname (eg.:
customer/provider)

Hooks
-----

.. autofunction::  register_hook

.. autofunction::  unregister_hook

.. autofunction::  get_hook

Layout
------

.. autofunction::  register_layout

.. autofunction::  unregister_layout

.. autofunction::  get_layout

Classes
-------

Classes can be registered as well. If you register a class, all the times you
pass a table to a sqlwidget, the class will be used, so that ll relations will
be available as well. This is particularly usefull in case you use
:ref:`RecordInMask` that can open a table that may use a layout with m2m/m2o
nested table that would result as unknown if the table was reflected from the
db.

.. autofunction::  register_class

.. autofunction::  get_class

Database
--------

.. autofunction::  get_differences


Descr
-----
This module provide a bare simple Class to help creating 
__str__ and __repr__ for tables, using _sqlkit_table.format field


tables
------

tables dictionary is a place where sqlkit looks for search_field and
format for tables (see: ref:`sqlkit_model`).

You can set values directly using TableDescr class or implicitely via
database editing (``sqledit -c url``)
"""

import re

from sqlalchemy import Table, orm
from sqlalchemy.exc import OperationalError, ProgrammingError

from defaults import register_hook, get_hook, register_layout, get_layout, register_class, \
     get_class, unregister_hook, unregister_layout

########   descriptor
from sqlkit.misc.utils import Container

class MissingMetadata(Exception): pass

class Descr(object):
    """
    Simple class that provide default __init__ and __str__ to be
    mixed when building classes with declarative layer

    __str__ will use 'format' description from database _sqlkit_fields
    """
    def __init__(self, **kw):
        for key, val in kw.iteritems():
            setattr(self, key, val)
        if not hasattr(self, '__tablename__'):
            self.__tablename__ = self.__table__.name
    
    def __str__(self):
        from sqlkit.db.utils import tables

        if not hasattr(self, '__tablename__'):
            self.__tablename__ = self.__table__.name
    
        try:
            if not self.__tablename__ in tables:
                format = get_description(self.__table__, attr='format')

            return tables[self.__tablename__].format % DictLike(self)
        except:
            return "<%s - %s>" % (self.__class__.__name__, hex(id(self)))

    def __getitem__(self, key):
        return getattr(self, key) or ''

    __repr__ = __str__
    
class DictLike(object):
    """
    simple way to enable %(field_name)s lookup in classes
    used to allow correct use of 'format'. None is casted to empty string
    """
    def __init__(self, obj):
        self.obj = obj
        
    def __getitem__(self, key):
        """
        Cast all None values to '' otherwise the lookup can be scattered with 'None'
        as %(field_name)s would render as 'None' a None value
        """
        return getattr(self.obj, key, '') or ''

class Tables(Container):
    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            try:
                table = TableDescr(key, metadata=db.metadata)
                return table
            except Exception, e:
                raise MissingMetadata("No metadata defined in sqlkit.db.utils")
            

tables = Tables()

class TableDescr(object):
    """
    Format may be eather a normal python format string
    (eg.: "%(title)s - %(year)s")
    in which case each prenthesized token must be a field_name
    or a simple string that again must be a field_name
    'table' may be a string or a sqlalchemy.Table object

    Metadata is not necessary to pick primary key or when autoloading is
    required unless a Table object is given

    Format string passed via TableDescr take precedence over format string
    present in the database (dbformat).

    self.format is always a proper format string
    self.attrs comprises pkey so that can be used for completion
    self.search: this is the field that will be searched for in a foreign
    key context
    """
    pattern = '%\((\w+)\)'
    def __init__(self, table, format=None, pk=None, metadata=None):
        global tables

        if isinstance(table, Table):
            self.table = table
            table_name = table.name

        elif isinstance(table, basestring):
            table_name = table

        elif hasattr(table, 'original'):  # A Table.alias()
            self.table = table.original
            table_name = table.original.name


        self.table_name = table_name
#        self.format = format
        self.metadata = metadata
        
        tables[table_name] = self

        self.description, dbformat = self.guess_description()

        if format:
            self.set_format(format)
        elif dbformat:
            self.set_format(dbformat)
        else:
            self.set_format(self.description)

        ## I want self attr to have pkey, that's handy for completion
        if not pk:
            self.add_pk()
        else:
            if pk not in self.attrs:
                self.attrs.insert(0, pk)

    def get_attrs_from_format(self, format):
        """
        Used when format is 
        """
        m = re.findall(self.pattern, format)
        if m:
            return m
        else:
            return [format]
        
    def set_format(self, format):
        m = re.findall(self.pattern, format)
        ## self.attrs is use to get the minimum possible info when completing
        if m:
            self.attrs = m
            self.format = format
        else:
            self.attrs = [format]
            self.format = "%%(%s)s" % format
            self.search = format

    def add_pk(self):

        table = self.get_table()
        pkeys = table.primary_key.columns

        for field in pkeys:
            if field.name not in self.attrs:
                self.attrs.insert(0, field.name)
                
    def get_table(self):
        """
        return the sqlalchemy.Table or try to get it from metadata
        """

        try:
            return self.table
        except AttributeError:
            if not self.metadata:
                raise MissingMetadata("Description  for '%s' cannot be guessed" % self.table_name)
        
        ## first time we meet this table  -> inspect w/ autoload
        return Table(self.table_name, self.metadata, autoload=True)

        

    def guess_description(self):
        """look if a description field is defined, if not use introspection
        return the description field if mode == return otherwise call set_fromat

        """
        table = self.get_table()
        description, format = get_description_from_sqlkit(table)
        if description:
            #self.set_format(format)
            return description, format
        descr_exists = False
        for field_name in table.c.keys():
            if re.search("string|text|char", table.c[field_name].type.__class__.__name__, re.I):
                found_field = field_name
                break

        return field_name, format
        
    def __str__(self):
        return "table: %s - description: %s\n    format: %s" % (self.table_name, self.description,
                                                            self.format)

    def __repr__(self):
        return "table: %s - format: %s" % (self.table_name, self.format)


def get_table_name(table):
    if isinstance(table, Table):
        table_name = table.name
                
    elif isinstance(table, basestring):
        table_name = table

    elif hasattr(table, 'original'):  # A Table.alias()
        table_name = table.original.name
        
    return table_name

def get_description(table, metadata=None, attr='attrs'):

    table_name = get_table_name(table)
    try:
        return getattr(tables[table_name], attr)
    except MissingMetadata, e:
        if isinstance(table, Table):
            return getattr(TableDescr(table), attr)
        return getattr(TableDescr(table_name, metadata=metadata), attr)
    
def get_description_from_sqlkit(table, metadata=None):
    """
    get the description to use in completion and __str__ from database
    table _sqlkit_table
    """
    if isinstance(table, Table):
        metadata = table.metadata

    SQL = """SELECT search_field, format
             FROM _sqlkit_table WHERE name = '%s'""" % table.name
    try:
        res_proxy = metadata.bind.execute(SQL, table=table.name)
        descr = res_proxy.fetchone()
        if not descr:
            descr = None, None
    except (OperationalError, ProgrammingError), e:  #_sqlkit_table is not defined
        descr = (None, None)
    return descr

def get_labels_and_tips_from_sqlkit(table, metadata=None):
    """
    get the labels and tips to use in label_map from
    table _sqlkit_field
    """
    if isinstance(table, Table):
        metadata = table.metadata
        table_name = table.name
    else:
        table_name = table
        
    SQL = """SELECT table_name, name, description, help_text
             FROM _sqlkit_field WHERE table_name = '%s'""" % table_name
    descr = {}
    try:
        res_proxy = metadata.bind.execute(SQL, table=table_name)
        for record in res_proxy.fetchall():
            descr[record.name] = (record.description, record.help_text)
    except (OperationalError, ProgrammingError), e:
        #_sqlkit_field is not defined
        pass
    return descr

###################


def get_differences(obj):
    """
    show differences between old and new version of an object
    this is a generator, you should use as in::

       for field_name, old_value, new_value in get_differences(obj):
           print 'field   %s changed from %s, to %s' % (field_name, old_value, new_value)

    :param obj: the object to look for changes

    this function uses ``sqlalchemy.orm.attributes.get_history`` but differs in 2 ways:

      * it only yield *changed* values
      * it returns the simple value (not a list) if the property is not a RelationProperty
        with direction MANYTOMANY or ONETOMANY (i.e.a collection)
    
    """

    session = orm.object_session(obj)
    mapper = orm.class_mapper(obj.__class__)
    for prop in mapper.iterate_properties:
        new = None
        old = None

        try:
            new, unchanged, old =  orm.attributes.get_history(obj, prop.key)
        except AttributeError, e:
            # sqla 0.5.0 -> 0.5.1
            new, unchanged, old =  orm.attributes.get_history(
                orm.attributes.instance_state(obj), prop.key)
        if new or old:
            ## Not sure about this code. I don't want to have to cope with
            ## a list if there is no need for that (i.e. is not a collection)
            if isinstance(prop, orm.properties.RelationProperty) and (
                prop.direction.name in ('MANYTOMANY', 'ONETOMANY')):
                yield prop.key, old, new
            else:
                try:
                    old = old[0]
                except (TypeError, IndexError):
                    old = None
                    
                try:
                    new = new[0]
                except (TypeError, IndexError):
                    new = None
                    
                yield prop.key, old, new

def get_history(obj, field_name, session=None):
    """
    show the history of a field of an object

    :param obj: the object to look for history
    :param field_name: the field name of which we want to know the history
    :return: new, unchanged, old
    """

    mapper = orm.class_mapper(obj.__class__)
    for prop in mapper.iterate_properties:

        if prop.key == field_name:

            try:
                try:
                    new, unchanged, old =  orm.attributes.get_history(obj, prop.key)
                except AttributeError, e:
                    # sqla 0.5.0 -> 0.5.1
                    new, unchanged, old =  orm.attributes.get_history(
                        orm.attributes.instance_state(obj), prop.key)
                if isinstance(prop, orm.properties.RelationProperty) and (
                    prop.direction.name in ('MANYTOMANY', 'ONETOMANY')):
                    return new, unchanged, old
                else:
                    return new and new[0] or '',  unchanged and unchanged[0] or '', old and old[0] or ''

            except Exception, e:
                pass
            
def clean_for_markup(text):
    """
    quote string from undesired chars in pango markup
    """
    from gobject import markup_escape_text
    
    if isinstance(text, (tuple, list)):
        text = [markup_escape_text(str(item)) for item in text]
    else:
        text = markup_escape_text(str(text))
    return str(text)


def get_fields(table, metadata=None, name=True):
    """
    return all field_names for this table
    table may be a sqlalchemy.Table or a table_name in which case a metadata
    must be provided as well.

    If a registered class is found, all properties are returned, i.e. also
    relation properties (PropertyLoaders). This may change...?
    """
    # first try if a registered class exists
    class_ = get_class(table)

    if class_:
        mapper = orm.class_mapper(class_)
        if name:
            return mapper.c.keys()
        else:
            return [c for c in mapper.c]
    else:
        if not isinstance(table, Table):
            if not metadata:
                raise MissingMetadata("A metadata must be provided as autoload is needed")
            try:
                table = Table(table, metadata, autoload=True)
            except Exception, e:
                e.message = "Missing table: %s" % table
                raise e
        if name:
            return table.c.keys()
        else:
            return [c for c in table.c]


if __name__ == '__main__':
    from sqlkit.db import proxy

    db = proxy.DbProxy(engine="sqlite://///misc/src/hg/py/sqlkit4/doc/db/movies.sqlite")
    movie = Table('movie', metadata=db.metadata, autoload=True)

    #t = TableDescr('movie', '%(dirctor_id)s - (%(nation)s)', metadata=db.metadata)

    tables['movie'].attrs
    print get_description(movie, attr='format')
    print tables.movie
    print get_description('movie', metadata=db.metadata)
    print get_description('movie', metadata=db.metadata, attr='format')    


