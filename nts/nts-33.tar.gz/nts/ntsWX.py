#!/usr/bin/env python

import wx
from nts.ntsData import *
from nts.ntsAbout import About
from nts.ntsHTML import NTShtml

from pkg_resources import resource_filename

options = get_opts()
filters = get_filters(options)

ID_BUTTON=100
ID_SPLITTER=300

try:
    from docutils import __version__ as docutils_version
    from docutils.core import publish_string
    has_docutils = True
except:
    docutils_version = 'none'
    has_docutils = False
    
def sysinfo():
    from platform import python_version as pv
    wxv = "%s.%s.%s" % (wx.MAJOR_VERSION, 
                wx.MINOR_VERSION, wx.RELEASE_VERSION)
    sysinfo = "platform: %s; python %s; wx(Python) %s; docutils %s" % (sys.platform, pv(), wxv, docutils_version)
    return(sysinfo)


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


help = """\
        <title>nts: note taking simplified</title>
<center>
nts version %s. Copyright %s Daniel A Graham. All rights reserved.
<br>
%s
<br>
%s
</center>
<pre>
Shortcuts:
    F1:               show this help information.
    F2:               clear option panel settings.
    F3:               apply option panel settings.
    F4:               show 'about' information for nts.
    F5:               if a note or leaf (notes file) is selected, open the
                      file using the external editor. Otherwise, open the node
                      (directory) using the system default application,
                      usually the file manager.
    Ctrl F:           move focus to the option panel f (FIND) field.
    Ctrl H:           display notes as HTML with an option to print. Select
                      notes to be displayed from a list with defaults
                      corresponding to the current selection. Requires
                      the python package docutils. See 'Restructured text'
                      below for more information.
    Ctrl M:           move the selected note it to an existing file to be
                      selected from a file dialog.
    Shift Ctrl M:     move the selected note to a new file to be selected
                      from a file dialog.
    Ctrl N:           create a new note.
    Ctrl O:           cycle the option panel o (OUTLINEBY) setting between
                      p)aths and t)ags.
    Ctrl P:           move focus to the option panel p (PATH) field.
    Ctrl Q:           quit.
    Ctrl R:           reload data files.
    Ctrl S:           save changes to a modified note. If editing an existing
                      note, replace it with the modified version. If creating
                      a new note, append it to an existing file to be chosen
                      from a list of existing files.
    Shift Ctrl S:     save changes to a modified note to a new file to be
                      selected from a file dialog.
    Ctrl T:           move focus to the option panel t (TAG) field.
    Ctrl U:           unselect all items.
    Ctrl X:           export notes. Select notes to be exported
                      from a list with defaults corresponding to the
                      current selection. Selected notes will be
                      exported as a restructured text file to
                          %s
                      (specified in %s).

    Left arrow:       collapse any children and then move to the parent.
    Ctrl left arrow:  move to parent and then collapse all children.
    Right arrow:      expand any children and then move down in the outline.
    Ctrl right arrow: expand entire branch and then move down in the outline.
    Up/Down arrows:   move up or down in outline without expanding or
                      collapsing any items.

    Double click:     with a note selected, open the note for editing.
    Return:           in the option panel PATH, TAG or FIND fields, apply
                      option panel settings. In the outline panel with a note
                      selected, open the note for editing.
    Tab:              cycle focus between the outline and display panels.
    Escape:           cancel editing a note. Warn if the note has been
                      modified.
    Delete:           delete the selected note.

Option panel settings:
   o OUTLINEBY  An element from [p, t] where:
                p: outline by path
                t: outline by tag
                Default: p.
   p PATH       Regular expression. Include items with paths matching PATH
                (ignoring case). Prepend an exclamation mark, i.e., use !PATH
                rather than PATH, to include items which do NOT have contexts
                matching PATH.
   t TAG        Regular expression. Include items with tags matching TAG
                (ignoring case). Prepend an exclamation mark, i.e., use !TAG
                rather than TAG, to include items which do NOT have tags
                matching TAG.
   f FIND       Regular expression. Include items containing FIND (ignoring
                case) in the note description or note text. Prepend an
                exclamation mark, i.e., use !FIND rather than FIND, to include
                notes which do NOT have descriptions or note texts matching
                FIND.

Making changes:
    To edit an existing note, either double-click on the note or select the
    note and then press Return. Make your changes to the note in the display
    panel and then press Ctrl-S when you are finished to replace the original
    note with your modified version.

    To create a new note, press Ctrl-N and then create your note in the
    display panel. When you are finished, either press Ctrl-S to save the note
    to an existing notes file or press Shift and Ctrl-S to save it to a new
    file.

    To delete a note, select the note and then press Delete. You will be
    prompted to confirm the deletion.

    To move a note, select the note and then press Ctrl-M. You will be
    prompted to select an existing notes file. The note will then be appended
    to the new file and deleted from the existing file.

    When making any of the changes listed above, nts will first make a backup
    of the existing file and add a log entry describing the changes. Backup
    files are rotated using the num_baks setting from your nts rc file.

    You can also make changes to notes files using the editor you specified in
    your ~/.nts/rc file. Press F5 with a note selected and the file will be
    opened in your editor with the cursor on the relevant line.

    Please use your favorite file manager to reorganize your nts date
    directory structure. If you press F5 on a node with any children, your
    system default application will be called with the relevant path. Normally
    this will open your file manager at the relevent directory.

Notes file format:
    Notes files must have the extension '.txt' and must be located in or
    below:
        %s
    (specified in %s).

    The file name without the extension will appear as the outline parent for
    all included notes. E.g., suppose your **only** notes file:

        %s

    has the contents:

        ----------- begin note file ----------------------
        + note a (tag 1, tag 2)
        the body of my first note

        + note b (tag 2, tag 3)
        the body of my second note
        ----------- end note file ------------------------

    Then when outlining by paths you would see

        parent
            child
                grandchild
                    note a
                    note b

    and when outlining by tags you would see

        tag 1
            note a
        tag 2
            note a
            note b
        tag 3
            note b

    Each notes file can contain one or more notes using the following format
    for each:

        + note title (optional tags)
        one or more lines containing the body of the note
        with all white space preserved.

    In the note title, the '+' must be in the first column. If given, tags
    must be comma separated and inclosed in parentheses. White space between
    notes is ignored. The note body continues until another note line or the
    end of the file is reached.

Restructured text:
    Standard restructured text (rst) markup can be used in the body of a note.
    E.g., *emphasis* and **bold faced**. See

          http://docutils.sourceforge.net/docs/user/rst/quickref.html

    for details. This markup will be preserved when exporting. Additionally,
    note descriptions will be treated as sections and a title added. Exporting
    the two notes from the file above would, for example, write the following:

        ----------- begin export file -------------------
        nts
        ===

        note a
        ------

        the body of my first note

        note b
        ------

        the body of my second note
        ----------- end export file ---------------------

    to 'export.rst'. Using the standard tools that come with python's docutils
    module, this rst file can be easily converted to a number of formats
    including HTML, Latex and OpenOffice ODF.

    If docutils is installed on your system, you will have the option (bound
    to Ctrl-H) of displaying selected notes as html with an option to print.
</pre>
""" % (version, copyright, ntsinfo(), sysinfo(), os.path.join(ntsexport, 'export.rst'), ntsrc, ntsdata, ntsrc, os.path.join(ntsdata,'parent', 'child', 'grandchild.txt'))


class MyTree(wx.TreeCtrl):
    def __init__(self, parent, id, position, size, style):
        wx.TreeCtrl.__init__(self, parent, id, position, size, style)
        # lofl item: (description, content, tags, id, path) 
        self.displayed = []
        self.MakeTree(options, filters)
            
    def MakeTree(self, options, filters):
        self.DeleteAllItems()
        root = self.AddRoot('root')
        self.root = root
        self.id2item = {}
        lofl = make_tree(options, filters)
        #lofl: note['description'], note['text'], note['tags'], note['id'], path        
        # self.details = {}
        paths = []
        parentof = {}
        self.id2note = {}
        self.displayed = []
        for note in lofl:
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
                        parentof[part[-1]] = self.AppendItem(parentof[part[-2]], part[-1])
                    self.SetPyData(parentof[part[-1]], 
                        (note[0], '', '', (), full_node))
            description = "%s" % note[0]
            parentof[description] = self.AppendItem(parentof[part[-1]], description)
            self.id2item[note[3]] = parentof[description]
            text = "%s" % ("\n".join(note[1]))
            if note[2]:
                tag_str = "(%s)" % ', '.join(note[2])
            else:
                tag_str = ""
            id = note[3]
            content = (description, text, tag_str, id, path)
            self.SetPyData(parentof[description], content)
        num = len(self.id2item.keys())
        if len(lofl) == 1:
            self.num_notes = "%s note" % num
        else:
            self.num_notes = "%s notes" % num
        self.SetPyData(root, ('', '', '', (), ""))

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title,
                          wx.DefaultPosition, wx.Size(760, 400))

        if notepad_type == 'ico':
            self.SetIcon(wx.Icon(nts_notepad, wx.BITMAP_TYPE_ICO))
            self.tbicon = MyTaskBarIcon(self)
        elif notepad_type == 'png':
            self.SetIcon(wx.Icon(nts_notepad, wx.BITMAP_TYPE_PNG))
            self.tbicon = MyTaskBarIcon(self)
        self.Bind(wx.EVT_ICONIZE, self.OnIconify)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        # outline tree
        tfont = wx.Font(font_size, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        # display panel
        dfont = wx.Font(font_size, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.dfont = dfont
        # labels in the option panel
        lfont = wx.Font(font_size - 1, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        # buttons in the option panel
        bfont = wx.Font(font_size - 1, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        # entry fields in the option panel
        efont = wx.Font(font_size, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        # monospaced font for the help display
        mfont = wx.Font(font_size, wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.mfont = mfont
        self.splitter = wx.SplitterWindow(self, ID_SPLITTER, style = wx.SP_LIVE_UPDATE)
        leftPanel = wx.Panel(self.splitter, -1, style=wx.LC_LIST)
        leftBox = wx.BoxSizer(wx.VERTICAL)
        self.hofh = load_data()
        self.tree = MyTree(leftPanel, -1, wx.DefaultPosition, wx.DefaultSize,
                           wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS)
        self.tree.SetBackgroundColour("white")
        self.tree.Bind(wx.EVT_CHAR, self.OnChar)
        leftBox.Add(self.tree, 1, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, 4)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnSelActivated)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGING, self.OnSelChanging)
        self.tree.SetFont(tfont)
        leftPanel.SetSizer(leftBox)
        rightPanel = wx.Panel(self.splitter, -1, size = wx.DefaultSize,
            style=wx.SP_3D)
        rightBox = wx.BoxSizer(wx.VERTICAL)
        self.display = wx.TextCtrl(rightPanel, -1, size = wx.DefaultSize,
            style=wx.TE_MULTILINE| wx.BORDER_NONE | wx.TE_READONLY)
        self.display.Bind(wx.EVT_TEXT, self.OnText)
        self.display.Bind(wx.EVT_CHAR, self.OnDisplayChar)
        self.display.SetFont(dfont)
        self.display.SetBackgroundColour("white")
        rightBox.Add(self.display, 1, wx.EXPAND | wx.ALL, 4)
        rightPanel.SetSizer(rightBox)
        self.splitter.SplitVertically(leftPanel, rightPanel, 240)
        
        self.optionbar = wx.BoxSizer(wx.HORIZONTAL)
        button1 = wx.StaticText(self, ID_BUTTON + 1, "^O ")
        button1.SetFont(lfont)
        self.gb = wx.Choice(self, ID_BUTTON + 2, choices = ['p', 't'])
        self.gb.SetFont(bfont)
        button3 = wx.StaticText(self, ID_BUTTON + 3, "^P ")
        button3.SetFont(lfont)
        self.pf = wx.TextCtrl(self, ID_BUTTON + 4, "")
        self.pf.SetFont(efont)
        self.pf.Bind(wx.EVT_CHAR, self.OnOptChar)
        button5 = wx.StaticText(self, ID_BUTTON + 5, "^T ")
        button5.SetFont(lfont)
        self.tf = wx.TextCtrl(self, ID_BUTTON + 6, "")
        self.tf.SetFont(efont)
        self.tf.Bind(wx.EVT_CHAR, self.OnOptChar)
        button7 = wx.StaticText(self, ID_BUTTON + 7, "^F ")
        button7.SetFont(lfont)
        self.ff = wx.TextCtrl(self, ID_BUTTON +8, "")
        self.ff.SetFont(efont)
        self.ff.Bind(wx.EVT_CHAR, self.OnOptChar)
        # apply
        self.eb = wx.Button(self, ID_BUTTON +9, "F3: APPLY", style = wx.BU_EXACTFIT)
        self.eb.SetFont(bfont)
        self.Bind(wx.EVT_BUTTON, self.OnEnter, self.eb)
        self.cb = wx.Button(self, ID_BUTTON +10, "F2: CLEAR", style = wx.BU_EXACTFIT)
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
        self.file_selected = False
        self.node_selected = False
        self.selected_id = ()
        self.active_id = ()
        nts_count = self.CountChildren(self.tree.root)
        self.SetTitle("nts (%s)" % self.tree.num_notes)
        self.content = nts_count
        self.display.ChangeValue(nts_count)
        self.Centre()
        
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
        self.file_selected = ()
        self.node_selected = ()
        content = self.tree.GetPyData(item)
        if content[1]:
            # print content[3]
            self.leaf_selected = content[3]
            self.selected_id = content[3]
            if content[2]:
                tag_str = " %s" % content[2]
            else:
                tag_str = ""
            detail_str = "\n--- %s%s" % (':'.join(map(str, content[3])), tag_str)
            self.display.ChangeValue("%s\n%s" % (content[1], detail_str))
            # self.content = self.display.GetValue()
        else:
            # print content[4]
            self.selected_id = (content[4], 0, 0)
            nts_count = self.CountChildren(item)
            self.display.ChangeValue(nts_count)
            children = self.tree.GetChildrenCount(item, recursively=False)
            other = self.tree.GetChildrenCount(item)
            descendants = other - children
            if descendants == 0:
                self.file_selected = content[4]
            else:
                self.node_selected = content[4]
        self.content = self.display.GetValue()

    def OnSelActivated(self, event):
        item =  event.GetItem()
        self.selected = item
        # Display the selected item text in the text widget
        item = self.tree.GetPyData(item)
        if item[1]:
            if item[2]:
                tag_str = " %s" % item[2]
            else:
                tag_str = ""
            self.display.ChangeValue("+ %s%s\n%s" % (item[0], tag_str, item[1]))
            self.active_id = item[3]
            self.selected_id = item[3]
            self.treeFocused = False
            self.display.SetEditable(True)
            self.display.SetFocus()
            self.display.SetInsertionPoint(self.display.XYToPosition(2,0))
            # self.display.SetBackgroundColour('wheat')
            
    def DeActivate(self):
        if self.display.IsEditable():
            if self.modified:
                dlg = wx.MessageDialog(None, 'abandon changes?',  'nts',
                    wx.YES_NO | wx.YES_DEFAULT )
                if dlg.ShowModal() == wx.ID_NO:
                    return ()                    
                self.modified = False
                self.display.SetBackgroundColour('white')
            self.display.SetEditable(False)
        self.display.ChangeValue(self.content)
        self.treeFocused = True
        self.active_id = ()
        self.tree.SetFocus()
            
    def OnSelChanging(self, event):
        item =  event.GetItem()
        if self.modified:
            event.Veto()
            dlg = wx.MessageDialog(None, 'abandon changes?',  'nts',
                    wx.YES_NO | wx.YES_DEFAULT )
            if dlg.ShowModal() == wx.ID_NO:
                self.display.SetFocus()
                self.treeFocused = False
                return ()
            self.modified = False
        self.display.SetEditable(False)
        self.treeFocused = True
        self.active_id = ()
        # self.selected_id = ()
        self.tree.SetFocus()
        self.display.ChangeValue(self.content)
        self.display.SetBackgroundColour('white')
        event.Skip()
                        
    def ToggleFocus(self):
        if self.treeFocused:
            self.display.SetFocus()
            self.treeFocused = False
        else:
            self.DeActivate()
            
    def OnText(self, event):
        self.modified = True
        self.display.SetBackgroundColour('medium goldenrod')        
        # self.display.SetBackgroundColour('light grey')        

    def OnChar(self, event):
        keycode = event.GetKeyCode()
        shift = event.ShiftDown()
        control = event.ControlDown()
        # print "on char: keycode/shift/control", keycode, shift, control
        if keycode == 27:               # ESC
            self.DeActivate()
        elif keycode == wx.WXK_LEFT:
            if (control and self.selected and self.tree.IsSelected(self.selected)):
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
        elif keycode == 8:           # Ctrl-H html
            ids = self.getIDs()
            if ids:
                self.OnHTML(ids)
        elif control and keycode == 13:     # Ctrl-M move note
            if shift:
                # save to a new file, append = False
                self.OnMove(False)
            else:
                # append to an existing file, append = True
                self.OnMove(True)
        elif keycode == 14:           # Ctrl-N add new note
            self.OnAdd()
        elif keycode == 24:           # Ctrl-X export
            ids = self.getIDs()
            if ids:
                str = self.OnExport(ids)
        elif keycode == 17:           # Ctrl-Q quit
            self.OnQuit()
        elif keycode == 18:           # Ctrl-R reload
            self.ReloadData()
        elif keycode == 21:           # Ctrl-U unselect all
            self.UnselectAll()
        elif keycode in [wx.WXK_BACK, wx.WXK_DELETE] and self.leaf_selected:
            self.OnDelete()
        elif keycode == wx.WXK_TAB:
            self.ToggleFocus()
        elif keycode == wx.WXK_F1: 
            self.OnHelp(event)
        elif keycode == wx.WXK_F2: 
            self.OnClear(event)
        elif keycode == wx.WXK_F3: 
            self.OnEnter(event)
        elif keycode == wx.WXK_F4: 
            self.OnAbout(event)
        elif keycode == wx.WXK_F5: 
            self.OnOpen()
        elif keycode in [15, 16, 20, 6]: # ^O, ^P, ^T, ^F 71, 80, 84, 70
            self.setfocus(event, keycode+64)
        else:
            event.Skip()

    def OnDisplayChar(self, event):
        keycode = event.GetKeyCode()
        shift = event.ShiftDown()
        control = event.ControlDown()
        if keycode == 27:               # ESC
            self.DeActivate()
        elif keycode == 17:           # Ctrl-Q quit
            self.OnQuit()
        elif keycode == 19:           # Ctrl-S quit
            if shift:
                # save to a new file, append = False
                self.OnSave(event, False)
            else:
                # append to an existing file, append = True
                self.OnSave(event, True)
        elif keycode == wx.WXK_TAB:
            if not self.modified:
                self.ToggleFocus()
        elif keycode == wx.WXK_F1: 
            self.OnHelp(event)
        elif keycode == wx.WXK_F4: 
            self.OnAbout(event)
        else:
            event.Skip()

    def OnOptChar(self, event):
        keycode = event.GetKeyCode()
        shift = event.ShiftDown()
        control = event.ControlDown()
        if keycode in [15, 16, 20, 6]: # ^O, ^P, ^T, ^S 71, 80, 84, 83
            self.setfocus(event, keycode+64)
        elif keycode == 13:    # Ctrl-C clear
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
            self.OnClear(event)
        elif keycode == wx.WXK_F3: 
            self.OnEnter(event)
        elif keycode == wx.WXK_F4: 
            self.OnAbout(event)
        else:
            event.Skip()

    def OnAbout(self, event):
        # show the about page
        About(self)

    def OnEnter(self, evt):
        local_options = options
        local_options['outlineby']  = ['p', 't'][self.gb.GetCurrentSelection()]
        local_options['path']  = self.pf.GetValue()
        local_options['tag']  = self.tf.GetValue()
        local_options['find']  = self.ff.GetValue()
        local_filters = get_filters(local_options)
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


    def UnselectAll(self):
        nts_count = self.CountChildren(self.tree.root)
        self.display.ChangeValue(nts_count)
        self.treeFocused = True
        self.active_id = ()
        self.selected_id = ()
        self.leaf_selected = False
        self.file_selected = False
        self.node_selected = False
        self.tree.SetFocus()
        self.tree.UnselectAll()
            
    def OnClear(self, evt):
        gb = self.gb.SetSelection(0)
        self.pf.SetValue('')
        self.tf.SetValue('')
        self.ff.SetValue('')
        # self.OnEnter(evt)

    def setfocus(self, event, key):
        if key == 79:
            # toggle outlineby
            old_gb = self.gb.GetCurrentSelection()
            new_gb = (old_gb + 1) % 2
            self.gb.SetSelection(new_gb)
            self.OnEnter(event)
        elif key == 80:
            self.pf.SetFocus()
        elif key == 84:
            self.tf.SetFocus()
        elif key == 70:
            self.ff.SetFocus()
        else:
            pass
        
    def OnSave(self, event, append=True):
        if not self.display.IsEditable() or not self.modified:
            return()
        id = self.active_id
        lines = self.ContentLines()
        if id:
            # this is an existing note
            res = noteReplace(id, lines)
        else:
            # this is a new note
            file = self.getFile(append)
            if file:
                res = noteAdd(file, lines)
            else:
                res = False
        if res:
            self.display.SetEditable(False)
            self.modified = False
            self.display.SetBackgroundColour('white')
            self.treeFocused = True
            self.active_id = ()
            self.ReloadData()
            self.tree.SetFocus()

    def getSelection(self, prompt, choices, dflt=None):
        dlg = wx.SingleChoiceDialog(self, prompt, 'nts',
                choices, wx.CHOICEDLG_STYLE)
        if dflt:
            dlg.SetSelection(dflt)
        if dlg.ShowModal() == wx.ID_OK:
            return dlg.GetStringSelection()
        else:
            return ""

    def getFile(self, append = True, prompt = "Append note to"):
        file = None
        if append:
            flst = [ x[0] for x in get_filelist() ]
            flst.sort()
            file = self.getSelection(prompt, flst)
        else:         
            filedlg = wx.FileDialog(
                self, message = "Append note",
                defaultDir = ntsdata,
                defaultFile="",
                wildcard="etm project file (*.txt)|*.txt",
                style=wx.SAVE
            )
            if filedlg.ShowModal() == wx.ID_OK:
                file = filedlg.GetPath()
                name, ext = os.path.splitext(file)
                file = "%s.txt" % name
        if file:
            return(os.path.join(ntsdata, file))
        else:
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
                # add one because inserting ALL makes the choices index 1 greater than the ids index
                selected.append(ids.index(self.selected_id)+1)
            else:
                # a note is not selected so get the path to the node and append all descendent notes  
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
            
    def OnExport(self, ids):
        '''Export selected notes in rst format'''
        out = ['nts', '===', '']
        if ids:
            for id in ids:
                note = self.tree.id2note[id]
                out.append(note[0])
                out.append('-'*len(note[0]))
                out.append('')
                for line in note[1]:
                    out.append("%s" % line)
                out.append('')
            export_file = os.path.join(ntsexport, 'export.rst')
            fo = codecs.open(export_file, 'w', encoding, 'replace')
            fo.writelines(["%s\n" % x for x in out])
            fo.close()

    def OnHTML(self, ids):
        '''Show selected notes in HTML window'''
        if has_docutils and ids:
            out = []
            for id in ids:
                note = self.tree.id2note[id]
                out.append(str(note[0]))
                out.append('-'*len(note[0]))
                out.append('')
                for line in note[1]:
                    out.append("%s" % line)
                out.append('')
            rst = "\n".join(out)
            if stylesheet:
                customcss = {'embed_stylesheet':False, 
                'stylesheet_path':stylesheet}
                html = publish_string(source=rst, writer_name='html',
                    settings_overrides=customcss)
            else:
                html = publish_string(source=rst, writer_name='html')
            dlg = NTShtml(self, size=(600,340), page = html)
            dlg.Show(True)
            
    def OnAdd(self):
        self.display.ChangeValue("+ ")
        self.active_id = ()
        self.treeFocused = False
        self.display.SetEditable(True)
        self.display.SetFocus()
        self.display.SetInsertionPoint(self.display.XYToPosition(2,0))

    def OnDelete(self):
        dlg = wx.MessageDialog(None, 'delete note?',  'nts',
            wx.YES_NO | wx.YES_DEFAULT )
        if dlg.ShowModal() == wx.ID_NO:
                return ()
        res = noteDelete(self.leaf_selected)
        if res == 2:
            del self.hofh[self.leaf_selected[0]]
        if res:
            self.active_id = ()
            self.tree.SetFocus()
            self.ReloadData()
        return(True)
            
    def OnMove(self, append = True):
        id = self.leaf_selected
        item = self.tree.id2note[id]
        if item[2]:
            tag_str = " (%s)" % ", ".join(item[2])
        else:
            tag_str = ""
        lines = ["\n", "+ %s%s\n" % (item[0], tag_str)]
        for line in item[1]:
            lines.append("%s\n" % line)
        file = self.getFile(append, "Move note to")
        if file:
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
        if self.leaf_selected:
            file, beg, end = self.leaf_selected
            file = full_path(file)
            command = editcmd % {'e': editor, 'n': beg, 'f': file}
            backup(file)
            os.system(command)
            self.ReloadData()
        elif self.file_selected:
            file = self.file_selected
            file = "%s.txt" % full_path(file)
            command = editcmd % {'e': editor, 'n': 1, 'f': file}
            backup(file)
            os.system(command)
            self.ReloadData()
        elif self.node_selected: 
            dir = self.node_selected
            dir = full_path(dir)
            try:
                OpenWithDefault(dir)
            except:
                print "Error: could not open '%s'" % dir
        else:
            try:
                OpenWithDefault(ntsdata)
            except:
                print "Error: could not open '%s'" % dir
        
    def ContentLines(self):
        # get rid of the trailing new lines
        content = self.display.GetValue()
        lines = content.split('\n')
        while not lines[-1].rstrip():
            lines.pop()
        # and put one back
        lines.append('\n')
        return(["%s\n" % x.rstrip() for x in lines])

    def OnHelp(self, event):
        dlg = NTShtml(self, size=(600,340), page = help)
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