from sqlalchemy.orm import class_mapper, object_mapper
from rum import app

#from sqlalchemy.orm.exc import UnmappedError

__all__ = ["get_mapper", "get_foreign_keys", "get_other", "get_remote_name"]

def get_mapper(obj):
    try: return class_mapper(obj)
    except:
        try: return object_mapper(obj)
        except: return None


def get_foreign_keys(prop):
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

def get_dialect_name():
    try:
        return app.repositoryfactory.session_factory.bind.dialect.name
    except AttributeError:
        return "GENERIC"

def get_other(prop):
    return prop.mapper.class_

def get_remote_name(prop):
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
    return remote_name