import turbogears
import cherrypy

from turbogears import widgets, testutil


def test_table_widget_js():
    """
    The TableForm Widget can require JavaScript and CSS resources. Addresses
    ticket #425. Should be applicable to any widget.
    """
    class MyTableWithJS(widgets.TableForm):
        javascript = [widgets.JSLink(mod=widgets.static, name="foo.js"),
                      widgets.JSSource("alert('hello');")]
        css = [widgets.CSSLink(mod=widgets.static, name="foo.css")]

    form = MyTableWithJS(fields=[widgets.TextField(name='title')])

    class MyRoot(turbogears.controllers.RootController):
        def test(self):
            return dict(form=form)
        test = turbogears.expose(template=".form")(test)

    cherrypy.root = MyRoot()
    testutil.create_request("/test")
    output = cherrypy.response.body[0]
    assert 'foo.js' in output
    assert "alert('hello');" in output
    assert 'foo.css' in output


def test_calendardatepicker_js():

    class MyRoot(turbogears.controllers.RootController):

        def test(self, lang=None):
            return dict(widget=widgets.CalendarDatePicker(calendar_lang=lang))
        test = turbogears.expose(template=".widget")(test)

    cherrypy.root = MyRoot()

    # testing default language (en)
    testutil.create_request("/test")
    output = cherrypy.response.body[0]
    assert 'calendar/calendar.js' in output
    assert 'calendar/calendar-setup.js' in output
    assert 'calendar/lang/calendar-en.js' in output

    # testing non-existing language
    testutil.create_request("/test",
        headers={"Accept-Language": "x"})
    output = cherrypy.response.body[0]
    assert 'calendar/lang/calendar-x.js' not in output
    assert 'calendar/lang/calendar-en.js' in output

    # testing French language
    testutil.create_request("/test",
        headers={"Accept-Language": "fr"})
    output = cherrypy.response.body[0]
    assert 'calendar/lang/calendar-fr.js' in output
    assert 'calendar/lang/calendar-en.js' not in output
    assert 'charset="utf-8"' in output

    # testing German language with any charset
    testutil.create_request("/test",
        headers={"Accept-Language": "de", "Accept-Charset": "*"})
    output = cherrypy.response.body[0]
    assert 'calendar/lang/calendar-de.js' in output
    assert 'calendar/lang/calendar-en.js' not in output
    assert 'charset="*"' not in output

    # testing Turkish language with non-existing charset
    testutil.create_request("/test",
        headers={"Accept-Language": "tr", "Accept-Charset": "big5"})
    output = cherrypy.response.body[0]
    assert 'calendar/lang/calendar-tr.js' in output
    assert 'calendar/lang/calendar-en.js' not in output
    assert 'charset="big5"' not in output

    win1254 = 'windows-1254'
    from codecs import lookup
    try:
        assert lookup(win1254).name == 'cp1254'
    except AttributeError: # Py < 2.5
        win1254 = 'cp1254' # cannot test name normalization here

    # testing Turkish language with existing, not normalized charset
    testutil.create_request("/test",
        headers={"Accept-Language": "tr", "Accept-Charset": win1254})
    output = cherrypy.response.body[0]
    assert 'calendar/lang/calendar-tr-cp1254.js' in output
    assert 'calendar/lang/calendar-en.js' not in output
    assert 'charset="cp1254"' in output

    # testing more than one language and charset
    testutil.create_request("/test", headers={"Accept-Language": "x,tr,de,fr",
        "Accept-Charset": "big5,%s,latin-1" % win1254})
    output = cherrypy.response.body[0]
    assert 'calendar/lang/calendar-tr-cp1254.js' in output
    assert 'calendar/lang/calendar-x.js' not in output
    assert 'calendar/lang/calendar-en.js' not in output
    assert 'charset="cp1254"' in output
    assert 'charset="big5"' not in output

    # testing predetermined language (fr)
    testutil.create_request("/test?lang=fr",
        headers={"Accept-Language": "de,en,tr"})
    output = cherrypy.response.body[0]
    assert 'calendar/lang/calendar-fr.js' in output
    assert 'calendar/lang/calendar-en.js' not in output

    # testing predetermined non-existing language
    testutil.create_request("/test?lang=x",
        headers={"Accept-Language": "de,en,fr,tr"})
    output = cherrypy.response.body[0]
    assert 'calendar/lang/calendar-de.js' in output
    assert 'calendar/lang/calendar-x.js' not in output
    assert 'calendar/lang/calendar-en.js' not in output
