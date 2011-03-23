"""
Functions to automatically create (or modify) a formencode schema based
upon a sqlalchemy orm instance.
"""
import types
import warnings
import sqlalchemy.types as sa_types
import formencode
import formencode.validators as validators

def generate(allowed_fields, sql_fields):
    """
    Generate a formencode schema based on the sqlalchemy information
    available.
    """
    klass = types.ClassType('DynamicSchema', (formencode.Schema, ), {})
    klass.allow_extra_fields = True
    klass.filter_extra_fields = False
    
    for key in sql_fields.keys():
        if key not in allowed_fields:
            warnings.warn('test')
            continue
        
        validator = _create_validator(sql_fields[key])
        if validator is not None:
            klass.add_field(key, validator)
    return klass

def set_string_maxlength(schema_class, sql_fields):
    """
    Iterate over the sqlalchemy fields and set the matching field
    in the formencode schemaclass to accept a max number of chars if the
    validator is of type formencode.validators.String
    """
    for key in sql_fields.keys():
        if key in schema_class.fields:
            field = schema_class.fields[key]
            
            if isinstance(field, validators.String) and not field.max:
                field.max = sql_fields[key].properties.columns[0].type.length
                        
def _create_validator(field):
    """
    Create a validator for the given field.
    """
    validator = None
    if isinstance(field.type, (sa_types.Unicode, sa_types.String)):
        validator = _create_string_validator(field)
    
    elif isinstance(field.type, sa_types.Integer):
        validator = _create_integer_validator(field)
    
    elif isinstance(field.type, sa_types.Boolean):
        validator = _create_boolean_validator(field)

    else:
        print 'no validator created for field "%r"' % repr(field)
    return validator
    
def _create_string_validator(field):
    """
    Create a formencode.validators.String validator for string/unicode
    fields.
    """
    validator = validators.String
    return validator(max=field.type.length, not_empty=not field.nullable)

def _create_integer_validator(field):
    """
    Create a formencode.validators.Int for Integer types
    """
    validator = validators.Int
    if field.primary_key:
        return None
    return validator(not_empty=not field.nullable)

def _create_boolean_validator(field):
    """
    Create a validator for a boolean. formencode.validators.StringBool
    is used since we assume that a checkbox is used.
    """
    validator = validators.StringBool
    return validator(if_missing=None)