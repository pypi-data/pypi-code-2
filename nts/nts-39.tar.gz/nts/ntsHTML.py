import wx, wx.html
from nts.ntsRC import *

class MyHtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, pos = wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.html.HtmlWindow.__init__(self, parent, id, pos, size,
            style=wx.BORDER_SUNKEN)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts(htmlfont+4, '', '')
        else:
            self.SetFonts('', '', [i for i in range(htmlfont,
                htmlfont+13, 2)])
    
    def AcceptsFocus(self, *args, **kwargs):
        return False

class NTShtml(wx.Dialog):
    def __init__(self, parent = None, size=wx.DefaultSize, page = ''):
        wx.Dialog.__init__(
            self, parent, -1, 'nts', size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.html = MyHtmlWindow(self, -1, size=size)
        self.html.Bind(wx.EVT_CHAR, self.OnChar)
        self.html.SetBorders(0)
        self.page = page
        self.html.SetPage(self.page)
        self.printer = wx.html.HtmlEasyPrinting()
        self.printer.SetFonts('', '', [i for i in range(htmlprintfont,
            htmlprintfont+13, 2)])
        self.printdata = self.printer.GetPrintData()
        self.printdata.SetColour(False)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        vbox.Add(self.html, 1, wx.EXPAND | wx.ALL, 4)
        sizer.Add(vbox, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 1)
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn2 = wx.Button(self, wx.ID_PRINT)
        self.btn2.SetLabel("Print")
        self.btn2.Bind(wx.EVT_BUTTON, self.OnPrint)
        btnsizer.Add(self.btn2, 0, wx.RIGHT, 3)
        self.btn1 = wx.Button(self, wx.ID_CANCEL)
        self.btn1.Bind(wx.EVT_BUTTON, self.OnCancel)
        self.btn1.SetDefault()
        btnsizer.Add(self.btn1, 0, wx.LEFT, 3)
        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER | wx.BOTTOM, 5)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def OnEnter(self, event):
        event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.btn1.GetId())        
        self.btn1.Command(event) 

    def OnPrint(self, event):
        self.printer.SetHeader(
          '<center><font size="+1">%s</font></center>' %
          self.html.GetOpenedPageTitle())
        self.printer.SetFooter(
                '<center>Page @PAGENUM@ of @PAGESCNT@</center>')
        self.printer.PrintText(self.page)
        
    def OnChar(self, event):
        keycode = event.GetKeyCode()
        if keycode in [27, 17, ord('q'), ord('Q')]:  # Escape, Ctrl-Q, q or Q quit
            self.OnCancel(event)
        elif keycode in [16, ord('p'), ord('P')]: # Ctrl-P, p or P print
            self.OnPrint(event)
        else:
            event.Skip()

    def OnCancel(self, event):
        event.Skip()
        self.Destroy()

class App(wx.App):
    def OnInit(self):
        dlg = NTShtml(size=(300, -1), page="<b>my page</b>")
        response = dlg.Show()    
        return(True)
        
def main():
    app = App(redirect=False)
    app.MainLoop()
    
if __name__ == '__main__':
    main()