
import  wx
from pyre.components.Component import Component

class AtomLoader(wx.Dialog):#, Component):
    '''load atoms for various molecular modeling engines'''

    def __init__(self, parent = None,
                 size = (600,400), # wx.DefaultSize,
                 pos = wx.DefaultPosition,
                 style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
                 pyre_component = None, pyre_inventory = None,
                 verbosity = 1, toolkit = None
                 ):

        self.parent = parent

        self.toolkit = toolkit

        #self._registry = GuiElementRegistry()
        
        #self.inventory = InventoryProxy(pyre_inventory)
        self.pyre_component = pyre_component
        self.verbosity = verbosity

        #apptitle = "Component: %s" % pyre_component.name
        apptitle = "Settings of Loader"    
        
        wx.Dialog.__init__(self,parent = None)
        
        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        
#        pre = wx.PreDialog()
#        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
#        pre.Create(parent, -1, apptitle, pos, size, style)
#        
#        # This next step is the most important, it turns this Python
#        # object into the real wrapper of the dialog (instead of pre)
#        # as far as the wxPython extension is concerned.
#        
#        self.PostCreate(pre)
                
        l3 = wx.StaticText(self, -1, "Multi-line")
        self.t3 = wx.TextCtrl(self, -1,
                        "Atom   x    y    z\n",
                       size=(200, 100), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
#        sizer = wx.FlexGridSizer(cols=3, hgap=space, vgap=space)
#        sizer.AddMany([ l3, t3, (0,0)])
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(self.t3, 0, wx.ALL, 25)
        self.SetSizer(border)
        self.SetAutoLayout(True)
        
    def atoms(self):
        return self.t3.GetValue()
    
    
if __name__ == "__main__":
#    demo_plotter(sample_graph())
    
    # Make a frame to show it
    app = wx.PySimpleApp()
    frame = AtomLoader()
    #frame = wx.Frame(None,-1,'Plottables')
    #plotter = Plotter(frame)
    frame.Show()
    app.MainLoop()
