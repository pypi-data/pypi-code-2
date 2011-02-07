from tw.api import Widget, JSLink, CSSLink, js_function
from tw.jquery import jquery_js
from tw.jquery.ui import jquery_ui_all_js

__all__ = ["JqGrid","jqgrid_css","jqgrid_search_css"]

# declare your static resources here
i18n_jqgrid = JSLink(modname=__name__,
               filename='static/i18n/grid.locale-en.js',
               javascript=[])

jquery_jqgrid = JSLink(modname=__name__,
               filename='static/javascript/jquery.jqGrid.min.js',
               javascript=[jquery_js, jquery_ui_all_js, i18n_jqgrid])

# <DEBUG>
# for debugging purpose ordered as in grid.loader.js

#debug_base =  JSLink(modname=__name__, filename='static/src/grid.base.js')
#debug_common =  JSLink(modname=__name__, filename='static/src/grid.common.js')
#
##debug_inlinedit =  JSLink(modname=__name__, filename='static/src/grid.inlinedit.js')
##debug_celledit =  JSLink(modname=__name__, filename='static/src/grid.celledit.js')
##debug_subgrid =  JSLink(modname=__name__, filename='static/src/grid.subgrid.js')
#debug_treegrid =  JSLink(modname=__name__, filename='static/src/grid.treegrid.js')
##debug_custom =  JSLink(modname=__name__, filename='static/src/grid.custom.js')
##debug_postext =  JSLink(modname=__name__, filename='static/src/grid.postext.js')
##debug_tbltogrid =  JSLink(modname=__name__, filename='static/src/grid.tbltogrid.js')
##debug_setcolumns =  JSLink(modname=__name__, filename='static/src/grid.setcolumns.js')
##debug_import =  JSLink(modname=__name__, filename='static/src/grid.import.js')
##debug_fmatter =  JSLink(modname=__name__, filename='static/src/jquery.fmatter.js')
##debug_jsonxml =  JSLink(modname=__name__, filename='static/src/JsonXml.js')
##debug_searchfilter =  JSLink(modname=__name__, filename='static/src/jquery.searchFilter.js')
#
#debug_formedit =  JSLink(modname=__name__, filename='static/src/grid.formedit.js',
#                         javascript=[jquery_js, jquery_ui_all_js, i18n_jqgrid,
#                                     debug_base, debug_common, debug_treegrid])
#
#
#jquery_jqgrid = debug_formedit

# </DEBUG>

from tw.uitheme import smoothness_css

jqgrid_css = CSSLink(modname=__name__, filename='static/css/ui.jqgrid.css')
jqgrid_search_css = CSSLink(modname=__name__, filename='static/css/jquery.searchFilter.css')


class JqGrid(Widget):
    """
    jqgrid full options : http://www.trirand.com/jqgridwiki/doku.php?id=wiki:options
    """
    template = """
             <table id="${id}" ></table>
             <div id="${id}_pager" ></div>
             <div id="${id}_search" ></div>
             """

    javascript = [jquery_jqgrid]
    css = [smoothness_css, jqgrid_css, jqgrid_search_css]

    params = {
           "url": "Tells us where to get the data.",
           "editurl": "Defines the url for inline and form editing",
           "datatype" : "This tells jqGrid the type of information being returned so it can construct the grid.",
           "mtype" :"Tells us how to make the ajax call: either 'GET' or 'POST'.",
           "colNames" :"An array in which we place the names of the columns. ",
           # column model options : http://www.trirand.com/jqgridwiki/doku.php?id=wiki:colmodel_options
           "colModel" :"An array that describes the model of the columns.",
           "pager" :"Defines that we want to use a pager bar to navigate through the records.",
           "rowNum" :"Sets how many records we want to view in the grid.",
           "rowList" :"An array to construct a select box element in the pager in which we can change the number of the visible rows.",
           "sortname" :"Sets the initial sorting column.",
           "sortorder": "Sets the initial sort order",
           "viewrecords" :"Defines whether we want to display the number of total records from the query in the pager bar",
           "caption" :"Sets the caption for the grid.",
           "height" : "The height of the grid.",
           "shrinkToFit" : "if True, every column width is scaled according to the defined option width.",
           "width" : "If this option is set, the initial width of each column is set according to the value of shrinkToFit option.",
           "toolbar" : "This option defines the toolbar of the grid. This is array with two values in which the first value enables the toolbar and the second defines the position relative to body Layer.",
           "rownumbers" : "If this option is set to true, a new column at left of the grid is added.",
           "toppager" : "When enabled this option place a pager element at top of the grid below the caption (if available).",
           "autowidth" : "When set to true, the grid width is recalculated automatically to the width of the parent element.",
           "multiselect" : "If this flag is set to true a multi selection of rows is enabled.",
           "multiselectWidth" : "Determines the width of the multiselect column if multiselect is set to true.",
           "subGrid" : "If set to true this enables using a subgrid.",
           "subGridUrl" : "This option points to the file from which we get the data for the subgrid. jqGrid adds the id of the row to this url as parameter. If there is a need to pass additional parameters, use the params option in subGridModel",
           "subGridModel" : "It is an array in which we describe the column model for the subgrid data",
           "subGridWidth" : "Determines the width of the subGrid column if subgrid is enabled.",
           "postData" : "additional data to pass to the request",
           # events http://www.trirand.com/jqgridwiki/doku.php?id=wiki:events
           "afterInsertRow": "This event fires after every inserted row.",
           "beforeRequest" : "javascript callable, called before the request is sent to the server (ts.p.beforeRequest.call(ts)).",
           "beforeSelectRow": "This event fire when the user click on the row, but before select them.",
           "gridComplete": "This fires after all the data is loaded into the grid and all other processes are complete.",
           "loadBeforeSend": "A pre-callback to modify the XMLHttpRequest object (xhr) before it is sent.",
           "loadComplete": "This event is executed immediately after every server request.",
           "loadError": "A function to be called if the request fails.",
           "onCellSelect": "Fires when we click on particular cell in the grid.",
           "ondblClickRow": "Raised immediately after row was double clicked.",
           "onHeaderClick": "Fire after clicking to hide or show grid (hidegrid:true)",
           "onPaging": "This event fires after click on [page button] and before populating the data.",
           "onRightClickRow": "Raised immediately after row was right clicked.",
           "onSelectAll": "This event fires when multiselect option is true and you click on the header checkbox.",
           "onSelectRow" :"Raised immediately after row was clicked.",
           "onSortCol": "Raised immediately after sortable column was clicked and before sorting the data.",
           "resizeStart": "Event which is called when we start resize a column.",
           "resizeStop": "Event which is called after the column is resized.",
           "serializeGridData": "If set this event can serialize the data passed to the ajax request.",

           "subGridRowExpanded" : "This event is raised when the subgrid is enabled and is executed when the user clicks on the plus icon of the grid.",

           # TreeGrid options
           "ExpandColClick" : "when true, the tree is expanded and/or collapsed when we click on the text of the expanded column, not only on the image",
           "ExpandColumn" : "indicates which column (name from colModel) should be used to expand the tree grid. If not set the first one is used. Valid only when treeGrid option is set to true.",
           "treedatatype" : "Determines the initial datatype (see datatype option). Usually this should not be changed. During the reading process this option is equal to the datatype option.",
           "treeGrid" : "Enables (disables) the tree grid format.",
           "treeGridModel" : "Determines the method used for the treeGrid. Can be nested or adjacency.",
           "treeIcons" : "This array set the icons used in the tree. The icons should be a valid names from UI theme roller images.",
           "treeReader" : "extends the colModel defined in the basic grid. The fields described here are added to end of the colModel array and are hidden. This means that the data returned from the server should have values for these fields.",
           "tree_root_level" : "Determines the level where the root element begins when treeGrid is enabled",

           }

    #defaults
    editurl = None
    datatype = "json"
    mtype = "POST"
    sortorder = "asc"
    subGrid = False
    toolbar = [False, '']
    rownumbers = False
    toppager = False
    autowidth = True
    multiselect = False
    multiselectWidth = 20

    postData = {}
    # events
    afterInsertRow = None
    beforeRequest = None
    beforeSelectRow = None
    gridComplete = None
    loadBeforeSend = None
    loadComplete = None
    loadError = None
    onCellSelect = None
    ondblClickRow = None
    onHeaderClick = None
    onPaging = None
    onRightClickRow = None
    onSelectAll = None
    onSelectRow = None
    onSortCol = None
    resizeStart = None
    resizeStop = None
    serializeGridData = None

    subGridRowExpanded = None


    # tree specific
    treeGrid = False

    navbuttons_options = {"view":False, "edit": False, "add": False,"del": False,
                          "search":True,"refresh":True}
# full options for the navbuttons_options
#            edit: true,
#            editicon: "ui-icon-pencil",
#            add: true,
#            addicon:"ui-icon-plus",
#            del: true,
#            delicon:"ui-icon-trash",
#            search: true,
#            searchicon:"ui-icon-search",
#            refresh: true,
#            refreshicon:"ui-icon-refresh",
#            refreshstate: 'firstpage',
#            view: false,
#            viewicon : "ui-icon-document",
#            position : "left",
#            closeOnEscape : true,
#            beforeRefresh : null,  # js callable
#            afterRefresh : null,
#            cloneToTop : false


    addbutton_options = {}
    editbutton_options = {}
    delbutton_options = {}
    search_options = {}
    viewbutton_options = {}

    def __init__(self, id, **kwargs):
        """
        """
        super(JqGrid, self).__init__(**kwargs)
        if not kwargs.get("url", False):
            raise ValueError, "JqGrid must have url for fetching data"
        if not kwargs.get("colModel", False):
            raise ValueError, "JqGrid must have colModel for setting up the columns"

        # default values
        self.pager = kwargs.get("pager", '%s_pager' % self.id)

    def update_params(self, d):
        super(JqGrid, self).update_params(d)
        grid_params = dict(url=self.url,
                           editurl=self.editurl,
                           datatype=self.datatype,
                           mtype=self.mtype,
                           colNames=self.colNames,
                           colModel=self.colModel,
                           pager=self.pager,
                           rowNum=self.rowNum,
                           rowList=self.rowList,
                           sortname=self.sortname,
                           sortorder=self.sortorder,
                           viewrecords=self.viewrecords,
                           caption=self.caption,
                           shrinkToFit=self.shrinkToFit,
                           height=self.height,
                           width=self.width,
                           autowidth=self.autowidth,
                           toolbar=self.toolbar,
                           rownumbers=self.rownumbers,
                           toppager=self.toppager,
                           multiselect=self.multiselect,
                           multiselectWidth=self.multiselectWidth,
                           postData=self.postData,
                           # events
                           # http://www.trirand.com/jqgridwiki/doku.php?id=wiki:events
                           afterInsertRow = self.afterInsertRow,
                           beforeRequest = self.beforeRequest,
                           beforeSelectRow = self.beforeSelectRow,
                           gridComplete = self.gridComplete,
                           loadBeforeSend = self.loadBeforeSend,
                           loadComplete = self.loadComplete,
                           loadError = self.loadError,
                           onCellSelect = self.onCellSelect,
                           ondblClickRow = self.ondblClickRow,
                           onHeaderClick = self.onHeaderClick,
                           onPaging = self.onPaging,
                           onRightClickRow = self.onRightClickRow,
                           onSelectAll = self.onSelectAll,
                           onSelectRow = self.onSelectRow,
                           onSortCol = self.onSortCol,
                           resizeStart = self.resizeStart,
                           resizeStop = self.resizeStop,
                           serializeGridData = self.serializeGridData,
                           # tree params
                           # http://www.trirand.com/jqgridwiki/doku.php?id=wiki:treegrid
                           ExpandColClick=self.ExpandColClick,
                           ExpandColumn=self.ExpandColumn,
                           treedatatype=self.treedatatype,
                           treeGrid=self.treeGrid,
                           treeGridModel=self.treeGridModel,
                           treeIcons=self.treeIcons,
                           treeReader=self.treeReader,
                           tree_root_level=self.tree_root_level,
                           # sub grids options
                           subGrid=self.subGrid,
                           subGridUrl=self.subGridUrl,
                           subGridModel=self.subGridModel,
                           subGridWidth=self.subGridWidth,
                           # sub grids events
                           subGridRowExpanded=self.subGridRowExpanded,
                           )
        call = js_function('jQuery("#%s").jqGrid' % d.id)(grid_params)
        self.add_call(call)
        # search options documentation can be found at:
        # http://www.trirand.com/jqgridwiki/doku.php?id=wiki:singe_searching#options
        nav_call = js_function('jQuery("#%s").jqGrid' % d.id)\
                                 ('navGrid', '#%s_pager' % d.id,
                                     self.navbuttons_options,
                                     #  default settings for edit
                                     self.editbutton_options,
                                     # default settings for add
                                     self.addbutton_options,
                                     # default settings for delete
                                     self.delbutton_options,
                                     # search parameters
                                     self.search_options,
                                     # view parameters
                                     self.viewbutton_options,
                                     )

        self.add_call(nav_call)


