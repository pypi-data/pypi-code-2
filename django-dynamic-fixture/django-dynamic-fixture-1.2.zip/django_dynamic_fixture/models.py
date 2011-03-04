from django.db import models

class ModelA(models.Model):
    #id is a models.AutoField()

    # numbers
    integer = models.IntegerField(null=True, unique=True)
    smallinteger = models.SmallIntegerField(null=True, unique=True)
    positiveinteger = models.PositiveIntegerField(null=True, unique=True)
    positivesmallinteger = models.PositiveSmallIntegerField(null=True, unique=True)
    biginteger = models.BigIntegerField(null=True, unique=True)
    float = models.FloatField(null=True, unique=True)
    decimal = models.DecimalField(max_digits=5, decimal_places=4, null=True, unique=False)

    # strings
    string = models.CharField(max_length=100, null=True, unique=True)
    text = models.TextField(null=True, unique=True)
    slug = models.SlugField(null=True, unique=True)
    commaseparated = models.CommaSeparatedIntegerField(max_length=100, null=True, unique=True)

    # booleans
    boolean = models.BooleanField()
    nullboolean = models.NullBooleanField()

    # time related
    date = models.DateField(null=True, unique=True)
    datetime = models.DateTimeField(null=True, unique=True)
    time = models.TimeField(null=True, unique=True)

    # formatted strings
    email = models.EmailField(null=True, unique=True)
    url = models.URLField(null=True, unique=True)
    ip = models.IPAddressField(null=True, unique=False)
    xml = models.XMLField(null=True, unique=True)

    # files
    filepath = models.FilePathField(unique=True, blank=True)
    file = models.FileField(upload_to='.')
    image = models.ImageField(upload_to='.')

    # relationship
    selfforeignkey = models.ForeignKey('self', null=True)
    foreignkey = models.ForeignKey('ModelB', related_name='fk', null=True)
    onetoone = models.OneToOneField('ModelB', related_name='o2o', null=True)
    manytomany = models.ManyToManyField('ModelB', related_name='m2m')

    # generic field
    # TODO

class ModelB(models.Model):
    integer = models.IntegerField(null=True, default=3)
    string = models.CharField(max_length=5, null=True, choices=(('a', 'A'), ('b', 'B')))


class ModelC(models.Model):
    d = models.ForeignKey('ModelD', null=True)


class ModelD(models.Model):
    c = models.ForeignKey(ModelC, null=True)


class CustomDjangoField(models.IntegerField):
    pass

class NewField(models.Field):
    pass

class ModelE(models.Model):
    x = CustomDjangoField(null=False)
    y = NewField(null=True)

class ModelF(models.Model):
    z = NewField(null=False)

class ModelForNullableTest(models.Model):
    nullable = models.IntegerField(null=True)
    not_nullable = models.IntegerField(null=False)

class ModelForIgnoreListTest(models.Model):
    required = models.IntegerField(null=False)
    required_with_default = models.IntegerField(null=False, default=1)
    not_required = models.IntegerField(null=True)
    not_required_with_default = models.IntegerField(null=True, default=1)
