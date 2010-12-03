from tw.core.testutil import WidgetTestCase
from tw.jqgrid import *

colModel = [
            {'name':'id', 'index':'id', 'width':20, 'align':'right'},
            {'name':'title', 'index':'title','width':100, 'align':'left'},
            {'name':'synopsis', 'index':'synopsis','width':580, 'align':'left', 'sortable':False},
           ]

class TestWidget(WidgetTestCase):
    # place your widget at the TestWidget attribute
    TestWidget = JqGrid
    # Initilization args. go here
    widget_kw = {'url': 'http://foo',
                 'colModel': colModel
                 }

    def test_render(self):
        # Asserts 'foo' and 'test' (the test widget's id) appear in rendered
        self.assertInOutput(['test', 'test_pager', 'test_search'])
        self.assertInDynamicCalls('jQuery("#test").jqGrid("navGrid", "#test_pager",')
        self.assertInDynamicCalls('"sortorder": "asc"')
