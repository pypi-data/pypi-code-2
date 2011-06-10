"""
Here you can create samples of your widgets by providing default parameters,
inserting them in a container widget, mixing them with other widgets, etc...
These samples will appear in the WidgetBrowser

See http://toscawidgets.org/documentation/WidgetBrowser for more information
"""

from tw.jqgrid import JqGrid

class DemoJqGrid(JqGrid):
    # Provide default parameters, value, etc... here
    demo_for = JqGrid
    colNames=['ID','Title', 'Synopsis']

    def __init__(self, id, **kwargs):
        """
        """
        kwargs['url']='foo'
        kwargs['colModel']=[
                {'name':'id', 'index':'id', 'width':20, 'align':'right'},
                {'name':'title', 'index':'title','width':100, 'align':'left'},
                {'name':'synopsis', 'index':'synopsis','width':580, 'align':'left', 'sortable':False},
               ]
        super(DemoJqGrid, self).__init__(id, **kwargs)

    def foo(self):
        from nose.tools import set_trace; set_trace()