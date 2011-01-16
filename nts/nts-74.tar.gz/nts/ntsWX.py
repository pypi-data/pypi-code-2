#!/usr/bin/env python

import wx, wx.html, subprocess
from nts.ntsData import *
from nts.ntsDocs import *
import wx.lib.dialogs
import  wx.stc as stc

# for the edge normal color
NORMAL = '#E5E5E5'
# for the edge modified color
ACTIVE = '#33FF00'
MODIFIED = '#FF6103'
# for search highlighting
SEARCHF = '#000000'
SEARCHB = '#FFE303'

wx.SetDefaultPyEncoding(encoding)

from pkg_resources import resource_filename

options = get_opts()
filters = get_filters(options)

ID_BUTTON=100
ID_SPLITTER=300

try:
    import markdown
    import markdown.extensions.abbr
    import markdown.extensions.footnotes
    import markdown.extensions.tables
    import markdown.extensions.def_list
    import markdown.extensions.fenced_code
    import markdown.extensions.headerid
    markdown_version = markdown.version
    has_markdown = True
except:
    has_markdown = False
    markdown_version = 'none'
try:
    from docutils import __version__ as docutils_version
    from docutils.core import publish_string
    has_docutils = True
except:
    docutils_version = 'none'
    has_docutils = False

if pandoc:
    # get pandoc version
    try:
        p = subprocess.Popen("%s -v | head -n1" % pandoc, shell=True, stdout = subprocess.PIPE)
        ret = p.stdout.read()
        pandoc_version = ret.split()[1]
        has_pandoc = True
    except:
        pandoc = None
        pandoc_version = "none"
        has_pandoc = False
else:
    pandoc_version = "none"
    has_pandoc = False

def sysinfo():
    from platform import python_version as pv
    wxv = "%s.%s.%s" % (wx.MAJOR_VERSION, 
                wx.MINOR_VERSION, wx.RELEASE_VERSION)
    sysinfo = "platform %s; python %s; wx(Python) %s" % (sys.platform, pv(), wxv)
    return(sysinfo)

def newer_alert():
    ok, res = get_newer()
    if ok and res:
        msg = "%s\n\n  Set 'newer = False' in %s\n  to prevent this check for newer releases." % (res, ntsrc)
        dlg = wx.MessageDialog(None, msg,  'nts', wx.OK )
        dlg.ShowModal() 
    return(True)


if "wxMac" in wx.PlatformInfo:
    notepad_type = 'png'
    notepad = "NTS_128.png"
elif "wxMSW" in wx.PlatformInfo:
    notepad_type = 'ico'
    notepad = "NTS.ico"
elif "wxGTK" in wx.PlatformInfo:
    notepad_type = 'png'
    notepad = "NTS_32.png"
else:
    notepad_type = ''
    notepad = ''

if notepad:
    try:
        nts_notepad = resource_filename(__name__, notepad)
    except:
        nts_notepad = notepad

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

class MyTaskBarIcon(wx.TaskBarIcon):
    TBMENU_SHOW  = wx.NewId()
    TBMENU_HIDE  = wx.NewId()
    TBMENU_CLOSE = wx.NewId()

    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        if notepad_type == 'ico':
            self.SetIcon(wx.Icon(nts_notepad, wx.BITMAP_TYPE_ICO), 'nts')
        elif notepad_type == 'png':
            self.SetIcon(wx.Icon(nts_notepad, wx.BITMAP_TYPE_PNG), 'nts')

        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarActivate)
        self.Bind(wx.EVT_MENU, self.OnTaskBarActivate, id=self.TBMENU_SHOW)
        self.Bind(wx.EVT_MENU, self.OnTaskBarDeActivate, id=self.TBMENU_HIDE)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.TBMENU_SHOW, "Show")
        menu.Append(self.TBMENU_HIDE, "Hide")
        menu.AppendSeparator()
        menu.Append(self.TBMENU_CLOSE, "Close")
        return menu

    def OnTaskBarClose(self, event):
        self.frame.Close()

    def OnTaskBarActivate(self, event):
        if "wxMSW" in wx.PlatformInfo and self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()

    def OnTaskBarDeActivate(self, event):
        if self.frame.IsShown():
            self.frame.Hide()

# vars = {'version': version, 'copyright' : copyright, 'ntsinfo' : ntsinfo(), 'sysinfo' : sysinfo(), 'markup' : markup(), 'ntstxt' : ntstxt, 'ntsenc' : ntsenc, 'ntsexport' : os.path.join(ntsexport, 'export.rst'), 'ntsrc' : ntsrc, 'ntsdata' : ntsdata, 'grandchild' :  os.path.join(ntsdata,'parent', 'child', 'grandchild.txt')}

class MyTree(wx.TreeCtrl):
    def __init__(self, parent, id, position, size, style):
        wx.TreeCtrl.__init__(self, parent, id, position, size, style)
        # lofl item: (description, content, tags, id, path) 
        self.displayed = []
        self.rel_path = ''
        self.line_beg = 0
        self.show_id = None
        self.MakeTree(options, filters)

    def SetActive(self, rel_path, line_beg):
        self.rel_path = rel_path
        self.line_beg = line_beg

    def MakeTree(self, options, filters):
        self.DeleteAllItems()
        root = self.AddRoot('root')
        self.root = root
        self.id2item = {}
        lofl = make_tree(options, filters)
        paths = []
        parentof = {}
        self.id2note = {}
        self.displayed = []
        self.show_id = None
        for note in lofl:
            id = note[3]
            self.id2note[note[3]] = note
            self.displayed.append((note[0], note[3]))
            path = note[4]
            # the last component of path is the leaf (.txt)
            for i in range(len(path)+1):
                part = path[:i]
                if part and part not in paths:
                    full_node = ""
                    for node in part:
                        full_node = os.path.join(full_node, node)
                    paths.append(part)
                    description = note[0]
                    if i == 1: 
                        parentof[part[-1]] = self.AppendItem(root,
                            part[-1])
                    else: 
                        parentof[part[-1]] = self.AppendItem(
                                parentof[part[-2]], part[-1])
                    if i == len(path):
                        self.SetPyData(parentof[part[-1]], 
                            (note[0], '', '', (note[3][0],0,0), full_node))
                    else:
                        self.SetPyData(parentof[part[-1]], 
                            (note[0], '', '', (), full_node))

            description = "%s" % note[0]
            parentof[description] = self.AppendItem(
                    parentof[part[-1]], description)
            self.id2item[note[3]] = parentof[description]
            if (self.rel_path and id[0] == self.rel_path and 
                    id[1] == self.line_beg):
                # save this item to make visible in OnReload
                self.show_id = parentof[description]
            text = "%s" % ("\n".join(note[1]))

            if note[2] and 'none' not in note[2]:
                tag_str = "(%s)" % ', '.join(note[2])
            else:
                tag_str = ""
            content = (description, text, tag_str, id, path)
            self.SetPyData(parentof[description], content)
        num = len(self.id2item.keys())
        if len(lofl) == 1:
            self.num_notes = "%s note" % num
        else:
            self.num_notes = "%s notes" % num
        self.SetPyData(root, ('', '', '', (), ""))


class MySTC(stc.StyledTextCtrl):
    def __init__(self, parent, ID):
        stc.StyledTextCtrl.__init__(self, parent, ID, size=(80,40))

        self.Bind(stc.EVT_STC_MODIFIED, self.OnModified)

        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)
        self.editable = False
        self.modified = False
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:%s" % NORMAL)
        # style 1 is for the search highlight
        self.StyleSetSpec(1, "fore:%s,back:%s" % (SEARCHF, SEARCHB))
        self.SetCaretWidth(2)
        self.SetMarginWidth(0,0)
        self.SetMarginWidth(1,4)
        self.SetMarginType(1, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(1, 0)  
        self.SetMarginType(2, stc.STC_MASK_FOLDERS)
        self.SetMarginWidth(2, 0)
        self.SetMargins(4,1)

        self.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS,  "white", "black")


    def OnDestroy(self, evt):
        wx.TheClipboard.Flush()
        evt.Skip()

    def ChangeValue(self, txt):
        self.SetReadOnly(False)
        self.SetText(txt)
        self.SetReadOnly(True)

    def GetValue(self):
        return self.GetText()

    def SetEditable(self, bool):
        self.editable = bool
        if bool:
            self.SetReadOnly(False)
            self.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:%s" % ACTIVE)
        else:
            self.SetReadOnly(True)
            self.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:%s" % NORMAL)

    def IsEditable(self):
        return self.editable

    def IsModified(self):
        return self.CanUndo()

    def SetStyle(self, b, e, ignore):
        self.StartStyling(b, 0xff)
        self.SetStyling(e-b, 1)

    def OnModified(self, evt):
        if self.IsEditable():
            if self.CanUndo():
                self.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:%s" % MODIFIED)
            else:
                self.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:%s" % ACTIVE)
        else:
            self.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:%s" % NORMAL)

    def getModType(self, evt):
        modType = evt.GetModificationType()
        st = ""
        table = [(stc.STC_MOD_INSERTTEXT, "InsertText"),
                 (stc.STC_MOD_DELETETEXT, "DeleteText"),
                 (stc.STC_MOD_CHANGESTYLE, "ChangeStyle"),
                 (stc.STC_MOD_CHANGEFOLD, "ChangeFold"),
                 (stc.STC_PERFORMED_USER, "UserFlag"),
                 (stc.STC_PERFORMED_UNDO, "Undo"),
                 (stc.STC_PERFORMED_REDO, "Redo"),
                 (stc.STC_LASTSTEPINUNDOREDO, "Last-Undo/Redo"),
                 (stc.STC_MOD_CHANGEMARKER, "ChangeMarker"),
                 (stc.STC_MOD_BEFOREINSERT, "B4-Insert"),
                 (stc.STC_MOD_BEFOREDELETE, "B4-Delete")
                 ]
        for flag,text in table:
            if flag & modType:
                st = st + text + " "
        if not st:
            st = 'UNKNOWN'
        return st

    def AcceptsFocus(self, *args, **kwargs):
        print "accepts focus?", self.editable
        return self.editable


class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title,
                          wx.DefaultPosition, wx.Size(840, 400))
        self.SetBackgroundColour('#EEEEEE')
        if notepad_type == 'ico':
            self.SetIcon(wx.Icon(nts_notepad, wx.BITMAP_TYPE_ICO))
            self.tbicon = MyTaskBarIcon(self)
        elif notepad_type == 'png':
            self.SetIcon(wx.Icon(nts_notepad, wx.BITMAP_TYPE_PNG))
            self.tbicon = MyTaskBarIcon(self)
        self.Bind(wx.EVT_ICONIZE, self.OnIconify)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        # outline tree
        if mono_tree:
            tfont = wx.Font(font_size, wx.MODERN, wx.NORMAL, wx.NORMAL)
        else:
            tfont = wx.Font(font_size, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        # display panel view mode
        if mono_display:
            dfont = wx.Font(font_size, wx.MODERN, wx.NORMAL, wx.NORMAL)
        else:
            dfont = wx.Font(font_size, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        # display panel edit mode
        if mono_edit:
            efont = wx.Font(font_size, wx.MODERN, wx.NORMAL, wx.NORMAL)
        else:
            efont = wx.Font(font_size, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.dfont = dfont
        self.efont = efont
        self.markup = None
        # labels in the option panel
        lfont = wx.Font(font_size - 1, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        # buttons in the option panel
        bfont = wx.Font(font_size - 1, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        # entry fields in the option panel
        ofont = wx.Font(font_size, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        # monospaced font for the help display
        mfont = wx.Font(font_size, wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.mfont = mfont
        self.splitter = wx.SplitterWindow(self, ID_SPLITTER,
                style = wx.SP_LIVE_UPDATE)
        leftPanel = wx.Panel(self.splitter, -1, 
                style = wx.LC_LIST | wx.NO_FULL_REPAINT_ON_RESIZE)
        leftBox = wx.BoxSizer(wx.VERTICAL)
        self.hofh = {}
        self.content = ''
        self.local_filters = get_filters({})
        self.hofh = load_data({})
        self.tree = MyTree(leftPanel, -1, wx.DefaultPosition, 
            wx.DefaultSize,
            wx.TR_HIDE_ROOT
            | wx.TR_HAS_BUTTONS
            )
        self.tree.SetBackgroundColour("white")
        self.tree.Bind(wx.EVT_CHAR, self.OnChar)
        leftBox.Add(self.tree, 1, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM,
                4)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnSelActivated)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGING, self.OnSelChanging)
        self.tree.SetFont(tfont)
        leftPanel.SetSizer(leftBox)
        rightPanel = wx.Panel(self.splitter, -1, size = wx.DefaultSize,
            style=wx.SP_3D)
        rightBox = wx.BoxSizer(wx.VERTICAL)
        self.display = MySTC(rightPanel, -1)
        self.display.SetWrapMode(True)
        self.display.Bind(wx.EVT_CHAR, self.OnDisplayChar)
        self.display.Bind(wx.EVT_KEY_DOWN, self.OnDisplayChar)
        self.display.Bind(wx.EVT_LEFT_DCLICK, self.OnSelActivated)
        self.display.StyleSetFont(stc.STC_STYLE_DEFAULT, dfont)
        rightBox.Add(self.display, 1, wx.EXPAND | wx.ALL, 4)
        rightPanel.SetSizer(rightBox)
        self.splitter.SplitVertically(leftPanel, rightPanel, 270)

        self.optionbar = wx.BoxSizer(wx.HORIZONTAL)
        button1 = wx.StaticText(self, ID_BUTTON + 1, "^O ")
        button1.SetFont(lfont)
        self.gb = wx.Choice(self, ID_BUTTON + 2, choices = ['p', 't'])
        self.gb.SetFont(bfont)
        button3 = wx.StaticText(self, ID_BUTTON + 3, "^P ")
        button3.SetFont(lfont)
        self.pf = wx.TextCtrl(self, ID_BUTTON + 4, "")
        self.pf.SetFont(ofont)
        self.pf.Bind(wx.EVT_CHAR, self.OnOptChar)
        button5 = wx.StaticText(self, ID_BUTTON + 5, "^T ")
        button5.SetFont(lfont)
        self.tf = wx.TextCtrl(self, ID_BUTTON + 6, "")
        self.tf.SetFont(ofont)
        self.tf.Bind(wx.EVT_CHAR, self.OnOptChar)
        button7 = wx.StaticText(self, ID_BUTTON + 7, "^F ")
        button7.SetFont(lfont)
        self.ff = wx.TextCtrl(self, ID_BUTTON +8, "")
        self.ff.SetFont(ofont)
        self.ff.Bind(wx.EVT_CHAR, self.OnOptChar)
        # apply
        self.eb = wx.Button(self, ID_BUTTON +9, "F4: APPLY", style = wx.BU_EXACTFIT)
        self.eb.SetFont(bfont)
        self.Bind(wx.EVT_BUTTON, self.OnEnter, self.eb)
        self.cb = wx.Button(self, ID_BUTTON +10, "F3: CLEAR", style = wx.BU_EXACTFIT)
        self.cb.SetFont(bfont)
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.cb)
        self.hb = wx.Button(self, ID_BUTTON +11, "F1: HELP", style = wx.BU_EXACTFIT)
        self.hb.SetFont(bfont)
        self.Bind(wx.EVT_BUTTON, self.OnHelp, self.hb)
        s = 8
        self.optionbar.Add(button1, 0, wx.EXPAND | wx.LEFT, s)
        self.optionbar.Add(self.gb, 0, wx.EXPAND | wx.RIGHT, s)
        self.optionbar.Add(button3, 0, wx.EXPAND | wx.LEFT, s)
        self.optionbar.Add(self.pf, 1, wx.EXPAND | wx.RIGHT, s)
        self.optionbar.Add(button5, 0, wx.EXPAND | wx.LEFT, s)
        self.optionbar.Add(self.tf, 1, wx.EXPAND | wx.RIGHT, s)
        self.optionbar.Add(button7, 0, wx.EXPAND | wx.LEFT, s)
        self.optionbar.Add(self.ff, 1, wx.EXPAND | wx.RIGHT, s)
        self.optionbar.Add(self.hb, 0, wx.EXPAND | wx.RIGHT, s)
        self.optionbar.Add(self.cb, 0, wx.EXPAND | wx.RIGHT, s)
        self.optionbar.Add(self.eb, 0, wx.EXPAND  | wx.RIGHT, s)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.splitter, 1, wx.EXPAND)
        self.vbox.Add(self.optionbar, 0, wx.EXPAND | wx.BOTTOM, 2)
        self.SetSizer(self.vbox)

        self.tree.SetFocus()
        self.treeFocused = True
        self.modified = False
        self.leaf_selected = False
        self.node_selected = False
        self.selected_id = ()
        self.active_id = ()
        nts_count = self.CountChildren(self.tree.root)
        self.SetTitle("nts (%s)" % self.tree.num_notes)
        self.content = nts_count
        self.display.ChangeValue(nts_count)
        self.Centre()
        if newer:
            newer_alert()
        self.tree.SetFocus()

    def CountChildren(self, item):
        children = self.tree.GetChildrenCount(item, recursively=False)
        if item == self.tree.root:
            head = "Displayed:"
        else:
            head = "The selected item has:"
        if children == 1:
             nts_children= "%d child" %1
        else:
            nts_children = "%d children" % children
        other = self.tree.GetChildrenCount(item)
        descendants = other - children
        if descendants == 1:
             nts_descendants= " and %d other descendant" % 1
        else:
            nts_descendants = " and %d other descendants" % descendants
        if descendants > 0:
            nts_count = "%s%s" % (nts_children, nts_descendants)
        else:
            nts_count = "%s" % (nts_children)
        return(nts_count)

    def OnIconify(self, event):
        if "wxMSW" in wx.PlatformInfo:
            self.Hide()

    def OnSelChanged(self, event):
        item =  event.GetItem()
        self.selected = item
        self.leaf_selected = ()
        self.node_selected = ()
        content = self.tree.GetPyData(item)
        #  content: 0:description, 1:text, 2:tag_str, 3:id, 4:path)
        if content[3]:
            self.selected_id = content[3]
            self.leaf_selected = content[3]
            if content[2]:
                tag_str = " %s" % content[2]
            else:
                tag_str = ""
            if content[3][1]:
                detail_str = "%s\n\n-- %s%s" % (content[1], 
                        ':'.join(map(str, content[3])),
                        tag_str)

                self.display.ChangeValue("%s" % detail_str)
                if (self.local_filters['find_regex'] and 
                    not self.local_filters['neg_find']):
                    for m in self.local_filters['find_regex'].finditer(detail_str):
                        b, e = m.span()
                        self.display.SetStyle(b, e, wx.TextAttr(wx.RED))
            else:
                nts_count = self.CountChildren(item)
                self.display.ChangeValue(nts_count)
        else:
            self.selected_id = (content[4], 0, 0)
            self.node_selected = content[4]
            nts_count = self.CountChildren(item)
            self.display.ChangeValue(nts_count)
        self.content = self.display.GetValue()

    def OnSelActivated(self, event):
        item = self.selected
        if self.display.IsEditable():
            event.Skip()
            return()
        # Display the selected item text in the text widget
        item = self.tree.GetPyData(item)
        if item[1]:
            if item[2]:
                tag_str = " %s" % item[2]
            else:
                tag_str = ""
            self.display.StyleSetFont(stc.STC_STYLE_DEFAULT, self.efont)
            self.display.ChangeValue("+ %s%s\n%s" % (item[0], tag_str, item[1]))
            self.active_id = item[3]
            self.selected_id = item[3]
            self.treeFocused = False
            self.display.SetFocus()
            self.display.DocumentStart()
            self.display.EmptyUndoBuffer()
            self.display.SetEditable(True)

    def DeActivate(self):
        if self.display.IsEditable() and self.display.IsModified():
            dlg = wx.MessageDialog(None, 'abandon changes?',  'nts',
                wx.YES_NO | wx.YES_DEFAULT )
            if dlg.ShowModal() == wx.ID_NO:
                return () 
            self.display.SetEditable(False)
        self.display.StyleSetFont(stc.STC_STYLE_DEFAULT, self.dfont)
        self.display.ChangeValue(self.content)
        self.treeFocused = True
        self.active_id = ()
        self.display.SetEditable(False)
        self.tree.SetFocus()

    def OnSelChanging(self, event):
        item =  event.GetItem()
        if self.display.IsEditable() and self.display.IsModified():
            event.Veto()
            dlg = wx.MessageDialog(None, 'abandon changes?',  'nts',
                    wx.YES_NO | wx.YES_DEFAULT )
            if dlg.ShowModal() == wx.ID_NO:
                self.display.SetFocus()
                self.treeFocused = False
                return ()
        self.display.SetEditable(False)
        self.treeFocused = True
        self.active_id = ()
        self.tree.SetFocus()
        self.display.ChangeValue(self.content)
        event.Skip()

    def ToggleFocus(self):
        if self.treeFocused:
            self.display.SetFocus()
            self.treeFocused = False
        else:
            self.DeActivate()

    def OnChar(self, event):
        keycode = event.GetKeyCode()        # for arrow keys
        ukeycode = event.GetUnicodeKey()    # for control keys
        shift = event.ShiftDown()
        control = event.ControlDown()
        modifier = event.GetModifiers()
        #  print "OnChar", modifier, keycode, ukeycode
        if keycode == 27:               # ESC
            self.DeActivate()
        elif keycode == wx.WXK_LEFT:
            if (control and self.selected and 
                    self.tree.IsSelected(self.selected)):
                parent = self.tree.GetItemParent(self.selected)
                if parent == self.tree.root:
                    self.tree.CollapseAllChildren(self.selected)
                else:
                    self.tree.CollapseAllChildren(parent)
            elif (self.selected and self.tree.IsSelected(self.selected) and
                self.tree.ItemHasChildren(self.selected)):
                self.tree.CollapseAllChildren(self.selected)
            event.Skip()
        elif control and keycode == wx.WXK_RIGHT:
            if (self.tree.IsSelected(self.selected) and
                self.tree.ItemHasChildren(self.selected)):
                self.tree.ExpandAllChildren(self.selected)
            event.Skip()
        elif modifier == 2 and ukeycode == 3:           # Ctrl-C convert
            self.OnConvert()

        elif modifier == 2 and ukeycode == 8:           # Ctrl-H html
            ids = self.getIDs()
            if ids:
                self.OnHTML(ids)
        elif ukeycode == 12:                             # ^L log file
            self.OnInfo()
        elif control and ukeycode == 13 and self.leaf_selected:  # Ctrl-M move
            # Return generates 13 as well but not control
			self.OnMove()
        elif ukeycode == 14:           # Ctrl-N add new note
            self.OnNew()
        elif ukeycode == 24:           # Ctrl-X export
            ids = self.getIDs()
            if ids:
                str = self.OnExport(ids)
        elif ukeycode == 17:           # Ctrl-Q quit
            self.OnQuit()
        elif ukeycode == 18:           # Ctrl-R reload
            self.hofh = {}
            self.ReloadData()
        elif ukeycode == 21:           # Ctrl-U unselect all
            self.UnselectAll()
        elif modifier == 0 and ukeycode in [8, 127] and self.leaf_selected:
            self.OnDelete()
        elif keycode == wx.WXK_TAB:
            self.ToggleFocus()
        elif keycode == wx.WXK_F1: 
            self.OnHelp(event)
        elif keycode == wx.WXK_F2: 
            self.OnAbout(event)
        elif keycode == wx.WXK_F3: 
            self.OnClear(event)
        elif keycode == wx.WXK_F4: 
            self.OnEnter(event)
        elif keycode == wx.WXK_F5: 
            self.OnOpen()
        elif ukeycode in [15, 16, 20, 6]: # ^O, ^P, ^T, ^F
            #  print "calling setfocus", ukeycode
            self.setfocus(event, ukeycode)
        else:
            event.Skip()

    def OnDisplayChar(self, event):
        keycode = event.GetKeyCode()
        ukeycode = event.GetUnicodeKey()    # for control keys
        shift = event.ShiftDown()
        control = event.ControlDown()
        modifier = event.GetModifiers()
        #  print "OnDisplayChar", modifier, control, shift, keycode, ukeycode
        if keycode == wx.WXK_F1: 
            self.OnHelp(event)
        elif keycode == wx.WXK_F2: 
            self.OnAbout(event)
        else:
            if self.display.IsEditable():
                if ukeycode == 17:           # Ctrl-Q quit
                    self.DeActivate()
                elif control and ukeycode == 19:           # Ctrl-S save
                    self.OnSave(event, False)
                else:
                    event.Skip()
            else:
                if keycode == wx.WXK_TAB:
                    self.ToggleFocus()
                elif keycode == 13:    # enter
                    self.OnSelActivated(event)
                else:
                    #  print "calling OnChar", ukeycode
                    self.OnChar(event)

    def OnOptChar(self, event):
        keycode = event.GetKeyCode()
        shift = event.ShiftDown()
        control = event.ControlDown()
        if keycode in [15, 16, 20, 6]: # ^O, ^P, ^T, ^S 71, 80, 84, 83
            self.setfocus(event, keycode+64)
        elif keycode == 13:    # enter
            if control:
                self.OnClear(event)
            else:
                self.OnEnter(event)
        elif keycode == 17:           # Ctrl-Q quit
            self.OnQuit()
        if keycode == 27:               # ESC
            if self.treeFocused:
                self.tree.SetFocus()
            else:
                self.display.SetFocus()
        elif keycode == wx.WXK_F1: 
            self.OnHelp(event)
        elif keycode == wx.WXK_F2: 
            self.OnAbout(event)
        elif keycode == wx.WXK_F3: 
            self.OnClear(event)
        elif keycode == wx.WXK_F4: 
            self.OnEnter(event)
        else:
            event.Skip()

    def OnAbout(self, event):
        info = wx.AboutDialogInfo()
        info.Name = "nts"
        info.Version = "%s" % version
        info.Copyright = "(C) %s Daniel A. Graham" % copyright
        info.Description = description
        info.WebSite = ("http://www.duke.edu/~dgraham/NTS", 
                "nts home page")
        info.Developers = [ "Daniel A. Graham <daniel.graham@duke.edu>", ]

        info.License = license
        wx.AboutBox(info)

    def OnEnter(self, evt):
        local_options = options
        local_options['outlineby']  = ['p', 't'][self.gb.GetCurrentSelection()]
        local_options['path']  = self.pf.GetValue()
        local_options['tag']  = self.tf.GetValue()
        local_options['find']  = self.ff.GetValue()
        local_filters = get_filters(local_options)
        self.local_filters = local_filters
        self.tree.MakeTree(local_options, local_filters)
        nts_count = self.CountChildren(self.tree.root)
        self.SetTitle("nts (%s)" % self.tree.num_notes)
        self.display.ChangeValue(nts_count)
        if local_options['path'] or local_options['tag'] or local_options['find']:
            self.tree.ExpandAll()
        self.tree.SetFocus()

    def ReloadData(self):
        local_options = options
        self.hofh = load_data(self.hofh)
        self.tree.MakeTree(options, filters)
        nts_count = self.CountChildren(self.tree.root)
        self.SetTitle("nts (%s)" % self.tree.num_notes)
        self.display.ChangeValue(nts_count)
        self.tree.SetFocus()
        if self.tree.show_id:
            self.tree.EnsureVisible(self.tree.show_id)
            self.tree.SelectItem(self.tree.show_id)


    def UnselectAll(self):
        nts_count = self.CountChildren(self.tree.root)
        self.display.ChangeValue(nts_count)
        self.treeFocused = True
        self.active_id = ()
        self.selected_id = ()
        self.leaf_selected = False
        self.node_selected = False
        self.tree.SetFocus()
        self.tree.UnselectAll()

    def OnClear(self, evt):
        gb = self.gb.SetSelection(0)
        self.pf.SetValue('')
        self.tf.SetValue('')
        self.ff.SetValue('')

    def setfocus(self, event, key):
        if key == 15:
            # toggle outlineby
            old_gb = self.gb.GetCurrentSelection()
            new_gb = (old_gb + 1) % 2
            self.gb.SetSelection(new_gb)
            self.OnEnter(event)
        elif key == 16:
            self.pf.SetFocus()
        elif key == 20:
            self.tf.SetFocus()
        elif key == 6:
            self.ff.SetFocus()
        else:
            pass

    def OnSave(self, event, must_exist = False):
        if not self.display.IsEditable() or not self.display.IsModified():
            return()
        #  note_id: (relative_path, beginning_line, ending_line) 
        id = self.active_id
        lines = self.ContentLines()
        if id:
            # this is an existing note
            rel_path = id[0]
            line_beg = noteReplace(id, lines)
        else:
            # this is a new note
            file = self.getFile("Append new note to", must_exist)
            if file:
                root, ext = os.path.splitext(file)
                if ext not in [ntstxt, ntsenc]: 
                    # make ntstxt the default
                    file = "%s%s" % (root, ntstxt)
                    if ext:
                        # only confirm use of default for bad extensions
                        dlg = wx.MessageDialog(None, 
                            'The file extension "%s" was provided but should either\nbe "%s" or "%s". The default extension "%s" and file\n\n            "%s"\n\nwill be used.  Is this OK?' % (ext, ntstxt, ntsenc, ntstxt, file),  
                            'nts',
                            wx.YES_NO | wx.YES_DEFAULT )
                        if dlg.ShowModal() == wx.ID_NO:
                                return(False) 
                line_beg = noteAdd(file, lines)
                rel_path = relpath(file, ntsdata)
            else:
                line_beg = False
        if line_beg:
            #  self.display.SetModified(False)
            self.display.SetEditable(False)
            #  self.display.SetBackgroundColour('white')
            self.treeFocused = True
            self.active_id = ()
            self.tree.SetActive(rel_path, line_beg)
            self.ReloadData()
            self.tree.SetFocus()
        return(line_beg)

    def getSelection(self, prompt, choices, dflt=None):
        dlg = wx.SingleChoiceDialog(self, prompt, 'nts',
                choices, wx.CHOICEDLG_STYLE)
        if dflt:
            dlg.SetSelection(dflt)
        if dlg.ShowModal() == wx.ID_OK:
            return dlg.GetStringSelection()
        else:
            return ""

    def getFile(self, prompt, must_exist = False):
        file = None
        wildcard = "nts plain text files (*%s)|*%s|nts encoded files (*%s)|*%s|all files (*.*)|*.*"  % (ntstxt, ntstxt, ntsenc, ntsenc) 
        if must_exist:
            style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        else:
            #  style = wx.FD_SAVE
            style = wx.FD_SAVE
            #  style = wx.FD_OPEN
        filedlg = wx.FileDialog(
                self, message = prompt,
                defaultDir = ntsdata,
                defaultFile="%s" % quick,
                wildcard = wildcard,
                style=style
        )
        #  filedlg.SetWildcard(wildcard)
        if filedlg.ShowModal() == wx.ID_OK:
            file = filedlg.GetPath()
            if file:
                return(os.path.join(ntsdata, file))
        return()

    def getIDs(self):
        choices = ['ALL OF THE FOLLOWING']
        ids = []
        selected = []
        for note in self.tree.displayed:
            choices.append("%s [%s]" % (note[0], ":".join(map(str,note[1]))))
            ids.append(note[1])
        dlg = wx.MultiChoiceDialog(self, "notes to include", 'nts',
               choices)
        if self.selected_id:
            if self.selected_id in ids:
                # add one because inserting ALL makes the choices index 1
                # greater than the ids index
                selected.append(ids.index(self.selected_id)+1)
            else:
                # a note is not selected so get the path to the node and 
                # append all descendent notes
                for i in range(len(choices)):
                    if self.selected_id[0] in choices[i]:
                        selected.append(i)
            dlg.SetSelections(selected)
        if dlg.ShowModal() == wx.ID_OK:
            indices = dlg.GetSelections()
        else:
            indices = []
        if 0 in indices:
            return(ids)
        else:
            return([ids[i-1] for i in indices])

    def MarkUp(self, ids):
        out = []
        if ids:
            if markup in ['md', 'pd']:
                # out = ['# nts #']
                out = []
            else:
                out = ['nts', '===', '']
            for id in ids:
                note = self.tree.id2note[id]
                if markup in ['md', 'pd']:
                    out.append("### %s ###" % note[0])
                    # out.append('')
                else: 
                    out.append(note[0])
                    out.append('-'*len(note[0]))
                    out.append('')
                for line in note[1]:
                    out.append("%s" % line)
                out.append('')
        return(out)

    def OnExport(self, ids):
        '''Export selected notes in md or rst format'''
        out = self.MarkUp(ids)
        if out:
            export_file = os.path.join(ntsexport, 'export.%s' % markup)
            fo = codecs.open(export_file, 'w', encoding, 'replace')
            fo.writelines(["%s\n" % x for x in out])
            fo.close()

    def OnInfo(self):
        f = os.path.join(ntsexport, 'messages.log')
        fo = open
        fo = codecs.open(f, 'r', encoding, 'replace')
        messages = fo.readlines()
        fo.close()
        message = "".join(messages)
        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, message,
                'nts message log')
        dlg.ShowModal()

    def CheckMarkup(self):
        if not self.markup:
            md = "markdown %s" % markdown_version
            du = "docutils %s" % docutils_version
            pd = "pandoc %s" % pandoc_version
            self.markup = "%s; %s; %s" % (du, md, pd)

    def OnHTML(self, ids):
        '''Show selected notes in HTML window'''
        html = ''
        out = self.MarkUp(ids)
        if out:
            txt = "\n".join(out)
        else:
            return()
        if markup == 'pd' and has_pandoc: 
            p = subprocess.Popen([pandoc, '-t html'], shell = True, 
                    stdout = subprocess.PIPE, stdin = subprocess.PIPE, 
                    stderr = subprocess.PIPE)
            html, err = p.communicate(txt.encode(encoding))
        elif markup == 'md' and has_markdown: 
            html = markdown.markdown(txt, 
                    ['abbr', 'footnotes', 'tables', 
                        'def_list', 'fenced_code', 'headerid'])
        elif markup == 'rst' and has_docutils:
            if stylesheet:
                customcss = {'embed_stylesheet':False, 
                'stylesheet_path':stylesheet}
                html = publish_string(source=txt, writer_name='html',
                    settings_overrides=customcss)
            else:
                html = publish_string(source=txt, writer_name='html')
        dlg = NTShtml(self, size=(600,340), page = html)
        dlg.Show(True)

    def OnNew(self):
        self.display.ChangeValue("+ ")
        self.display.SetEditable(True)
        self.active_id = ()
        self.treeFocused = False
        self.display.SetFocus()
        self.display.GotoPos(2)

    def OnDelete(self):
        dlg = wx.MessageDialog(None, 'delete note?',  'nts',
            wx.YES_NO | wx.YES_DEFAULT )
        if dlg.ShowModal() == wx.ID_NO:
                return ()
        res = noteDelete(self.leaf_selected)
        self.tree.SetActive('', 0)
        if res == 2:
            del self.hofh[self.leaf_selected[0]]
        if res:
            self.active_id = ()
            self.tree.SetFocus()
            self.ReloadData()
        return(True)

    def OnConvert(self):
        orig_file = self.getFile("File to convert", True)
        if orig_file:
            pathname, ext = os.path.splitext(orig_file)
            if ext == ntsenc:
                new_ext = ntstxt
                tocrypted = False
            else:
                new_ext = ntsenc
                tocrypted = True
            new_file = "%s%s" % (pathname, new_ext)
            dlg = wx.MessageDialog(None, 'convert %s\nto %s?' % (orig_file, new_file),  'nts',
                wx.YES_NO | wx.YES_DEFAULT )
            if dlg.ShowModal() == wx.ID_NO:
                return () 
            res = ConvertFile(orig_file, new_file, tocrypted, True)
            if res:
                rel_path = relpath(orig_file, ntsdata)
                del self.hofh[rel_path]
                self.active_id = ()
                self.tree.SetFocus()
                self.ReloadData()


    def OnMove(self):
        id = self.leaf_selected
        file = self.getFile("Move note to", False)
        if file:
            item = self.tree.id2note[id]
            if item[2]:
                tag_str = " (%s)" % ", ".join(item[2])
            else:
                tag_str = ""
            lines = ["\n", "+ %s%s\n" % (item[0], tag_str)]
            for line in item[1]:
                lines.append("%s\n" % line)
            added = noteAdd(file, lines)
            deleted = 0
            if added:
                res = noteDelete(self.leaf_selected)
                if res == 2:
                    del self.hofh[self.leaf_selected[0]]
                if res:
                    self.active_id = ()
                    self.tree.SetFocus()
            if res or added:
                self.ReloadData()

    def OnOpen(self):
        file = None
        temp = None
        if self.node_selected: 
            dir = self.node_selected
            dir = full_path(dir)
            try:
                OpenWithDefault(dir)
            except:
                print "Error: could not open '%s'" % dir
        elif self.leaf_selected:
            file, beg, end = self.leaf_selected
            file = full_path(file)
        if file:
            backup(file)
            pathname, ext = os.path.splitext(file)
            if ext == ntsenc:  # encoded, need a plain text copy
                temp = "%s%s" % (pathname, ntstxt)
                ConvertFile(file, temp, False, True) # removes orig
                command = editcmd % {'e': editor, 'n': beg, 'f': temp}
                os.system(command)
                ConvertFile(temp, file, True, True) # removes temp
            else: # plain text
                command = editcmd % {'e': editor, 'n': beg, 'f': file}
                os.system(command)
            self.ReloadData()

    def ContentLines(self):
        # get rid of the trailing new lines
        content = self.display.GetValue()
        lines = content.split('\n')
        while not lines[-1].rstrip('\n'):
            lines.pop()
        # and put one back
        lines.append('\n')
        return(["%s" % x.rstrip('\n') for x in lines])

    def OnHelp(self, event):
        self.CheckMarkup()
        vars = {'version': version, 'copyright' : copyright, 'ntsinfo' : ntsinfo(), 'sysinfo' : sysinfo(), 'markup' : self.markup, 'ntstxt' : ntstxt, 'ntsenc' : ntsenc, 'ntsexport' : os.path.join(ntsexport, 'export.rst'), 'ntsrc' : ntsrc, 'ntsdata' : ntsdata, 'grandchild' :  os.path.join(ntsdata,'parent', 'child', 'grandchild.txt')}
        dlg = NTShtml(self, size=(600,340), page = help % vars )
        dlg.Show(True)

    def OnQuit(self, evnt=None):
        self.tbicon.Destroy()
        self.Destroy()

class MyApp(wx.App):

    def OnInit(self):
        frame = MyFrame(None, -1, 'nts')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def main():
    app = MyApp(0)
    app.MainLoop()

if __name__ == '__main__':
    main()