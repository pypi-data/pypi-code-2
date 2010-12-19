import turbogears
from turbogears import widgets
from turbogears import controllers
from turbogears import validators
from turbogears import testutil


def setup_module():
    global app
    app = testutil.make_app(MyRoot)
    testutil.start_server()

def teardown_module():
    testutil.stop_server()


myform = widgets.TableForm(fields = [
    widgets.FieldSet(
        name = "p_data",
        fields = [
            widgets.TextField(name="name"),
            widgets.TextField(name="age",
                validator=validators.Int()),
        ]),
])

class MyRoot(controllers.RootController):
    def testform(self, p_data, tg_errors=None):
        has_errors = tg_errors is not None
        name = p_data['name']
        age = p_data['age']
        return dict(has_errors = has_errors, name=name, age = age)
    testform = turbogears.validate(form=myform)(testform)
    testform = turbogears.expose(template="turbogears.tests.othertemplate")(
                                 testform)

    def set_errors(self):
        return dict(has_errors = True)
        

    def testform_new_style(self, p_data):
        name = p_data['name']
        age = p_data['age']
        return dict(name = name, age = age)
    testform_new_style = turbogears.validate(form=myform)(testform_new_style)
    testform_new_style = turbogears.error_handler(set_errors)(testform_new_style)
    testform_new_style = turbogears.expose()(testform_new_style)



def test_form_translation_new_style():
    "Form input is translated into properly converted parameters"
    response = app.get("/testform_new_style?p_data.name=ed&p_data.age=5")
    assert response.raw['name'] == "ed"
    print response.raw['age']
    assert response.raw['age'] == 5

def test_invalid_form_with_error_handling():
    "Invalid forms can be handled by the method"
    response = app.get("/testform_new_style?p_data.name=ed&p_data.age=edalso")
    assert response.raw['has_errors']

