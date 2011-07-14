from unittest import TestCase
from datetime import datetime
import cherrypy
from turbogears import widgets, config, controllers, expose, mochikit, \
    validate, validators, testutil


class MyFormFields(widgets.WidgetsList):
    #XXX: Since allow_extra_fields should be removed from validators.Schema,
    #     we need a validator for every input-expecting widget
    name = widgets.TextField(validator=validators.String())
    age = widgets.TextField(validator=validators.Int(), default=0)
    date = widgets.CalendarDatePicker(validator=validators.DateConverter(
                                            if_empty=datetime.now()))

myfields = MyFormFields()
myform = widgets.TableForm(fields=myfields)


class MyRoot(controllers.RootController):

    [expose(template="turbogears.tests.form")]
    def index(self):
        return dict(form=myform)

    [expose(template="turbogears.tests.form")]
    def fields(self):
        myfields.display = lambda **kw: kw.values()
        return dict(form=myfields)

    [expose(template="turbogears.tests.form")]
    def usemochi(self):
        return dict(mochi=mochikit, form=myform)

    [expose(template="turbogears.tests.othertemplate")]
    [validate(form=myform)]
    def testform(self, name, date, age, tg_errors=None):
        if tg_errors:
            self.has_errors = True
        self.name = name
        self.age = age
        self.date = date

    [expose()]
    [validate(form=myform)]
    def testform_new_style(self, name, date, age):
        if cherrypy.request.validation_errors:
            self.has_errors = True
        self.name = name
        self.age = age
        self.date = date

def test_form_translation():
    """Form input is translated into properly converted parameters"""
    root = MyRoot()
    cherrypy.root = root
    testutil.create_request("/testform?name=ed&date=11/05/2005&age=5")
    assert root.name == "ed"
    assert root.age == 5

def test_form_translation_new_style():
    """Form input is translated into properly converted parameters"""
    root = MyRoot()
    cherrypy.root = root
    testutil.create_request("/testform_new_style?name=ed&date=11/05/2005&age=5&")
    assert root.name == "ed"
    assert root.age == 5

def test_invalid_form_with_error_handling():
    """Invalid forms can be handled by the method"""
    root = cherrypy.root
    testutil.create_request("/testform?name=ed&age=edalso&date=11/05/2005")
    assert root.has_errors

def test_css_should_appear():
    """CSS should appear when asked for"""
    testutil.create_request("/")
    assert "calendar-system.css" in cherrypy.response.body[0]
    testutil.create_request("/fields")
    assert "calendar-system.css" in cherrypy.response.body[0]

def test_javascript_should_appear():
    """JavaScript should appear when asked for"""
    testutil.create_request("/")
    assert "calendar.js" in cherrypy.response.body[0]
    testutil.create_request("/fields")
    assert "calendar.js" in cherrypy.response.body[0]

def test_include_mochikit():
    """JSLinks (and MochiKit especially) can be included easily"""
    testutil.create_request("/usemochi")
    assert "MochiKit.js" in cherrypy.response.body[0]

def test_suppress_mochikit():
    """MochiKit inclusion can be suppressed"""
    config.update({"global": {"tg.mochikit_suppress": True}})
    testutil.create_request("/usemochi")
    suppressed_body = cherrypy.response.body[0]
    # repair the fixture
    config.update({"global": {"tg.mochikit_suppress": False}})
    testutil.create_request("/usemochi")
    included_body = cherrypy.response.body[0]
    assert "MochiKit.js" not in suppressed_body
    assert "MochiKit.js" in included_body

def test_mochikit_everywhere():
    """MochiKit can be included everywhere by setting tg.mochikit_all"""
    config.update({"global": {"tg.mochikit_all": True}})
    testutil.create_request("/")
    config.update({"global": {"tg.mochikit_all": False}})
    assert "MochiKit.js" in cherrypy.response.body[0]

def test_mochikit_nowhere():
    """Setting tg.mochikit_suppress will prevent including it everywhere"""
    config.update({"global": {"tg.mochikit_all": True}})
    config.update({"global": {"tg.mochikit_suppress": True}})
    testutil.create_request("/")
    config.update({"global": {"tg.mochikit_all": False}})
    config.update({"global": {"tg.mochikit_suppress": False}})
    assert "MochiKit.js" not in cherrypy.response.body[0]

def test_include_widgets():
    """Any widget can be included everywhere by setting tg.include_widgets"""
    config.update({"global": {"tg.include_widgets": ["mochikit"]}})
    testutil.create_request("/")
    config.update({"global": {"tg.include_widgets": []}})
    assert "MochiKit.js" in cherrypy.response.body[0]


class State(object):
    counter = 0

class AddingValidator(validators.FancyValidator):
    def _to_python(self, value, state=None):
        state.counter += 1
        return value

class AddingSchema(validators.Schema):
    a = AddingValidator()
    b = AddingValidator()

class AddingNestedSchema(AddingSchema):
    c = AddingSchema()


class TestValidationState(TestCase):

    class Controller(controllers.RootController):

        [expose()]
        [validate(validators=AddingNestedSchema(), state_factory=State)]
        def validation(self, a, b, c):
            return 'counter: %d' % cherrypy.request.validation_state.counter

    def __init__(self, *args, **kw):
        super(TestValidationState, self).__init__(*args, **kw)

    def test_counter_is_incremented(self):
        cherrypy.root = self.Controller()
        # parameter values are irrelevant
        url = '/validation?a=1&b=2&c.a=3&c.b=4'
        testutil.create_request(url)
        body = cherrypy.response.body[0]
        msg = "Validation state is not handled properly"
        # 4 == 1 (a) + 1(b) + 1(c.a) + 1(c.b)
        self.failUnless('counter: 4' in body, msg)
