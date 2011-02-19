#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         sylli-gui.py
# Purpose:      A wx UI for sylli
#
# Author:       Luca Iacoponi
#
# Created:      June 2010
# Licence:      Apache Licence
#----------------------------------------------------------------------------
# to fix:
# * Middle sizer should wx.EXPAND

# to do:
# The open sonority problem

""" UI for Sylli """

import os
import subprocess
import shutil
import sys
import sylli
import filepath
import demo
try:
    import wx
    import wx.html
    from wx.lib.wordwrap import wordwrap
except ImportError:
    print "wx module not found. Please, download wxPython at www.wxpython.org."

# Syllabification class
syl = sylli.SylModule()
# Working sonority
SON = syl.sonority_file

def get_ico(ico):
    """ Return one of the icon in images/ as an ico object """
    ico_path = os.path.join(filepath.get_path('images'), ico + '.ico')
    icon = wx.Icon(ico_path, wx.BITMAP_TYPE_ICO)
    return icon

def get_bitmap(bitmap):
    """ Return one of the png in images/ as a bitmap object """
    bit_path = os.path.join(filepath.get_path('images'), bitmap + '.png')
    bit = wx.Bitmap(bit_path)
    return bit

def writefile(filename, content):
    """ Write in file $filename a content $content """
    sfile = filename[:-3] + "sy2"
    syl_file = open(sfile, 'w')
    #! error handling
    for char in content:
        syl_file.write(char)
    syl_file.close()
    print "Output saved to " + sfile

def syllabify_list(file_list, write=0):
    """ Syllabify files in the list """
    for ifile in file_list:
        content = ''.join(sylli.filel(ifile))
        if not content:
            self.parent.err_dial("Sorry, path does'nt exist:\n" + ifile)
            continue
        print '\n' + ifile
        syllabified = syl.syllabify(content)

        # Write to a file
        if write:
            writefile(ifile, syllabified)
        # Print
        else:
            print syllabified

def savedial(obj, wildcard, defdir, msg):
    """ Create a save file dialog. """
    path = None
    dlg = wx.FileDialog(
        obj, message=msg, defaultDir=defdir,
        defaultFile="", wildcard=wildcard, style=wx.SAVE)
    # Show the dialog and retrieve the user response. If it is the OK response,
    # process the data.
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
        # fp = file(path, 'w') # Create file anew
    dlg.Destroy()
    return path

def filedial(obj, wildcard, defdir):
    """ Create an open file dialog. """
    paths = None
    # Create the dialog.
    dlg = wx.FileDialog(obj, message="Choose a file",
        defaultDir=defdir, defaultFile="", wildcard=wildcard,
        style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
    if dlg.ShowModal() == wx.ID_OK:
        # This returns a Python list of files that were selected.
        paths = dlg.GetPaths()
    dlg.Destroy()
    return paths


class RedirectText:
    """ Redirect the stdout/stderr output to a wx text control. """
    def __init__(self, aWxTextCtrl):
        self.out = aWxTextCtrl

    def write(self, string):
        self.out.WriteText(string)


class MyFileDropTarget(wx.FileDropTarget):
    """ Create a drop target.
    It adds to a form the filenames of the files dropped in. """
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, alpha, beta, filenames):
        for cfile in filenames:
            self.window.WriteText(cfile + ';')


class NoteTab(wx.Panel):
    """ Create a note tab panel """
    def __init__(self, parent, tab_type):
        wx.Panel.__init__(self, parent)
        self.file = 0
        self.SetBackgroundColour(wx.WHITE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # files or
        if tab_type != "String":
            # button
            browse_button = wx.Button(self, -1, "Browse...")
            if tab_type == 'Files':
                self.Bind(wx.EVT_BUTTON, self.OnFileButton, browse_button)
            else:
                self.Bind(wx.EVT_BUTTON, self.OnDirButton, browse_button)
            # drag and drop text field
            self.file_field = wx.TextCtrl(self, -1, "", size = (210, -1))
            dropt = MyFileDropTarget(self.file_field)
            self.file_field.SetDropTarget(dropt)
            # checkbox
            create_syll = wx.CheckBox(self, -1, " create a .syl")
            create_syll.SetToolTip(wx.ToolTip("Create .syl "
            "file containing syllabified output"))
            self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox, create_syll)
            # sizer for button and text field
            file_sizer = wx.BoxSizer(wx.HORIZONTAL)
            file_sizer.Add(browse_button, 0, wx.ALL, 5)
            file_sizer.Add(self.file_field, 1, wx.ALL, 5)
            # add to main sizer
            sizer.Add(file_sizer, 5, wx.LEFT, 5)
            sizer.Add(create_syll, 0, wx.ALL, 5)
        # string selected, add text field only
        else:
            # text fields
            str_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.strTxt = wx.TextCtrl(self, -1, "", size = (300, -1),
                                 style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
            str_sizer.Add(self.strTxt, 1, wx.ALL, 5)
            self.strTxt.GetValue()
            # add to main sizer
            sizer.Add(str_sizer, wx.LEFT | wx.ALL,)
        self.SetSizer(sizer)

    def EvtCheckBox(self, evt):
        self.file = evt.IsChecked()

    def OnFileButton(self, evt):
        """ Show a dialog to choose the file to syllabify """
        wildcard = "All files (*.*)|*.*|" \
                   "CLIPS std (*.std)|*.std|" \
                   "CLIPS phn (*.phn)|*.phn|" \
                   "CLIPS wrd (*.wrd)|*.wrd|" \
                   "Text files (*.txt)|*.txt"

        self.file_field.Clear()
        paths = filedial(self, wildcard, os.getcwd())
        if paths:
            for path in paths:
                self.file_field.AppendText('%s;' % path)

    def OnDirButton(self, evt):
        """ Show a dialog to choose the directory to syllabify """
        # In this case we include a "New directory" button.
        dlg = wx.DirDialog(self, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.file_field.Clear()
            self.file_field.WriteText('%s' % dlg.GetPath())
        dlg.Destroy()


class MyHtmlWindow(wx.html.HtmlWindow):
    """ Create an html Window for displaying the documentation """
    def __init__(self, parent):
        wx.html.HtmlWindow.__init__(self, parent, -1,
                                    style=wx.NO_FULL_REPAINT_ON_RESIZE)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()


class ContentFrame(wx.Frame):
    """ Frame for the Content window """
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, title='Sylli Contents',
                          size = (550, 600), style = wx.DEFAULT_FRAME_STYLE)
        self.SetIcon(get_ico('cont'))
        html_path = os.path.join(filepath.get_path('htmldoc'), 'documentation.htm')
        self.html = MyHtmlWindow(self)
        self.html.LoadPage(html_path)


class MyPanel(wx.Panel):
    """ Main panel of the program, it contains all the widgets. """
    def __init__(self, parent, panel_id):
        """ Initialise the main panel. """
        wx.Panel.__init__(self, parent, panel_id)
        # default tab and radio
        self.parent = parent
        self.tab = 0
        # BoxSizer to manage all other sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        # Static box and sizers
        self.upper_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.middle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lowerBox = wx.StaticBox(self, -1, "Controls")
        self.lower_sizer = wx.StaticBoxSizer(lowerBox, wx.HORIZONTAL)
        # declare parenthood of the sizers
        main_sizer.Add(self.upper_sizer, 0, wx.ALL, 10)
        main_sizer.Add(self.middle_sizer, 0, wx.ALL, 10)
        main_sizer.Add(self.lower_sizer, 0,  wx.ALL, 10)
        # widgets - Radio - Output
        self.output_radio = wx.RadioBox(
                self, -1, "Output", wx.DefaultPosition, wx.DefaultSize,
                ['str', 'cvg', 'cvcv'], 3, wx.RA_SPECIFY_COLS)
        self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox2, self.output_radio)
        self.output_radio.SetToolTip(wx.ToolTip("str: show the segments;\n"
                                      "cvg: show the phonological class;\n"
                                      "cvcv: show Consonant Vowel structure"))
        # widget - Checkbox - Extra
        self.extra_checkb = wx.CheckBox(self, -1, "Extrasyllabicity")
        self.extra_checkb.SetToolTip(wx.ToolTip("Allow extrasyllibic segment."))
        self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox2, self.extra_checkb)
        # NB Panel
        self.nb =  wx.Notebook(self, -1)
        self.string_tab = NoteTab(self.nb, 'String')
        self.word_tab = NoteTab(self.nb, 'Files')
        self.dir_tab = NoteTab(self.nb, 'Directory')
        self.nb.AddPage(self.string_tab, "String")
        self.nb.AddPage(self.word_tab, "Files")
        self.nb.AddPage(self.dir_tab, "Directory")
        self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        # Buttons
        self.create_buttonbar(self)
        # Bind to sizers
        self.upper_sizer.Add(self.output_radio, 0, wx.RIGHT, 10)
        self.upper_sizer.Add(self.extra_checkb, 0, wx.LEFT|wx.ALIGN_CENTRE, 10)
        self.middle_sizer.Add(self.nb, 0, wx.EXPAND, 0)
        # set mainSizer as the frame sizer
        main_sizer.Fit(self)
        main_sizer.SetSizeHints(self)
        self.SetSizer(main_sizer)
        self.Layout()

    def button_data(self):
        """ Contains the data of the three buttons on the bottom """
        return (("Reload Son", self.OnReload, "(Re)load working sonority"),
                ("Syllabify!", self.OnSyll, "Syllabify input"),
                ("Demo", self.OnDemo, "Run a demo of current sonority"))

    def create_buttonbar(self, panel):
        """ Create the three buttons on the bottom of the panel """
        for label, handler, tooltip in self.button_data():
            button = self.build_button(panel, label, handler, tooltip)
            self.lower_sizer.Add(button, 0, wx.ALL, 10)

    def build_button(self, parent, label, handler, tooltip):
        """ Create a button. """
        button = wx.Button(parent, -1, label)
        self.Bind(wx.EVT_BUTTON, handler, button)
        button.SetToolTip(wx.ToolTip(tooltip))
        return button

    # event handlers
    def EvtCheckBox2(self, evt):
        syl.extra = evt.IsChecked()

    def EvtRadioBox2(self, evt):
        syl.output = self.output_radio.GetStringSelection()

    def OnPageChanged(self, evt):
        self.tab = evt.GetSelection()
        evt.Skip()

    def OnSyll(self, evt):
        # string
        if self.tab == 0:
            to_syll = self.string_tab.strTxt.GetValue()
            # each line is a different string to sillabify
            for string in to_syll.split('\n'):
                if string:
                    print syl.syllabify(string)

        # files
        elif self.tab == 1:
            # Get the file list
            file_list = self.word_tab.file_field.GetValue().split(';')
            # last is empty if list > 1
            if len(file_list) > 1:
                del file_list[-1]
            else:
                if file_list[0] == "":
                    return False
            # Write to a file
            if self.word_tab.file and self.tab == 1:
                syllabify_list(file_list, write=1)
            else:
                syllabify_list(file_list)

        # directory
        elif self.tab == 2:
            input_dir = self.dir_tab.file_field.GetValue()
            file_dict = sylli.dirl(input_dir)
            if not file_dict:
                self.parent.err_dial("Sorry, no valid in:\n" + input_dir)
            else:
                print '----------------------'
                # Write to a file
                if self.dir_tab.file and self.tab == 2:
                    syllabify_list(file_dict, write=1)
                else:
                    syllabify_list(file_dict)
                print str(len(file_dict)) + " file/s have been syllabified."

    def OnQuit(self, evt):
        """ Quit, destroy the frame """
        wx.GetApp().frame.Close()

    def OnDemo(self, evt):
        """ Run the demo module demo, showing syllabification examples. """
        print "\nDemo"
        print "sonority: " + syl.sonority_file
        print "extrasyllabicity: " + str(syl.extra)
        demo.demo(syl)

    def OnReload(self, evt):
        """ Set working sonority (which may have been edited or changed)
        as SylModule sonority, """
        self.parent.conf_update(SON)


class MyFrame(wx.Frame):
    """ Main frame. Includes the icon, menu bar, help bar, status bar
    and the two panels: one with the widgets, the other with the control
    for the sdout/stderr text. """
    def __init__(self, parent, title):
        # Top window can't be maximized
        wx.Frame.__init__(self, None, -1, title='Sylli', size=(350, -1),
                          style=wx.DEFAULT_FRAME_STYLE ^ (wx.MAXIMIZE_BOX))
        self.menubar = wx.MenuBar()
        self.SetIcon(get_ico('sylli'))
        self.create_menubar()
        self.create_helpbar()
        self.SetMenuBar(self.menubar)
        self.CreateStatusBar()
        self.Bind(wx.EVT_MENU_CLOSE, self.OnMenu)

        self.main_panel = MyPanel(self, -1)

        # Create the stdout text control
        right_panel = wx.Panel(self, -1)
        self.log = wx.TextCtrl(right_panel, -1, size=(400, 320),
                   style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL|wx.NO_BORDER)
        redir = RedirectText(self.log)
        sys.stdout = redir

        frame_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        left_sizer.Add(self.main_panel, 1, wx.ALL, 1)
        right_sizer.Add(right_panel, 1, wx.EXPAND)
        frame_sizer.Add(left_sizer, 0,  wx.EXPAND)
        frame_sizer.Add(right_sizer, 1, wx.EXPAND)

        frame_sizer.Fit(self)
        self.SetSizer(frame_sizer)
        self.Layout()
        self.ui_update()

    def menudata(self):
        """ Return data to be included in the menu bar.  """
        return (("&File",
                    ("&Quit\tAlt+F4", "Quit", self.OnQuit)),
                ("&Sonorities",
                    ("&New\tAlt+N", "New sonority", self.OnNewS),
                    ("&Edit\tAlt+E", "Edit sonority", self.OnEditS),
                    ("&Load\tAlt+L", "Load another sonority", self.OnLoadS),
                    ("&Reset", "Reset installation sonority", self.OnResetS)))

    def create_menubar(self):
        """ Get the data from menudata() and create the menu bar. """
        for menudata in self.menudata():
            label = menudata[0]
            items = menudata[1:]
            self.menubar.Append(self.create_menu(items), label)

    def create_menu(self, menudata):
        """ Create a menu of the menu bar.  """
        menu = wx.Menu()
        for label, status, handler in menudata:
            if not label:
                menu.AppendSeparator()
                continue
            item = menu.Append(-1, label, status)
            self.Bind(wx.EVT_MENU, handler, item)
        return menu

    def create_helpbar(self):
        """ Creates the help bar.  """
        # content
        help_menu = wx.Menu()
        item = wx.MenuItem(help_menu, -1, "C&ontents\tAlt+C", "Contents")
        item.SetBitmap(get_bitmap('content'))
        self.Bind(wx.EVT_MENU, self.OnContents, item)
        help_menu.AppendItem(item)
        # about
        item = wx.MenuItem(help_menu, -1, "A&bout\tAlt+A", "About")
        item.SetBitmap(get_bitmap('about'))
        self.Bind(wx.EVT_MENU, self.OnAbout, item)
        help_menu.AppendItem(item)
        # append to menu bar
        self.menubar.Append(help_menu, 'Help')

    def err_dial(self, msg):
        """ Show an error dialog. """
        dlg = wx.MessageDialog(self, msg, 'Sylli Error', wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def conf_update(self, new_son):
        """ Set a new sonority file as the one in use in UI and SylModule. """
        global SON
        # Update all variables
        SON = new_son
        syl.load_conf(new_son)
        print 'Sonority loaded: ' + new_son
        # Update the UI
        self.ui_update()
        self.SetStatusText("Son: " + syl.sonority_file)

    def ui_update(self):
        """ Update all widgets to reflect the SylModule attribute values. """
        self.SetStatusText("Son: " + syl.sonority_file)
        self.main_panel.extra_checkb.SetValue(syl.extra)
        if syl.output == 'str':
            output = 0
        elif syl.output == 'cvg':
            output = 1
        else:
            output = 2
        self.main_panel.output_radio.SetSelection(output)

    def OnMenu(self, evt):
        """ Update the status bar sonority """
        self.SetStatusText("Son: " + syl.sonority_file)

    def OnNewS(self, evt):
        """ Create a new sonority file,
        using  installation sonority as a template. """
        global SON
        new_sonfile = None
        new_sonfile = savedial(self, "Text files (*.txt)|*.txt",
        filepath.get_path('config_dir'), "Create new sonority.txt")
        if new_sonfile:
            # copy install sonority as a model
            try:
                shutil.copyfile(filepath.get_path('inst_sonority'), new_sonfile)
            except Exception, error:
                print 'Could not copy sonority.txt to '
                +  filepath.get_path('usr_sonority') + ': ' + str(error)
            # and open it
            try:
                os.startfile(new_sonfile)
            except AttributeError:
                subprocess.call(['open', new_sonfile])
            except Exception:
                print "Sorry, no default program was found when trying to open "
                new_sonfile + " edit the file using your favourite text editor."
                return(0)
            print new_sonfile, " created.\nRemember to load it when ready."
        SON = new_sonfile

    def OnEditS(self, evt):
        """ Edit the current working sonority file """
        if not os.path.exists(SON):
            self.err_dial('Sorry, file does not exist:' + SON)
            return False
        try:
            os.startfile(SON)
        except AttributeError:
            subprocess.call(['open', SON])
        except Exception:
            print "Sorry, no default program was found when trying to open "
            SON + " edit the file using your favourite text editor."
            return(0)
        print SON + " on edit.\nRemember to load it when ready!"

    def OnLoadS(self, evt):
        """ Load an alternative sonority file """
        global SON
        new_son = filedial(self, "Text files (*.txt)|*.txt",
                           filepath.get_path('config_dir'))[0]
        self.conf_update(new_son)
        SON = new_son

    def OnResetS(self, evt):
        """ Restore installation sonority.txt by copying it into user's home """
        dlg = wx.MessageDialog(self, "This operation will overwrite your "
                               "default sonority.txt with the installation "
                               "sonority!\n Continue?", \
                               "sonority.txt reset. Remember to load it!",
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
        if dlg.ShowModal() == wx.ID_YES:
            sylli.reset_son()
        dlg.Destroy()

    def OnQuit(self, evt):
        """ Quit, destroy the main frame """
        self.Destroy()

    def OnContents(self, evt):
        """ A wx frame showing the program documentation """
        contentwin = ContentFrame(self)
        contentwin.Show(True)

    def OnAbout(self, evt):
        """ A wx about box. """
        info = wx.AboutDialogInfo()
        info.Name = "Sylli"
        info.Version = sylli.VERSION
        info.Copyright = "(C) 2010 Iacoponi Luca"
        info.Description = wordwrap(
            "Divide phonematic sequences into syllables"
            " and provides other useful functions for syllable analysis",
            350, wx.ClientDC(self))
        info.WebSite = ("http://sylli.sourceforge.net", "Sylli home page")
        info.Developers = [ "Luca Iacoponi - jacoponi@gmail.com" ]
        license_text = sylli.version()
        info.License = wordwrap(license_text, 500, wx.ClientDC(self))
        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)


class MyApp(wx.App):
    """ Create the wxApp object which contains the main frame and show it. """
    def OnInit(self):
        """ Initialise the application """
        self.frame = MyFrame(None, "Sylli")
        self.frame.Fit()
        self.SetTopWindow(self.frame)
        self.frame.Show(True)
        return True

def main(debug=0):
    """ Run the application. Create a wx.App object and run MainLoop method. """
    redir = True
    # For debugging
    if debug:
        wx.Trap()
        print "wx.VERSION_STRING = %s (%s)" % (wx.VERSION_STRING,
        wx.USE_UNICODE and 'unicode' or 'ansi')
        print "pid:", os.getpid()
        redir = False
        raw_input("Press Enter...")
    app = MyApp(redirect=redir)
    app.MainLoop()

if __name__ == "__main__":
    main()
