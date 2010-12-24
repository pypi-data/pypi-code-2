import re

from django.db.models import EmailField

field_replacers = {
    'AutoField': None,
    'ForeignKey': None,
    'ManyToManyField': None,
    'OneToOneField': None,
    'SlugField': None, # we probably don't want to change slugs
    'DateField': '"date"',
    'DateTimeField': '"datetime"',
    'BooleanField': '"bool"',
    'NullBooleanField': '"bool"',
    'IntegerField': '"integer"',
    'SmallIntegerField': '"small_integer"',
    'PositiveIntegerField': '"positive_integer"',
    'PositiveSmallIntegerField': '"positive_small_integer"',
}

# NB - order matters. 'address' is more generic so should be at the end.
charfield_replacers = [
    (r'(\b|_)full_name\d*', '"name"'),
    (r'(\b|_)first_name\d*', '"first_name"'),
    (r'(\b|_)last_name\d*', '"last_name"'),
    (r'(\b|_)user_name\d*', '"username"'),
    (r'(\b|_)username\d*', '"username"'),
    (r'(\b|_)name\d*', '"name"'),
    (r'(\b|_)email\d*', '"email"'),
    (r'(\b|_)town\d*', '"city"'),
    (r'(\b|_)city\d*', '"city"'),
    (r'(\b|_)county\d*', '"uk_county"'),
    (r'(\b|_)post_code\d*', '"uk_postcode"'),
    (r'(\b|_)postcode\d*', '"uk_postcode"'),
    (r'(\b|_)zip\d*', '"zip_code"'),
    (r'(\b|_)zipcode\d*', '"zip_code"'),
    (r'(\b|_)zip_code\d*', '"zip_code"'),
    (r'(\b|_)telephone\d*', '"phonenumber"'),
    (r'(\b|_)mobile\d*', '"phonenumber"'),
    (r'(\b|_)tel\d*\b', '"phonenumber"'),
    (r'(\b|_)state\d*\b', '"state"'),
    (r'(\b|_)address\d*', '"full_address"'),
]

def get_replacer_for_field(field):
    # Some obvious ones:
    if isinstance(field, EmailField):
        return '"email"'

    field_type = field.get_internal_type()
    if field_type == "CharField" or field_type == "TextField":
        # Guess by the name

        # First, go for complete match
        for pattern, result in charfield_replacers:
            if re.match(pattern + "$", field.attname):
                return result

        # Then, go for a partial match.
        for pattern, result in charfield_replacers:
            if re.search(pattern, field.attname):
                return result

        # Nothing matched.
        if field_type == "TextField":
            return '"lorem"'

        # Just try some random chars
        max_length = field.max_length
        return "lambda self, obj, field, val: self.faker.varchar(%d, field=field)" % max_length


    try:
        r = field_replacers[field_type]
    except KeyError:
        r = "UNKNOWN_FIELD"


    if r is None:
        return None

    return r

attribute_template = "        '%(attname)s': %(replacer)s,"
skipped_template   = "         # Skipping field %s"
class_template = """
class %(modelname)sAnonymizer(Anonymizer):

    model = %(modelname)s

    attributes = {
%(attributes)s
    }
"""

def create_anonymizer(model):
    attributes = []
    for f in model._meta.fields:
        replacer = get_replacer_for_field(f)
        if replacer is None:
            attributes.append(skipped_template % f.attname)
        else:
            attributes.append(attribute_template % {'attname': f.attname,
                                                    'replacer': replacer })
    return class_template % {'modelname':model.__name__,
                             'attributes': "\n".join(attributes) }

