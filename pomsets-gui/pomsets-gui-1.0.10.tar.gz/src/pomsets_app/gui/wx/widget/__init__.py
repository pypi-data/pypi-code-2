import wx

ID_DIALOG_SELECTDEFINITION = wx.NewId()
ID_DIALOG_PARAMETERVALUES = wx.NewId()
ID_DIALOG_EXECUTIONPREVIEW = wx.NewId()
ID_DIALOG_TASKMESSAGES = wx.NewId()



class EvtHandler(wx.EvtHandler):
    
    WIDGET_BINDINGS = []
    
    def __init__(self, other):
        self.this = other.this
        self.thisown = 1
        del other.this
        self._setOORInfo(self)
        self.other = other
        
        self.bindWidgets()

        return
    
    
    def getWidget(self, widgetId):
        return wx.xrc.XRCCTRL(self, widgetId)
    
    def bindWidgets(self):
        for xrcId, nameOfFunctionToBind, eventId in self.__class__.WIDGET_BINDINGS:
            functionToBind = getattr(self, nameOfFunctionToBind)
            widget = self.getWidget(xrcId)
            widget.Bind(eventId, functionToBind)
            pass
        return
    
    pass


class Panel(wx.Panel, EvtHandler):

    WIDGET_BINDINGS = []
    
    def __init__(self, xmlResource, parent=None):
        EvtHandler.__init__(
            self, xmlResource.LoadPanel(parent, 'loadedDefinitionPanel'))
        return

    # END class Panel
    pass


class Dialog(wx.Dialog, EvtHandler):

    WIDGET_BINDINGS = [
        ('wxID_OK', 'OnButtonOk', wx.EVT_BUTTON)
    ]

    def __init__(self, other):
        EvtHandler.__init__(self, other)
        return

    def OnButtonOk(self, event):
        self.EndModal(wx.ID_OK)
        return

    pass
