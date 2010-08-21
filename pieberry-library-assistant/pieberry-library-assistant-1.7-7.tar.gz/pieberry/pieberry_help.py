import wx, wx.html, os, sys 

class Help(object): 
    def __init__(self): 
        print 'seeking help' 
        programDir = os.path.abspath(sys.path[0]) 
        self.help = wx.html.HtmlHelpController() 
        wx.CallAfter(self.makeOtherFrame, self.help) 
        self.help.AddBook(os.path.join(programDir, 'pieberry', 'help', 'pieberrymanual.hhp')) 
        self.help.DisplayContents() 

    def makeOtherFrame(self, help): 
        parent = help.GetFrame() 
        otherFrame = wx.Frame(parent) 


class MyHtmlFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title)
        p = wx.Panel(self)
        b1 = wx.Button(p, -1, "Show Help Contents")
        self.Bind(wx.EVT_BUTTON, self.OnShowHelpContents, b1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((10,10))
        sizer.Add(b1, 0, wx.ALL, 10)
        p.SetSizer(sizer)
        
        self.InitHelp()

    def InitHelp(self):
        def _addBook(filename):
            if not self.help.AddBook(filename):
                wx.MessageBox("Unable to open: " + filename,"Error", wx.OK|wx.ICON_EXCLAMATION)

        self.help = wx.html.HtmlHelpController()

        _addBook("testing.hhp")


    def OnShowHelpContents(self, evt):
        self.help.DisplayContents()
        self.help.DisplayIndex()
        self.help.Display("sub book")


app = wx.PySimpleApp()
frm = MyHtmlFrame(None, "HTML Help")
frm.Show()
app.MainLoop()
