# -*- coding: utf-8 -*-
from django.db.models import ForeignKey, OneToOneField, ManyToManyField
from django.db.models.fields import *

# need to be after django.db.models.fields import *
from decimal import Decimal
from datetime import datetime, time, date, timedelta
from functools import wraps
import threading


class UnsupportedFieldError(Exception):
    "DynamicFixture does not support this field."

class InvalidConfigurationError(Exception):
    "The specified configuration for the field can not be applied or it is bugged."

class InvalidManyToManyConfigurationError(Exception):
    "M2M attribute configuration must be a number or a list of DynamicFilters or model instances."

class BadDataError(Exception):
    "The data passed to a field has some problem (not unique or invalid) or a required attribute is in ignore list."

class DjangoHelper(object):

    @staticmethod
    def get_fields_from_model(model_class):
        return model_class._meta.fields

    @staticmethod
    def get_field_names_from_model(model_class):
        fields = DjangoHelper.get_fields_from_model(model_class)
        return [field.name for field in fields]

    @staticmethod
    def get_many_to_many_fields_from_model(model_class):
        return model_class._meta.many_to_many

    @staticmethod
    def get_related_model(field):
        return field.rel.to

    @staticmethod
    def field_has_choices(field):
        return field.choices and len(field.choices) > 0

    @staticmethod
    def field_has_default_value(field):
        return field.default != NOT_PROVIDED


class AutoDataFiller(object):

    def __init__(self):
        self.__data_controller_map = {} # key => counter
        self.__locks = {} # key => lock

    # synchronized by key
    def next(self, key, cast=lambda data: data):
        if key not in self.__data_controller_map:
            self.__data_controller_map[key] = 0
            self.__locks[key] = threading.RLock()
        self.__locks[key].acquire()
        self.__data_controller_map[key] += 1
        value = cast(self.__data_controller_map[key])
        self.__locks[key].release()
        return value


class DataFixture(object):
    def new(self, field): raise NotImplementedError()


class DefaultDataFixture(DataFixture):

    def __init__(self):
        self.filler = AutoDataFiller()

    # numbers
    def integerfield_config(self, field, key): return self.filler.next(key)
    def smallintegerfield_config(self, field, key): return self.integerfield_config(field, key)
    def positiveintegerfield_config(self, field, key): return self.integerfield_config(field, key)
    def positivesmallintegerfield_config(self, field, key): return self.integerfield_config(field, key)
    def bigintegerfield_config(self, field, key): return self.integerfield_config(field, key)
    def floatfield_config(self, field, key): return self.filler.next(key, lambda data: float(data))
    def decimalfield_config(self, field, key):
        data = self.filler.next(key)
        number_of_digits = field.max_digits - field.decimal_places
        max_value = 10 ** number_of_digits
        data = data % max_value
        return Decimal(str(data))

    #string
    def charfield_config(self, field, key):
        data = self.filler.next(key, cast=lambda data: str(data))
        data[:field.max_length]
        return data
    def textfield_config(self, field, key): return self.charfield_config(field, key)
    def slugfield_config(self, field, key): return self.charfield_config(field, key)
    def commaseparatedintegerfield_config(self, field, key): return self.charfield_config(field, key)

    # boolean
    def booleanfield_config(self, field, key): return False
    def nullbooleanfield_config(self, field, key): return None

    # time related
    def datefield_config(self, field, key):
        return self.filler.next(key, cast=lambda data: (date.today() - timedelta(days=data)))
    def timefield_config(self, field, key):
        return self.filler.next(key, cast=lambda data: (datetime.now() - timedelta(seconds=data)))
    def datetimefield_config(self, field, key):
        return self.filler.next(key, cast=lambda data: (datetime.now() - timedelta(seconds=data)))

    # formatted strings
    def emailfield_config(self, field, key): return 'a%s@dynamicfixture.com' % (self.filler.next(key, cast=lambda data: str(data)),)
    def urlfield_config(self, field, key): return 'http://dynamicfixture%s.com' % (self.filler.next(key, cast=lambda data: str(data)),)
    def ipaddressfield_config(self, field, key):
        # TODO: better workaround (this suppose ip field is not unique)
        data = self.filler.next(key)
        a = '1'
        b = '1'
        c = '1'
        d = data % 256
        return '%s.%s.%s.%s' % (a, b, c, str(d))
    def xmlfield_config(self, field, key): return '<a>%s</a>' % (self.filler.next(key, cast=lambda data: str(data)),)

    # files
    def filepathfield_config(self, field, key): return self.filler.next(key, cast=lambda data: str(data))
    def filefield_config(self, field, key): return self.filler.next(key, cast=lambda data: str(data))
    def imagefield_config(self, field, key): return self.filler.next(key, cast=lambda data: str(data))

    def get_key_from_instance_field(self, model_class, field):
        return model_class.__name__ + '.' + field.name

    def field_fixture_template(self, field_class):
        return '%s_config' % (field_class.__name__.lower(),)

    def field_fixture_factory(self, field_class):
        try:
            fixture = self.field_fixture_template(field_class)
            getattr(self, fixture)
            return fixture
        except AttributeError:
            if len(field_class.__bases__) > 0:
                parent_class = field_class.__bases__[0] # field must not have multiple inheritance
                return self.field_fixture_factory(parent_class)
            else:
                return None

    def new(self, field):
        config = self.field_fixture_factory(field.__class__)
        is_supported_field = config != None
        if is_supported_field:
            key = self.get_key_from_instance_field(field.model, field)
            data = eval('self.%s(field, "%s")' % (config, key,))
        else:
            if field.null:
                data = None # a workaround for versatility
            else:
                raise UnsupportedFieldError(field.model, field)
        return data


DATA_FIXTURE = DefaultDataFixture()

class DynamicFixture(object):

    def __init__(self, fill_nullable_fields=True, ignore_fields=[], number_of_laps=1, model_path=[], data_fixture=None, **kwargs):
        self.fill_nullable_fields = fill_nullable_fields
        self.ignore_fields = ignore_fields
        self.number_of_laps = number_of_laps
        self.model_path = model_path
        if data_fixture is None:
            self.data_fixture = DATA_FIXTURE
        else:
            self.data_fixture = data_fixture
        self.kwargs = kwargs

    def _process_field_with_customized_fixture(self, field, fixture, persist_dependencies):
        if isinstance(fixture, DynamicFixture): # DynamicFixture
            next_model = DjangoHelper.get_related_model(field)
            if persist_dependencies:
                data = fixture.get(next_model)
            else:
                data = fixture.new(next_model, persist_dependencies=persist_dependencies)
        elif isinstance(fixture, DataFixture): # DataFixture
            next_model = DjangoHelper.get_related_model(field)
            data = fixture.new(next_model)
        elif callable(fixture): # callable with the field as parameters
            data = fixture(field)
        else: # attribute value
            data = fixture
        return data

    def _process_field_with_default_fixture(self, field, model_class, persist_dependencies):
        if field.null and not self.fill_nullable_fields:
            return None

        if isinstance(field, (ForeignKey, OneToOneField)):
            next_model = DjangoHelper.get_related_model(field)
            occurrences = self.model_path.count(next_model)
            if occurrences >= self.number_of_laps:
                data = None
            else:
                next_model_path = self.model_path[:]
                next_model_path.append(model_class)
                fixture = DynamicFixture(fill_nullable_fields=self.fill_nullable_fields,
                                         number_of_laps=self.number_of_laps,
                                         model_path=next_model_path,
                                         data_fixture=self.data_fixture)
                if persist_dependencies:
                    data = fixture.get(next_model)
                else:
                    data = fixture.new(next_model, persist_dependencies=persist_dependencies)
        else:
            if DjangoHelper.field_has_choices(field):
                data = field.choices[0][0]
            elif DjangoHelper.field_has_default_value(field):
                # TODO: deal with auto_now and auto_now_add for DateField
                if callable(field.default):
                    data = field.default() # datetime default can receive a function: datetime.now
                else:
                    data = field.default
            else:
                data = self.data_fixture.new(field)
        return data

    def _process_many_to_many_field(self, field, manytomany_field, fixture):
        next_model = DjangoHelper.get_related_model(field)
        if isinstance(fixture, int):
            amount = fixture
            for i in range(amount):
                next_instance = self.get(next_model)
                try:
                    manytomany_field.add(next_instance)
                except AttributeError: # M2M with trough: ManyRelatedManager
                    next_instance.save()
        elif isinstance(fixture, list):
            items = fixture
            for item in items:
                if isinstance(item, DynamicFixture):
                    next_instance = item.get(next_model)
                else:
                    next_instance = item
                try:
                    manytomany_field.add(next_instance)
                except AttributeError: # M2M with trough: ManyRelatedManager
                    next_instance.save()
        else:
            raise InvalidManyToManyConfigurationError(field, fixture)

    def new(self, model_class, persist_dependencies=True, **kwargs):
        kwargs.update(self.kwargs)
        instance = model_class()
        for field in DjangoHelper.get_fields_from_model(model_class):
            if isinstance(field, AutoField) and 'id' not in kwargs: continue
            if field.name in self.ignore_fields: continue
            if field.name in kwargs:
                config = kwargs[field.name]
                try:
                    data = self._process_field_with_customized_fixture(field, config, persist_dependencies)
                except Exception as e:
                    raise InvalidConfigurationError(model_class, field, e)
            else:
                data = self._process_field_with_default_fixture(field, model_class, persist_dependencies)
            setattr(instance, field.name, data)
        return instance

    def get(self, model_class, **kwargs):
        kwargs.update(self.kwargs)
        instance = self.new(model_class, **kwargs)
        try:
            instance.save()
        except Exception as e:
            print_field_values(instance)
            raise BadDataError(model_class, e)
        for field in DjangoHelper.get_many_to_many_fields_from_model(model_class):
            if field.name in kwargs.keys():
                manytomany_field = getattr(instance, field.name)
                fixture = kwargs[field.name]
                try:
                    self._process_many_to_many_field(field, manytomany_field, fixture)
                except Exception as e:
                    raise InvalidManyToManyConfigurationError(field, e)
        try:
            instance.save() # saving m2m fields
        except Exception as e:
            print_field_values(instance)
            raise BadDataError(model_class, e)
        return instance


# Wrappers
def new(model, fill_nullable_fields=True, ignore_fields=[], number_of_laps=1, persist_dependencies=True, **kwargs):
    d = DynamicFixture(fill_nullable_fields, ignore_fields, number_of_laps)
    return d.new(model, persist_dependencies=persist_dependencies, **kwargs)

def get(model, fill_nullable_fields=True, ignore_fields=[], number_of_laps=1, **kwargs):
    d = DynamicFixture(fill_nullable_fields, ignore_fields, number_of_laps)
    return d.get(model, **kwargs)

def print_field_values(model_instance):
    print('\n:: Model %s (%s)' % (model_instance.__class__.__name__, model_instance.id))
    for field in DjangoHelper.get_fields_from_model(model_instance.__class__):
        print('%s: %s' % (field.name, getattr(model_instance, field.name)))
    if model_instance.id is not None:
        for field in DjangoHelper.get_many_to_many_fields_from_model(model_instance.__class__):
            print('%s: %s' % (field.name, getattr(model_instance, field.name).all()))
