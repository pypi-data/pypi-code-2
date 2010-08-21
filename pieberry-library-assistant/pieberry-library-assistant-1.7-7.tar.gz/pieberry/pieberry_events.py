#python

import wx

EVT_PIEUPDATE_ID = wx.NewId()
EVT_RESULT_ID = wx.NewId()
EVT_PIEPREFETCH_ID = wx.NewId()

def EVT_PIEUPDATE(win, func):
    win.Connect(-1, -1, EVT_PIEUPDATE_ID, func)

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

def EVT_PIEPREFETCH(win, func):
    win.Connect(-1, -1, EVT_PIEPREFETCH_ID, func)
 
    '''Define event updating user (through outputList) of progress of downloads'''
class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class piePrefetchEvent(wx.PyEvent):
    """Simple event to carry prefetched page info."""
    def __init__(self, tag):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_PIEPREFETCH_ID)
        self.tag = tag

class pieUpdateEvent(wx.PyEvent):
    """Simple event to carry message to the user."""
    def __init__(self, msgtype, msg='', cite=None, href=None, data_id=None, updatelast=False):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_PIEUPDATE_ID)
        self.msgtype = msgtype
        self.msg = msg
        self.cite = cite
        self.href = href
        self.data_id = data_id
        self.updatelast = updatelast
