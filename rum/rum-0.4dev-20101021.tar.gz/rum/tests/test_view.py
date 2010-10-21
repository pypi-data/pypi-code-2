from unittest import TestCase
from formencode import validators as v
from rum import ViewFactory
from rum.tests.model import Model, clear_all
from rum.validators import FilteringSchema, All, MaxLength

class ModelView(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __call__(self, resource=None, **kw):
        dct = dict((k, getattr(resource, k)) for k in dir(resource)
                                        if not k.startswith('_'))
        return repr(dct)

    def validate(self, obj, state=None):
        if self.validator:
            return self.validator.to_python(obj)
        return dict(obj)

class ModelViewFactory(ViewFactory):
    pass

model_view = ModelView(
    id= "for_model",
    validator = FilteringSchema(
        a = v.UnicodeString(not_empty=True),
        b = v.UnicodeString(not_empty=True),
        c = v.Int(if_missing=0)
        )
    )

from inspect import isclass
ModelViewFactory.register(model_view, Model, pred="action != 'delete'")

class DummyClassDecoratedModel(Model):
    ModelViewFactory.view(ModelView(id="for_decorated"), action='show')
    ModelViewFactory.view(ModelView(id="for_decorated_edit"), action='edit')

class TestValidation(TestCase):
    def test_all_validator(self):
        self.failUnlessEqual(All().to_python(''), '')
    def test_maxlength_validator(self):
        self.failUnlessEqual(MaxLength().to_python(''), '')

class TestViewFactory(TestCase):
    def setUp(self):
        clear_all()
        self.factory = ModelViewFactory()

    def makeOne(self):
        return ModelViewFactory()

    def test_base(self):
        factory = self.makeOne()
        view = factory(Model)
        self.failUnless(isinstance(view, ModelView))
        self.failUnlessEqual(view.id, "for_model")

    def test_class_decorated(self):
        factory = self.makeOne()
        view = factory(DummyClassDecoratedModel, action='show')
        self.failUnless(isinstance(view, ModelView))
        self.failUnlessEqual(view.id, "for_decorated")

    def test_class_decorated_fixed_action(self):
        factory = self.makeOne()
        view = factory(DummyClassDecoratedModel, action='edit')
        self.failUnless(isinstance(view, ModelView))
        self.failUnlessEqual(view.id, "for_decorated_edit")
