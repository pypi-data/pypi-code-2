from unittest import TestCase
from rum import RumApp, fields
from rumalchemy.tests import model
from rumalchemy.util import get_mapper
from rumalchemy import SAFieldFactory


class TestSAFieldFactory(TestCase):
    def setUp(self):
        self.factory = SAFieldFactory()
        #XXX: The following line, for some reason, prevents the first test
        #     from failing if coverage is on, go figure   
        get_mapper(model.User)

    def test_foreign_key(self):
        user_id = get_mapper(model.Address).get_property('user_id').columns[0]
        field = self.factory(model.Address, user_id)
        self.failUnless(isinstance(field, fields.ForeignKey), `field`)
        self.failUnless(field.required, `field`)

        field = field.type
        self.failUnless(isinstance(field, fields.Integer), `field`)
        self.failUnless(field.required, `field`)

    def test_primary_key(self):
        id = get_mapper(model.Address).get_property('id').columns[0]
        field = self.factory(model.Address, id)
        self.failUnless(isinstance(field, fields.PrimaryKey), `field`)
        self.failUnless(field.auto, `field`)
        self.failUnless(not field.required, `field`)

        field = field.type
        self.failUnless(isinstance(field, fields.Integer), `field`)
        self.failUnless(field.required, `field`)

    def test_relation(self):
        user = get_mapper(model.Address).get_property('user')
        field = self.factory(model.Address, user)
        self.failUnless(isinstance(field, fields.Relation), `field`)
        self.failUnless(field.required, `field`)

    def test_non_auto_pk(self):
        code = get_mapper(model.Country).get_property('code')
        field = self.factory(model.Country, code)
        self.failUnless(isinstance(field, fields.PrimaryKey), `field`)
        self.failUnless(field.required, `field`)
        self.failUnless(not field.auto, `field`)

    def test_sequence(self):
        id = get_mapper(model.User).get_property('id')
        field = self.factory(model.User, id)
        self.failUnless(isinstance(field, fields.PrimaryKey), `field`)
        self.failUnless(not field.required, `field`)
        self.failUnless(field.auto, `field`)
        self.failUnless(not field.has_default, `field`)

        field = field.type
        self.failUnless(isinstance(field, fields.Integer), `field`)
        self.failUnless(field.required, `field`)

    def test_length(self):
        prop = get_mapper(model.User).get_property('name')
        field = self.factory(model.User, prop)
        self.failUnlessEqual(field.length, 15)

    def test_explicit_from_info(self):
        prop = get_mapper(model.PowerUser).get_property('description')
        field = self.factory(model.PowerUser, prop)
        self.failUnless(isinstance(field, fields.HTMLText), `field`)

    def test_related_list(self):
        prop = get_mapper(model.User).get_property('addresses')
        field = self.factory(model.User, prop)
        self.failUnless(isinstance(field, fields.List), `field`)
        self.failUnless(not field.required, `field`)

    def test_unicode_field(self):
        prop = get_mapper(model.User).get_property('name')
        field = self.factory(model.User, prop)
        self.failUnless(isinstance(field, fields.Unicode), `field`)
    
    def test_mapper_renamed_key(self):
        prop=get_mapper(model.CountryModified).get_property('label')
        field=self.factory(model.CountryModified, prop)
        self.failUnless(field.name=='label', `field`)
