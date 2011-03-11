from django.test import TestCase
from django.db import models
from django.db import IntegrityError

from datetime import datetime, time, date
from decimal import Decimal

from django_dynamic_fixture.models import *
from django_dynamic_fixture import *


class NewCreateAModelInstanceTest(TestCase):

    def test_new_create_a_non_saved_instance_of_the_model(self):
        instance = new(ModelA)
        self.assertTrue(isinstance(instance, ModelA))
        self.assertEquals(None, instance.id)


class NewFullFillAttributesWithAutoDataTest(TestCase):

    def setUp(self):
        self.instance = new(ModelA)

    def test_new_fill_number_fields_with_1(self):
        self.assertTrue(isinstance(self.instance.integer, int))
        self.assertTrue(isinstance(self.instance.smallinteger, int))
        self.assertTrue(isinstance(self.instance.positiveinteger, int))
        self.assertTrue(isinstance(self.instance.positivesmallinteger, int))
        self.assertTrue(isinstance(self.instance.biginteger, int))
        self.assertTrue(isinstance(self.instance.float, float))

    def test_decimal_deal_with_max_digits(self):
        # max_digits=5, decimal_places=4
        # value 10 must be a problem, need to restart the counter
        for i in range(11):
            self.assertTrue(isinstance(self.instance.decimal, Decimal))

    def test_new_fill_string_fields_with_string_1(self):
        self.assertTrue(isinstance(self.instance.string, str))
        self.assertTrue(isinstance(self.instance.text, str))
        self.assertTrue(isinstance(self.instance.slug, str))
        self.assertTrue(isinstance(self.instance.commaseparated, str))

    def test_new_fill_boolean_fields_with_False_and_None(self):
        self.assertEquals(False, self.instance.boolean)
        self.assertEquals(None, self.instance.nullboolean)

    def test_new_fill_time_related_fields_with_current_values(self):
        self.assertTrue(date.today() >= self.instance.date)
        self.assertTrue(datetime.now() >= self.instance.time)
        self.assertTrue(datetime.now() >= self.instance.datetime)

    def test_new_fill_formatted_strings_fields_with_basic_values(self):
        self.assertTrue(isinstance(self.instance.email, str))
        self.assertTrue(isinstance(self.instance.url, str))
        self.assertTrue(isinstance(self.instance.ip, str))
        self.assertTrue(isinstance(self.instance.xml, str))

    def test_new_fill_file_fields_with_basic_strings(self):
        self.assertTrue(isinstance(self.instance.filepath, str))
        self.assertTrue(isinstance(self.instance.file.path, unicode))
        self.assertTrue(isinstance(self.instance.image, str))


class NewFullFillAttributesWithDefaultDataAndChoicesTest(TestCase):

    def setUp(self):
        self.instance = new(ModelB)

    def test_fill_field_with_default_data(self):
        self.assertEquals(3, self.instance.integer)

    def test_fill_field_with_possible_choices(self):
        self.assertEquals('a', self.instance.string)


class NewFullFillAttributesWithCustomDataTest(TestCase):

    def setUp(self):
        self.instance = new(ModelA, integer=9, string='7', boolean=True)

    def test_fields_are_filled_with_custom_attributes(self):
        self.assertEquals(9, self.instance.integer)
        self.assertEquals('7', self.instance.string)
        self.assertEquals(True, self.instance.boolean)

    def test_fields_without_customized_values_are_filled_with_auto_data(self):
        self.assertTrue(isinstance(self.instance.smallinteger, int))
        self.assertTrue(isinstance(self.instance.text, str))
        self.assertEquals(None, self.instance.nullboolean)

    def test_fields_can_be_filled_by_functions(self):
        self.instance = new(ModelA, string=lambda field: field.name)
        self.assertEquals('string', self.instance.string)

    def test_invalid_configuration_raise_an_error(self):
        self.assertRaises(InvalidConfigurationError, new, ModelA, integer=lambda x: ''.invalidmethod())

    def test_bad_data_raise_an_error(self):
        get(ModelA, integer=50000)
        self.assertRaises(BadDataError, get, ModelA, integer=50000)


class NewAlsoCreatesRelatedObjectsTest(TestCase):

    def setUp(self):
        self.dynamic_fixture = DynamicFixture(data_fixture=DefaultDataFixture())
        self.instance = self.dynamic_fixture.new(ModelA)

    def test_new_fill_foreignkey_fields(self):
        self.assertTrue(isinstance(self.instance.foreignkey, ModelB))

    def test_new_fill_onetoone_fields(self):
        self.assertTrue(isinstance(self.instance.onetoone, ModelB))

#        TODO
#    def test_new_fill_genericrelations_fields(self):
#        self.assertTrue(isinstance(self.instance.foreignkey, ModelB))


class NewCanCreatesCustomizedRelatedObjectsTest(TestCase):

    def setUp(self):
        self.instance = new(ModelA, selfforeignkey=DynamicFixture(fill_nullable_fields=False))

    def test_customizing_nullable_fields_for_related_objects(self):
        self.assertTrue(isinstance(self.instance.integer, int))
        self.assertEquals(None, self.instance.selfforeignkey.integer)


class NewDealWithSelfReferencesTest(TestCase):

    def test_new_create_by_default_only_1_lap_in_cycle(self):
        instance = new(ModelA)
        self.assertNotEquals(None, instance.selfforeignkey) # 1 cycle
        self.assertEquals(None, instance.selfforeignkey.selfforeignkey) # 2 cycles

    def test_new_create_n_laps_in_cycle(self):
        instance = new(ModelA, number_of_laps=2)
        self.assertNotEquals(None, instance.selfforeignkey) # 1 cycle
        self.assertNotEquals(None, instance.selfforeignkey.selfforeignkey) # 2 cycles
        self.assertEquals(None, instance.selfforeignkey.selfforeignkey.selfforeignkey) # 3 cycles


class NewDealWithCyclicDependenciesTest(TestCase):

    def test_new_create_by_default_only_1_lap_in_cycle(self):
        c = new(ModelC)
        self.assertNotEquals(None, c.d) # 1 cycle
        self.assertEquals(None, c.d.c) # 2 cycles

    def test_new_create_n_laps_in_cycle(self):
        c = new(ModelC, number_of_laps=2)
        self.assertNotEquals(None, c.d)
        self.assertNotEquals(None, c.d.c) # 1 cycle
        self.assertNotEquals(None, c.d.c.d) # 2 cycles
        self.assertEquals(None, c.d.c.d.c) # 3 cycles


class NewFullFilledModelInstanceWithSequencialAutoDataTest(TestCase):
    def setUp(self):
        # using DynamicFixture with data_fixture to make tests easier: renew AutoData
        self.dynamic_fixture = DynamicFixture(data_fixture=DefaultDataFixture())

    def test_new_fill_integer_fields_sequencially_by_attribute(self):
        # using DynamicFixture with data_fixture to make tests easier: renew AutoData
        instance = self.dynamic_fixture.new(ModelA)
        self.assertEquals(1, instance.integer)
        self.assertEquals(1, instance.positiveinteger)
        self.assertEquals(2, instance.selfforeignkey.integer)
        self.assertEquals(2, instance.selfforeignkey.positiveinteger)
        instance = self.dynamic_fixture.new(ModelA)
        self.assertEquals(3, instance.integer)
        self.assertEquals(3, instance.positiveinteger)
        instance = self.dynamic_fixture.new(ModelA)
        self.assertEquals(5, instance.integer)
        self.assertEquals(5, instance.positiveinteger)

    def test_new_fill_string_with_sequences_of_numbers_by_attribute(self):
        instance = self.dynamic_fixture.new(ModelA)
        self.assertEquals('1', instance.string)
        self.assertEquals('1', instance.text)
        instance = self.dynamic_fixture.new(ModelA)
        self.assertEquals('3', instance.string)
        self.assertEquals('3', instance.text)


class GetDealWithPrimaryKeyTest(TestCase):

    def test_get_use_database_id_by_default(self):
        instance = get(ModelForNullableTest)
        self.assertNotEquals(None, instance.id)
        self.assertNotEquals(None, instance.pk)

    def test_get_use_given_id(self):
        instance = new(ModelForNullableTest, id=99998)
        self.assertEquals(99998, instance.id)
        self.assertEquals(99998, instance.pk)


class NewIgnoringNullableFieldsTest(TestCase):

    def test_new_do_not_fill_nullable_fields_if_we_do_not_want_to(self):
        instance = new(ModelForNullableTest, fill_nullable_fields=False)
        self.assertNotEquals(None, instance.not_nullable)
        self.assertEquals(None, instance.nullable)


class NewIgnoreFieldsInIgnoreListTest(TestCase):

    def test_new_do_not_fill_ignored_fields(self):
        instance = new(ModelForIgnoreListTest, ignore_fields=['not_required', 'not_required_with_default'])
        self.assertEquals(None, instance.not_required)
        self.assertNotEquals(None, instance.not_required_with_default)
        # not ignored fields
        self.assertNotEquals(None, instance.required)
        self.assertNotEquals(None, instance.required_with_default)

    def test_get_raise_an_error_if_a_required_field_is_in_ignore_list(self):
        self.assertRaises(BadDataError, get, ModelForIgnoreListTest, ignore_fields=['required', 'required_with_default'])

    def test_ignore_fields_are_propagated_to_self_references(self):
        instance = new(ModelForIgnoreListTest, ignore_fields=['not_required', 'nullable'])
        self.assertEquals(None, instance.not_required)
        self.assertEquals(None, instance.self_reference.not_required)

    def test_ignore_fields_are_not_propagated_to_different_references(self):
        instance = new(ModelForIgnoreListTest, ignore_fields=['not_required', 'nullable'])
        self.assertNotEquals(None, instance.different_reference.nullable)


class CreatingMultipleObjectsTest(TestCase):

    def test_new(self):
        self.assertEquals([], new(ModelA, n=0))
        self.assertEquals([], new(ModelA, n= -1))
        self.assertTrue(isinstance(new(ModelA), ModelA)) # default is 1
        self.assertTrue(isinstance(new(ModelA, n=1), ModelA))
        self.assertEquals(2, len(new(ModelA, n=2)))

    def test_get(self):
        self.assertEquals([], get(ModelA, n=0))
        self.assertEquals([], get(ModelA, n= -1))
        self.assertTrue(isinstance(get(ModelA), ModelA)) # default is 1
        self.assertTrue(isinstance(get(ModelA, n=1), ModelA))
        self.assertEquals(2, len(get(ModelA, n=2)))


class GetFullFilledModelInstanceAndPersistTest(TestCase):

    def setUp(self):
        self.dynamic_fixture = DynamicFixture(data_fixture=DefaultDataFixture())
        self.instance = get(ModelA)

    def test_get_create_and_save_a_full_filled_instance_of_the_model(self):
        self.assertTrue(isinstance(self.instance, ModelA))
        self.assertNotEquals(None, self.instance.id)
        # checking unique problems
        another_instance = get(ModelA)
        self.assertTrue(isinstance(another_instance, ModelA))
        self.assertNotEquals(None, another_instance.id)

    def test_get_create_and_save_related_fields(self):
        self.assertNotEquals(None, self.instance.selfforeignkey)
        self.assertNotEquals(None, self.instance.foreignkey)
        self.assertNotEquals(None, self.instance.onetoone)


class ManyToManyRelationshipTest(TestCase):

    def setUp(self):
        self.dynamic_fixture = DynamicFixture(data_fixture=DefaultDataFixture())

    def test_new_ignore_many_to_many_configuratios(self):
        self.instance = self.dynamic_fixture.new(ModelA, manytomany=3)
        self.instance.save()
        self.assertEquals(0, self.instance.manytomany.all().count())

    def test_get_ignore_many_to_many_configuratios(self):
        self.instance = self.dynamic_fixture.get(ModelA, manytomany=3)
        self.assertEquals(3, self.instance.manytomany.all().count())

    def test_many_to_many_configuratios_accept_list_of_dynamic_filters(self):
        self.instance = self.dynamic_fixture.get(ModelA, manytomany=[DynamicFixture(integer=1000), DynamicFixture(integer=1001)])
        self.assertEquals(2, self.instance.manytomany.all().count())
        self.assertEquals(1000, self.instance.manytomany.all()[0].integer)
        self.assertEquals(1001, self.instance.manytomany.all()[1].integer)

    def test_many_to_many_configuratios_accept_list_of_instances(self):
        b1 = self.dynamic_fixture.get(ModelB, integer=1000)
        b2 = self.dynamic_fixture.get(ModelB, integer=1001)
        self.instance = self.dynamic_fixture.get(ModelA, manytomany=[b1, b2])
        self.assertEquals(2, self.instance.manytomany.all().count())
        self.assertEquals(1000, self.instance.manytomany.all()[0].integer)
        self.assertEquals(1001, self.instance.manytomany.all()[1].integer)


class CustomFieldsTest(TestCase):
    def setUp(self):
        self.dynamic_fixture = DynamicFixture(data_fixture=DefaultDataFixture())

    def test_new_field_that_extends_django_field_must_be_supported(self):
        instance = self.dynamic_fixture.new(ModelE)
        self.assertEquals(1, instance.x)

    def test_unsupported_field_is_filled_with_null_if_it_is_possible(self):
        instance = self.dynamic_fixture.new(ModelE)
        self.assertEquals(None, instance.y)

    def test_unsupported_field_raise_an_error_if_it_does_not_accept_null_value(self):
        self.assertRaises(UnsupportedFieldError, self.dynamic_fixture.new, ModelF)


class PrintFieldValuesTest(TestCase):
    def setUp(self):
        self.dynamic_fixture = DynamicFixture(data_fixture=DefaultDataFixture())

    def test_model_not_saved_do_not_raise_an_exception(self):
        instance = self.dynamic_fixture.new(ModelA)
        print_field_values(instance)

    def test_model_saved_do_not_raise_an_exception(self):
        instance = self.dynamic_fixture.get(ModelA)
        print_field_values(instance)


class SanityTest(TestCase):
    def setUp(self):
        self.dynamic_fixture = DynamicFixture(data_fixture=DefaultDataFixture())

    def test_create_lots_of_models_to_verify_data_unicity_errors(self):
        for i in range(1000):
            self.dynamic_fixture.get(ModelA)
