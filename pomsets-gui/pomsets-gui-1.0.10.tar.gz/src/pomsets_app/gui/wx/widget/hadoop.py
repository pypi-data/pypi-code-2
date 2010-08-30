import wx

import pomsets_app.gui.widget as WidgetModule

class ConfigDialog(WidgetModule.Dialog):

    XRC_NAME = 'HadoopDialog'
    WIDGET_BINDINGS = WidgetModule.Dialog.WIDGET_BINDINGS + []

    def __init__(self, xmlResource, parent=None):
        WidgetModule.Dialog.__init__(
            self, xmlResource.LoadDialog(parent, ConfigDialog.XRC_NAME))

        hadoopHomeTextCtrl = self.getWidget('hadoopHomeTextCtrl')
        hadoopHomeTextCtrl.SetMinSize(wx.Size(300, 25))
        streamingJarTextCtrl = self.getWidget('streamingJarTextCtrl')
        streamingJarTextCtrl.SetMinSize(wx.Size(300, 25))

        self.SetMinSize(wx.Size(325, 220))
        self.Fit()
        self.SetAutoLayout(True)
        return


    pass
