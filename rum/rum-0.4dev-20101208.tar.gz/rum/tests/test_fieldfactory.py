import unittest
from rum import fields, repository, RumApp, view

factory = fields.FieldFactory

class SuperHero(object):
    factory.fields(
        fields.Unicode("name", required=True),
        fields.Integer("age"),
        fields.HTMLText("resume"),
        )

class SuperResourceWithDefaults(object):
    factory.fields(
        fields.Unicode("name", default="Herbert"),
        fields.Integer("age", default=lambda: 108),
        )

class EvilVillain(object):
    pass



factory.fields(EvilVillain, (
    fields.Unicode("name", required=True),
    fields.Integer("age"),
    fields.HTMLText("mischieves"),
    "superpowers",
    "you_cant_guess_me",
    ))

# We explicitly register a field for 'superpowers' since it will
# be tried to be guessed an there are no base rules to guess from a normal
# object. Normally it would be a custom factory which will kick in to try and
# guess a field, but we have no factories to handle arbitrary villains
factory.fields(EvilVillain, "superpowers", fields.HTMLText("superpowers"))

class TestFields(unittest.TestCase):
    def setUp(self):
        self.app = RumApp()
        self.ctx = self.app.mounted_at()
        self.ctx.__enter__()

    def tearDown(self):
        self.ctx.__exit__()

    def test_bad_args(self):
        self.failUnlessRaises(TypeError, factory.fields,
            EvilVillain, fields.HTMLText("superpowers")
            )

    def test_class_decorator_for_class(self):
        got = self.app.fields_for_resource(SuperHero)
        expected = [
            fields.Unicode("name", required=True),
            fields.Integer("age"),
            fields.HTMLText("resume"),
            ]
        self.failUnlessEqual(expected, got)

    def test_mapper_style_for_class(self):
        got = self.app.fields_for_resource(EvilVillain)
        expected = [
            fields.Unicode("name", required=True),
            fields.Integer("age"),
            fields.HTMLText("mischieves"),
            fields.HTMLText("superpowers"),
            ]
        self.failUnlessEqual(expected, got)


class TestFieldFactory(unittest.TestCase):
    def setUp(self):
        self.app = RumApp()
        self.ctx = self.app.mounted_at()
        self.ctx.__enter__()

    def tearDown(self):
        self.ctx.__exit__()

    def makeOne(self):
        return self.app.repositoryfactory.field_factory

    def test_defaults(self):
        ff = self.makeOne()
        self.failUnlessEqual(
            ff.defaults(SuperResourceWithDefaults),
            {'age': 108, 'name': 'Herbert'}
            )
        
