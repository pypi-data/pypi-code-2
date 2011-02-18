from tg import TGController, tmpl_context, expose
from tw.api import Widget
from abl.jquery.ui.widgets import JQueryUITabs


class MyWidget(Widget):
    """
    A minimalistic widget that renders a div with a
    given value.
    """
    template = """<div>${value}</div>"""
    engine_name = "genshi"

w1 = MyWidget('w1')
w2 = MyWidget('w2')
dw = MyWidget('default')

tabs_widget = JQueryUITabs('tabs', #internal id
                           tabs_id="example_tabs", #id used in HTML
                           children=[w1, w2],
                           title_list=['first tab', 'last tab'],
                           default_field=dw)


class TabsController(TGController):

    @expose('abl.jquery.examples.tabs.templates.index')
    def index(self):
        tmpl_context.tabs_widget = tabs_widget
        #See the template to see how the widget is called
        return dict()

