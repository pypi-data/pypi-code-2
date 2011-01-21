from urllib import urlretrieve
from random import choice
from string import letters
from random import randint

from django.db.models import fields
from django.core.files import File
from django.core.validators import MaxLengthValidator
from django.contrib.webdesign import lorem_ipsum


def get_or_create_random(model, **kwargs):
    """
    Returns an instance of model that matches the values passed in kwargs.
    If such an instance does not exist, creates a new one, filling its fields
    with the values provided in kwargs.
    Fields that are required and are not provided with values are filled with
    random values.
    """
    defaults = kwargs.pop('defaults', {})
    objects = model.objects.filter(**kwargs).order_by('?')
    if objects:
        return objects[0]
    else:
        params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
        # Use defaults only to create an instance, not to get an existing one
        params.update(defaults)
        for field in model._meta.fields:
            if not (field.name in params or field.null or field.blank or \
                field.has_default()):
                params[field.name] = fill_field(field)
        obj = model(**params)
        obj.save()
        return obj

def fill_field(field):
    """
    Fill a field with a random content based on its type.
    """
    internal_type = field.get_internal_type()
    try:
        return eval("random_%s(field)" % internal_type)
    except NameError:
        # TODO:
        # BigIntegerField, DecimalField, FloatField, IntegerField, PositiveIntegerField, PositiveSmallIntegerField, SmallIntegerField
        # BooleanField, NullBooleanField
        # CommaSeparatedIntegerField
        # EmailField
        # FileField, FilePathField
        # IPAddressField
        # SlugField
        # DateField, DateTimeField, TimeField
        # ManyToManyField, OneToOneField
        # URLField
        # XMLField
        raise NameError, "Don't know how randomly fill a %s" % internal_type    

def random_CharField(field):
    """
    Generates random char data for a CharField.
    Satisfies the MaxLengthValidator requirement of the field.
    """
    for validator in field.validators:
        if type(validator) == MaxLengthValidator:
            limit = validator.limit_value
    return "".join([choice(letters) for i in xrange(randint(1, limit))])

def random_TextField(field):
    """
    Generates a random number of paragraphs (maximum: 5) for a TextField.
    """
    limit = randint(1, 5)
    return "\n".join(lorem_ipsum.paragraphs(2, False))

def random_SlugField(field):
    """
    Generates random char data for a SlugField.
    """
    return random_CharField(field).strip().lower().replace(" ","_")
        
def random_ForeignKey(field):
    """
    Find or generate a random related object for a ForeignKey.
    """
    return get_or_create_random(field.related.parent_model)

def random_FileField(field):
    """
    Find or download a random image object for a FileField.
    """
    # TODO: Might be nice to differentiate between ImageField and FileField
    # TODO: Close the file at the end
    # TODO: Get a random image from flickr instead
    remote_path="http://blazingwolf.com/drupal6/files/random%20flame.jpg"
    local_path = 'tmp/random.jpg' # to not clutter the current folder
    # if not exists(local_path): 
    urlretrieve(remote_path, local_path)    
    f = open(local_path, 'r')
    f.read()
    return File(f)

