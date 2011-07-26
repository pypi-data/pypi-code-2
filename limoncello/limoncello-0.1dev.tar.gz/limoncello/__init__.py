from sqlalchemy.orm import class_mapper, object_mapper
from sqlalchemy.schema import ColumnDefault, Sequence, DefaultClause
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.properties import ColumnProperty

#from sqlalchemy.orm.exc import UnmappedError

__all__ = ["get_mapper", "get_foreign_keys", "get_other", "get_remote_name", "primary_key_property_names",
"get_real_column", "get_remote_name", "get_default", "have_empty_string_as_default", "version_id_name"]

def get_mapper(obj):
    """
    returns the mapper independent whether you pass the mapped class or one of its instances
    """
    try: return class_mapper(obj)
    except:
        try: return object_mapper(obj)
        except: return None


def get_foreign_keys(prop):
    """simple compat for get_foreign_keys, I think in newer SA version this can also be achieved using the Inspector"""
    # This wrapper is to support both SA 0.5 and <
    try:
        return prop._foreign_keys # 0.5
    except AttributeError:
        try:
            return prop.foreign_keys # 0.4
        except AttributeError:
            return [c for c in prop.local_side if getattr(c, 'foreign_keys' ,None)]
            #0.6.4
            
    #XXX Why did SA "privatize" foreign_keys??

def primary_key_property_names(obj):
    """
    return the primary_key_property_names    
    in SA 0.7 you should use the inspector for that.
    """
    mapper = get_mapper(obj)
    assert mapper
    return [p.key for p in mapper.iterate_properties if hasattr(p,"columns")\
       and len([c for c in p.columns if c.primary_key])>0]

def version_id_name(obj):
    mapper = get_mapper(obj)
    assert mapper
    col = mapper.version_id_col
    if col:
        return col.key



def get_other(prop):
    """
    for a relation return the class at the remote end.
    >>> from limoncello.tests.model import Movie
    >>> prop = Movie.director
    >>> get_other(prop)
    <class 'limoncello.tests.model.Movie'>
    """
    return prop.mapper.class_

def get_remote_name(prop):
    """
    return the name of the reverse relation
    >>> from limoncello.tests.model import Movie
    >>> prop = Movie.director.property
    >>> get_remote_name(prop)
    'movies'
    """
    remote_name = None
    if prop._reverse_property:
        if isinstance(prop._reverse_property, set):
            # SA 0.5.1
            rps = list(prop._reverse_property)
            if len(rps) == 1:
                remote_name = rps[0].key
            else:
                msg = ("Did not expect several remote properties " + `rps` +
                       "Please file a bug report and include this traceback")
                raise AssertionError(msg)
        else:
            # SA < 0.5.1
            remote_name = prop._reverse_property.key
    return remote_name#

def get_real_column(col):
    """
    can handle aliasings properly, use this functions to get the original columns which
    might feature more reflected properties
    >>> from limoncello.tests.model import Movie, country_a
    >>> get_real_column(Movie.title.property)
    Column('title', Unicode(length=None), table=<movie>, nullable=False)
    >>> get_real_column(Movie.title.property.columns[0])
    Column('title', Unicode(length=None), table=<movie>, nullable=False)
    >>> aliased_column=country_a.columns['name']
    >>> aliased_column is get_real_column(aliased_column)
    False
    >>> get_real_column(aliased_column)
    Column('name', String(length=None, convert_unicode=False, assert_unicode=None, unicode_error=None, _warn_on_bytestring=False), table=<country>)
    """
    if isinstance(col, InstrumentedAttribute):
        col=col.property
    if isinstance(col, ColumnProperty):
        col=col.columns[0]
    if hasattr(col, 'base_columns') and len(col.base_columns)==1:
        return iter(col.base_columns).next()
    return col

def get_default(column):
    """
        return the default value of column, also considers server_defaults
    """
    resource = get_real_column(column)
    if isinstance(column.default, ColumnDefault):
        return column.default
    if hasattr(column, 'server_default') and column.server_default!=None:
        return column.server_default
    return None
            
def have_empty_string_as_default(resource):
    """decides, whether the column has the empty string as default,
    if the empty string is the default, it is a good hint, that
    nontrivial values (length >0) are not required
    """
    default=get_default(resource)
    if isinstance(default, ColumnDefault):
        default=resource.default.arg
        if not callable(default):
            return default==''
    if hasattr(default, 'arg') and hasattr(default.arg,'text'):
        return default.arg.text in [u"''::character varying", u"''::text"]
    return False
