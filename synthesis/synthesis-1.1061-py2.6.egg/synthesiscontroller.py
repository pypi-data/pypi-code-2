## -*- coding: utf-8 -*- 
#
############################################################################
### Python code generated with wxFormBuilder (version Jun 11 2010)
### http://www.wxformbuilder.org/
###
### PLEASE DO "NOT" EDIT THIS FILE!
############################################################################
#
#import wx
#
############################################################################
### Class MyFrame4
############################################################################
#
#class MyFrame4 ( wx.Frame ):
#	
#	def __init__( self, parent ):
#		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Synthesis Controller", pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
#		
#		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
#		
#		sbSizer4 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )
#		
#		sbSizer5 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )
#		
#		self.m_staticText36 = wx.StaticText( self, wx.ID_ANY, u"You may place CSV or XML files into:", wx.DefaultPosition, wx.DefaultSize, 0 )
#		self.m_staticText36.Wrap( -1 )
#		sbSizer5.Add( self.m_staticText36, 0, wx.ALL, 5 )
#		
#		m_listboxDirectoriesChoices = []
#		self.m_listboxDirectories = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listboxDirectoriesChoices, 0 )
#		sbSizer5.Add( self.m_listboxDirectories, 0, wx.ALL|wx.EXPAND, 5 )
#		
#		self.m_staticText37 = wx.StaticText( self, wx.ID_ANY, u"When you're done converting, press the \"Stop\" button below.", wx.DefaultPosition, wx.DefaultSize, 0 )
#		self.m_staticText37.Wrap( -1 )
#		sbSizer5.Add( self.m_staticText37, 0, wx.ALL, 5 )
#		
#		bSizer3 = wx.BoxSizer( wx.VERTICAL )
#		
#		bSizer6 = wx.BoxSizer( wx.VERTICAL )
#		
#		gSizer2 = wx.GridSizer( 2, 2, 0, 0 )
#		
#		self.m_btnStop = wx.Button( self, wx.ID_ANY, u"S&top", wx.DefaultPosition, wx.DefaultSize, 0 )
#		self.m_btnStop.SetToolTipString( u"Use this to Stop Processing Files" )
#		
#		gSizer2.Add( self.m_btnStop, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL, 5 )
#		
#		gSizer21 = wx.GridSizer( 2, 2, 0, 0 )
#		
#		self.m_btnStart = wx.Button( self, wx.ID_ANY, u"&Start", wx.DefaultPosition, wx.DefaultSize, 0 )
#		self.m_btnStart.SetToolTipString( u"Use this to Start Synthesis File Processor" )
#		
#		gSizer21.Add( self.m_btnStart, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL, 5 )
#		
#		gSizer2.Add( gSizer21, 1, wx.EXPAND, 5 )
#		
#		bSizer6.Add( gSizer2, 1, wx.EXPAND, 5 )
#		
#		bSizer3.Add( bSizer6, 1, wx.EXPAND, 5 )
#		
#		sbSizer5.Add( bSizer3, 1, wx.EXPAND, 5 )
#		
#		sbSizer4.Add( sbSizer5, 1, wx.EXPAND, 5 )
#		
#		self.SetSizer( sbSizer4 )
#		self.Layout()
#		self.m_statusBar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
#		
#		self.Centre( wx.BOTH )
#		
#		# Connect Events
#		self.m_btnStop.Bind( wx.EVT_BUTTON, self.m_btnStopClick )
#		self.m_btnStop.Bind( wx.EVT_ENTER_WINDOW, self.m_btnStopMouseOver )
#		self.m_btnStart.Bind( wx.EVT_BUTTON, self.m_btnStartClick )
#	
#	def __del__( self ):
#		pass
#	
#	
#	# Virtual event handlers, overide them in your derived class
#	def m_btnStopClick( self, event ):
#		event.Skip()
#	
#	def m_btnStopMouseOver( self, event ):
#		event.Skip()
#	
#	def m_btnStartClick( self, event ):
#		event.Skip()
#	
