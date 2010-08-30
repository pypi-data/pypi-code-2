import wx
import pomsets_app.gui.widget as WidgetModule

class VerifyExitDialog(WidgetModule.Dialog):

    XRC_NAME = 'VerifyExitDialog'

    WIDGET_BINDINGS = WidgetModule.Dialog.WIDGET_BINDINGS + [
        ('wxID_OK', 'OnButtonOk', wx.EVT_BUTTON),
    ]

    def __init__(self, xmlResource, parent=None):

        WidgetModule.Dialog.__init__(
            self, 
            xmlResource.LoadDialog(parent, VerifyExitDialog.XRC_NAME))

        self.SetSize(wx.Size(300, 300))
        #self.SetAutoLayout(True)


        messageTextCtrl = self.getWidget('messageTextCtrl')
        messageTextCtrl.SetMinSize(wx.Size(275,220))
        # messageTextCtrl.SetSize(wx.Size(250,280))
        messageTextCtrl.SetValue(
"""Thare are unsaved pomsets.
Do you wish to continue exiting the application?
Press OK to exit without saving, Cancel to cancel exit"""
)

        return

    def unsavedPomsetContexts(self, value=None):
        if value is not None:
            self._unsavedPomsetContexts = value
        if not hasattr(self, '_unsavedPomsetContexts'):
            self._unsavedPomsetContexts = []
        return self._unsavedPomsetContexts


    # END class VerifyExitDialog
    pass

