from inspect import isclass
import logging
from types import NoneType

from sqlalchemy import types, Column, func, select
from sqlalchemy.orm.interfaces import MANYTOONE, ONETOMANY, MANYTOMANY
from sqlalchemy.orm.properties import ColumnProperty, PropertyLoader,\
                                      SynonymProperty
from sqlalchemy.schema import ColumnDefault, Sequence, DefaultClause

from rum import fields
from rumalchemy.util import get_mapper, get_foreign_keys, version_id_name, get_remote_name, get_other

__all__ = ["SAFieldFactory"]

log = logging.getLogger(__name__)

get = fields.FieldFactory.get.im_func

def get_real_column(col):
    if hasattr(col, 'base_columns') and len(col.base_columns)==1:
        return iter(col.base_columns).next()
    return col
def get_default(resource):
    resource = get_real_column(resource)
    if isinstance(resource.default, ColumnDefault):
        return resource.default
    if hasattr(resource, 'server_default') and resource.server_default!=None:
        return resource.server_default
    return None
            
def have_empty_string_as_default(resource):
    default=get_default(resource)
    if isinstance(default, ColumnDefault):
        default=resource.default.arg
        if not callable(default):
            return default==''
    if hasattr(default, 'arg') and hasattr(default.arg,'text'):
        return default.arg.text in [u"''::character varying", u"''::text"]
    return False

    
class SAFieldFactory(fields.FieldFactory):
    type_map = {
        types.String:      fields.String,
        types.Integer:     fields.Integer,
        types.Numeric:     fields.Decimal,
        types.Date:        fields.Date,
        types.DateTime:    fields.DateTime,
        types.Time:        fields.Time,
        types.Boolean:     fields.Boolean,
        types.Text:        fields.Text,
        types.UnicodeText: fields.UnicodeText,
        types.Unicode:     fields.Unicode,
        types.Binary:      fields.Binary
    }

    def __init__(self, repositoryfactory=None):
        self.repositoryfactory = repositoryfactory
        super(SAFieldFactory, self).__init__()

    @classmethod
    def register_field_for_type(cls, field, type, prio=0):
        get.when((cls,Column,type), prio)(lambda s,r,a,ar: field)


    @staticmethod
    def _get_remote_name(prop):
        return get_remote_name(prop)


    #
    # before methods to set arguments for the fields' constructors
    #
    @get.before("hasattr(attr, 'key') and not 'name' in args")
    def _set_field_name(self, resource, attr, args):
        args['name'] = attr.key
        
    @get.before((Column,))
    def _set_requiredness(self, col, attr, args):
        args['required'] = not col.nullable and not have_empty_string_as_default(col)
        
    @get.before((Column,types.Time))
    @get.before((Column,types.DateTime))
    def _set_has_timezone(self, col, attr, args):
        args['has_timezone'] = attr.timezone
    
    
    @get.before(
        "isinstance(attr, PropertyLoader) and "
        "attr.viewonly==True"
    )
    def _set_read_only_for_property_loader(self, col, attr, args):
        args['read_only']=True

    @get.before(
        "isinstance(resource, Column) and "
        "have_empty_string_as_default(resource)"
        )
    def _set_empty_default(self, col, attr, args):

        args['default'] = fields.NoDefault


    @get.before(
        "isinstance(resource, Column) and "
        "isinstance(resource.default, ColumnDefault)"
        )
    def _set_default(self, col, attr, args):
        if not "default" in args:
            default = col.default.arg
            if callable(default):
                args['default'] = lambda: default(None)
            else:
                args['default'] = default
    @get.before(
        "isinstance(resource, Column) and "
        "resource.default is None"
        )
    def _set_default(self, col, attr, args):
        #server defaults
        default = get_default(col)
        if hasattr(default, 'arg') and hasattr(default.arg, 'text'):
            
            default=default.arg.text
            if default.find('::')>0:
                for type_ in ['text', 'character varying']:
                    if default.endswith('::'+type_):
                        candidate=default[1::(-len(type_)-2)]
                        if default=="'" +candidate+"'"+type_:
                            args['default']=candidate
                            break
            else:
                if set("0123456789").issuperset(set(default)):
                    args['default']=default

    @get.before(
        "isinstance(resource, Column) and "
        "isinstance(resource.default, Sequence)"
        )
    def _set_auto_on_col_with_sequence(self, col, attr, args):
        args['auto'] = True

    @get.before(
        "isinstance(resource, Column) and hasattr(attr, 'length')"
        )
    def _set_length(self, col, attr, args):
        args['length'] = attr.length

    @get.before('''isinstance(resource, Column) and\
        hasattr(self.repositoryfactory, "session_factory") and\
        self.repositoryfactory.session_factory.bind.dialect.name.startswith("postgres")''')
    def _postgresql_reflect_description(self, col, attr, args):
          connection = self.repositoryfactory.session_factory.connection()
          col= get_real_column(col)
          schema=col.table.schema or 'public'
          column_name=col.name
          table_name = col.table.name
          r=connection.execute('''select coalesce(col_description(pg_class.oid, pg_attribute.attnum),'')
              from pg_attribute, pg_class, pg_type, pg_namespace
              where    
                    pg_attribute.atttypid = pg_type.oid
                    and pg_attribute.attrelid = pg_class.oid
                    and pg_namespace.nspname=%s
                    and pg_namespace.oid = pg_class.relnamespace
                    and pg_class.relname=%s
                    and pg_attribute.attname=%s;''',  (schema,table_name,column_name))
          r=list(r)
          if len(r)==1:
              args['description']= r[0][0]
          else:
              log.warn('could not fetch comment for column %s '% (column,))

    #
    # Wrappers around fields
    #
    @get.when(
        "isinstance(resource, Column) and isinstance(attr, types.TypeEngine) "
        "and resource.primary_key", prio=10
        )
    def _wrap_primary_key(next_method, self, col, attr, args):
        """
        Column is a primary key. Call the next method to see which field
        it is and wrap it with a field.PrimaryKey.
        This has a higher prio than _wrap_with_ForeignKey so PK wraps FK
        """
        type_args = args.copy()
        type_cls = next_method(self, col, attr, type_args)
        args['type'] = type = self.instantiate_field(type_cls, **type_args)
        if isinstance(type, fields.Integer) and not type.has_default and not\
           isinstance(col.default, Sequence):
            # Work around SA autoincrement bug: if field is an integer
            # pk assume it autoincrements so query db for next unused id
            def get_next_id():
                session = self.repositoryfactory.session_factory()
                query = select([func.max(col)])
                return (session.execute(query).scalar() or 0) + 1
            type.default = get_next_id
            args.setdefault('auto', True)
        else:
            args.setdefault('auto', False)
        return fields.PrimaryKey

        
    @get.when(
        "isinstance(resource, Column) and isinstance(attr, types.TypeEngine) "
        "and len(get_foreign_keys(resource)) > 0", prio=5
        )
    def _wrap_foreign_key(next_method, self, col, attr, args):
        """
        Column is a foreign key. Call the next method to see which field
        it is and wrap it with a field.ForeignKey.
        """
        type_args = args.copy()
        type_cls = next_method(self, col, attr, type_args)
        args['type'] = self.instantiate_field(type_cls, **type_args)
        return fields.ForeignKey


    @get.when(
        "isinstance(attr, Column) and "
        "attr.key == version_id_name(resource)",
        prio=4
        )
    def _wrap_version_col(next_method, self, col, attr, args):
        type_args = args.copy()
        type_cls = next_method(self, col, attr, type_args)
        args['type'] = self.instantiate_field(type_cls, **type_args)
        return fields.VersionID


    @get.when(
        "isinstance(attr, Column) and "
        "attr is get_mapper(resource).polymorphic_on",
        prio=4
        )
    def _wrap_poly_discriminator(next_method, self, resource, col, args):
        """
        Match the case when the column we're dealing with is the resource's
        polymorphic discrimnator.
        Note that we need to match a little earlier in the recursive descent
        (when ``resource`` is the mapped class) since we need a ref to it to
        see which is the poly discriminator.
        """
        type_args = args.copy()
        type_cls = next_method(self, resource, col, type_args)
        args['type'] = self.instantiate_field(type_cls, **type_args)
        return fields.PolymorphicDiscriminator




    #
    # The following rules control the recursive descent on a mapped class:
    #    1) _fields_for_mapped_class matches a mapped class when no attr is
    #       specified. It builds a FieldList by calling recursively the factory
    #       with (resource, property) pairs for each property of resource
    #    2) These properties will either be ColumnProperties or PropertyLoaders.
    #       2.1) If a ColumnProperty, recursive descent on the first Column
    #       2.2) If a PropertyLoader, figure out the relation type
    #    3) _fields_for_column will match recursive calls made by 2.1 and
    #       continue the recursive descent passing (column, type) so the
    #       rules that match each type can kick in.


    @get.when(
        "isclass(resource) and get_mapper(resource) is not None and "
        "attr is None",
        prio=-1)
    def _fields_for_mapped_class(self, resource, attr, args):
        """
        Matches calls like (resource,None) which means that we're operating
        on a resource, not on it's properties/attributes.
        Begin a recursive descent passing (resource, attr_name) for each
        attribute.
        """
        #XXX: It should be documented somewhere that FieldFactories
        #     should pass the attr. names as a string sometime during
        #     the recursive descent so rules that match (resource, attr_name)
        #     can kick in
        #     -> This applies also to other factories like viewfactories
        properties = get_mapper(resource).iterate_properties
        args['fields'] = filter(
            lambda f: f is not None and not f.name.startswith('_'),
            [self(resource, prop.key) for prop in properties]
            )
        return fields.FieldList
        
    @get.when(
        "isclass(resource) and get_mapper(resource) is not None and "
        "isinstance(attr, basestring)",
        prio=-1)
    def _get_property_from_mapper(self, resource, attr, args):
        """
        Matches calls like (resource, attr_name). Fetches the property from
        the mapper and does a recursive call passing it as ``attr`` so other
        rules can match the property by type.
        """
        prop = get_mapper(resource).get_property(attr)
        return self.get(resource, prop, args)


    @get.when("isinstance(attr, ColumnProperty)")
    def _fields_for_ColumnProperty(self, resource, attr, args):
        """
        Matches ColumnPropertys when they appear as ``attr`` (call made by
        _get_property_from_mapper). Continues descending passing the first
        Column of the property as ``attr``.
        """
        return self.get(resource, attr.columns[0], args)

    @get.when("isinstance(attr, SynonymProperty)")
    def _fields_for_SynonymProperty(self, resource, attr, args):
        """
        Matches SynonymProperties when they appear as ``attr`` (call made by
        _get_property_from_mapper).
        Returns the property this synonym is referring to.
        """
        return self.get(resource, attr.name, args)

    @get.when(
        "isinstance(attr, PropertyLoader) and attr.direction == MANYTOONE",
        prio=-1)
    def _fields_for_many_to_one(self, resource, attr, args):
        """
        Matches PropertyLoaders when they manage a many-to-one relation.
        """
        is_req = lambda c: not c.nullable
        other = get_other(attr)
        args.update(
            other = other,
            remote_name = self._get_remote_name(attr),
            required = bool(filter(is_req, get_foreign_keys(attr)))
            )
        if len(attr.local_side)==1 and not 'default' in args:
            def default_getter():
                column = iter(attr.local_side).next()
                column_default = get_default(column)
                default = get_default(column)
                if isinstance(default, DefaultClause):
                    #very common case
                    #we are very careful here, as defaults can also be function calls
                    repository = self.repositoryfactory(other)
                    print repository
                    try:
                        default=int(default.arg.text)
                        print default
                        default = repository.get(default)
                        return default
                    except ValueError:
                        pass
                    return None
            args['default']=default_getter
        return fields.ToOneRelation



    @get.when(
        "isinstance(attr, PropertyLoader) and "
        "attr.direction in [ONETOMANY, MANYTOMANY]",
        prio=-1
        )
    def _fields_for_list_collection(self, resource, attr, args):
        """
        Matches PropertyLoaders when they manage a {one,many}-to-many relation
        mapped as a list
        """
        is_req = lambda c: not c.nullable
        args.update(
            other = attr.mapper.class_,
            remote_name = self._get_remote_name(attr),
            #required = bool(filter(is_req, get_foreign_keys(attr)))
            )
        return fields.List

    @get.when("isinstance(attr, Column)")
    def _fields_for_column(self, resource, col, args):
        """
        Matches Columns when they appear as ``attr`` (call made by
        _fields_for_ColumnProperty). Continues descending on
        (column, column_type) so rules can match the column type.
        """
        return self.get(col, col.type, args)

    @get.when(
        "isinstance(attr, Column) and attr.info.get('rum', {}).get('field')")
    def _explicit_field_from_info(self, resource, col, args):
        """
        Matches Columns when they appear as ``attr`` and they have a
        'rum' key in their info dict. Stops the recursive descent (ignoring
        rules that match column type) since it means that the user wants to
        override the guessing and provide their own Field and its arguments.
        """
        explicit_args = col.info['rum'].copy()
        field_class = explicit_args.pop('field')
        args.update(explicit_args)
        if isinstance(field_class, basestring):
            field_class = getattr(fields, field_class)
        return field_class

# Register default rules to generate fields for each column type
for type, field in SAFieldFactory.type_map.iteritems():
    SAFieldFactory.register_field_for_type(field, type, -1)
