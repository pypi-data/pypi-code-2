import turbogears
from turbogears import widgets, testutil

def setup_module():
    testutil.start_server()

def teardown_module():
    testutil.stop_server()


def test_table_widget_js():
    """The TableForm Widget can require JavaScript and CSS resources.

    Addresses ticket #425. Should be applicable to any widget.
    """
    class MyTableWithJS(widgets.TableForm):
        javascript = [widgets.JSLink(mod=widgets.static, name="foo.js"),
                      widgets.JSSource("alert('hello');")]
        css = [widgets.CSSLink(mod=widgets.static, name="foo.css")]

    form = MyTableWithJS(fields=[widgets.TextField(name='title')])

    class MyRoot(turbogears.controllers.RootController):
        def test(self):
            return dict(form=form)
        test = turbogears.expose(template="kid:turbogears.widgets.tests.form")(test)

    app = testutil.make_app(MyRoot)
    response = app.get("/test")
    assert 'foo.js' in response.body
    assert "alert('hello');" in response.body
    assert 'foo.css' in response.body


def test_calendardatepicker_js():

    class MyRoot(turbogears.controllers.RootController):

        def test(self, lang=None):
            return dict(widget=widgets.CalendarDatePicker(calendar_lang=lang))
        test = turbogears.expose(template="kid:turbogears.widgets.tests.widget")(test)

    app = testutil.make_app(MyRoot)

    # testing default language (en)
    response = app.get("/test")
    assert 'calendar/calendar.js' in response.body
    assert 'calendar/calendar-setup.js' in response.body
    assert 'calendar/lang/calendar-en.js' in response.body

    # testing non-existing language
    response = app.get("/test", headers={"Accept-Language": "x"})
    assert 'calendar/lang/calendar-x.js' not in response.body
    assert 'calendar/lang/calendar-en.js' in response.body

    # testing French language
    response = app.get("/test", headers={"Accept-Language": "fr"})
    assert 'calendar/lang/calendar-fr.js' in response.body
    assert 'calendar/lang/calendar-en.js' not in response.body
    assert 'charset="utf-8"' in response.body

    # testing German language with any charset
    response = app.get("/test",
        headers={"Accept-Language": "de", "Accept-Charset": "*"})
    assert 'calendar/lang/calendar-de.js' in response.body
    assert 'calendar/lang/calendar-en.js' not in response.body
    assert 'charset="*"' not in response.body

    # testing Turkish language with non-existing charset
    response = app.get("/test",
        headers={"Accept-Language": "tr", "Accept-Charset": "big5"})
    assert 'calendar/lang/calendar-tr.js' in response.body
    assert 'calendar/lang/calendar-en.js' not in response.body
    assert 'charset="big5"' not in response.body

    win1254 = 'windows-1254'
    from codecs import lookup
    try:
        assert lookup(win1254).name == 'cp1254'
    except AttributeError: # Py < 2.5
        win1254 = 'cp1254' # cannot test name normalization here

    # testing Turkish language with existing, not normalized charset
    response = app.get("/test",
        headers={"Accept-Language": "tr", "Accept-Charset": win1254})
    assert 'calendar/lang/calendar-tr-cp1254.js' in response.body
    assert 'calendar/lang/calendar-en.js' not in response.body
    assert 'charset="cp1254"' in response.body

    # testing more than one language and charset
    response = app.get("/test", headers={"Accept-Language": "x,tr,de,fr",
        "Accept-Charset": "big5,%s,latin-1" % win1254})
    assert 'calendar/lang/calendar-tr-cp1254.js' in response.body
    assert 'calendar/lang/calendar-x.js' not in response.body
    assert 'calendar/lang/calendar-en.js' not in response.body
    assert 'charset="cp1254"' in response.body
    assert 'charset="big5"' not in response.body

    # testing predetermined language (fr)
    response = app.get("/test?lang=fr",
        headers={"Accept-Language": "de,en,tr"})
    assert 'calendar/lang/calendar-fr.js' in response.body
    assert 'calendar/lang/calendar-en.js' not in response.body

    # testing predetermined non-existing language
    response = app.get("/test?lang=x",
        headers={"Accept-Language": "de,en,fr,tr"})
    assert 'calendar/lang/calendar-de.js' in response.body
    assert 'calendar/lang/calendar-x.js' not in response.body
    assert 'calendar/lang/calendar-en.js' not in response.body
