description = """\
nts (note taking simplified) provides a simple format for using 
text files to store notes, a command line interface for viewing
notes in a variety of convenient ways and a wx(python)-based
GUI for creating and modifying notes as well as viewing them.
"""

# license = "GNU General Public License (GPL)"
license = """\
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of
the License, or (at your option) any later version. 
[ http://www.gnu.org/licenses/gpl.html ]

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTabILITY or FITNESS FOR A PARTICULAR PURPOSE. See
the GNU General Public License for more details.
"""


help = """\
        <title>nts: note taking simplified</title>
<center>
nts version %(version)s. Copyright %(copyright)s Daniel A Graham. All rights reserved.
<br>
%(ntsinfo)s
<br>
%(sysinfo)s
<br>
%(markup)s
</center>
<pre>
Non editing shortcuts:
    F1                show this help information.
    F2                clear option panel settings.
    F3                apply option panel settings.
    F4                show 'about' information for nts.
    F5                if a note or leaf (notes file) is selected, open the
                      file using the external editor. Otherwise, open the node
                      (directory) using the system default application,
                      usually the file manager.
    Ctrl C            convert file. Select a file from a dialog and, if plain
                      text, then base-64 encode it and otherwise, if encoded,
                      then decode it. In either case, make the appropriate
                      change in the file extension.
    Ctrl F            move focus to the option panel f (FIND) field.
    Ctrl H            display notes as HTML with an option to print. Select
                      notes to be displayed from a list with defaults
                      corresponding to the current selection. Requires the
                      python package docutils. See 'Markup' below for more
                      information.
    Ctrl L            show nts message log with details of any problems
                      experienced in the last loading of the data files.
    Ctrl M            move the selected note it to a file to be selected 
                      from a file dialog. This dialog also allows creating
                      new files and folders.
    Ctrl N            create a new note. When finished use Ctrl-S, Shift
                      Ctrl-S or Alt-S to save it.
    Ctrl O            cycle the option panel o (OUTLINEBY) setting between
                      p)aths and t)ags.
    Ctrl P            move focus to the option panel p (PATH) field.
    Ctrl Q            quit nts.
    Ctrl R            reload data files.
    Ctrl T            move focus to the option panel t (TAG) field.
    Ctrl U            unselect all items.
    Ctrl X            export notes. Select notes to be exported from a list
                      with defaults corresponding to the current selection.
                      Selected notes will be exported as a restructured text
                      file to
                          %(ntsexport)s
                      (specified in %(ntsrc)s).

    Left Arrow        collapse any children and then move to the parent.
    Ctrl Left Arrow   move to parent and then collapse all children.
    Right Arrow       expand any children and then move down in the outline.
    Ctrl Right Arrow  expand entire branch and then move down in the outline.
    Up/Down Arrows    move up or down in outline without expanding or
                      collapsing any items.

    Double click      with a note selected, open the note for editing.
    Return            in the option panel PATH, TAG or FIND fields, apply
                      option panel settings. In the outline panel with a note
                      selected, open the note for editing.
    Tab               cycle focus between the outline and display panels.
    Escape            cancel editing a note. Warn if the note has been
                      modified.
    Delete            delete the selected note.

Editing shortcuts:
    Ctrl A                  Select all the text in the document
    Ctrl C                  Copy the selection to the clipboard
    Ctrl L                  Cut the line containing the cursor.
    Ctrl+Shift L            Delete the line containing the cursor.
    Ctrl Q                  Quit editing note. Prompt for confirmation if 
                            note is modified.
    Ctrl S                  Save changes to a note. If editing an existing 
                            note, replace it with the modified version. If 
                            creating a new note, append it to a file to be
                            chosen from a file dialog. This dialog also
                            allows creating new files and folders. 
    Ctrl T                  Switch the current line with the previous.
    Ctrl U                  Transform the selection to lower case.
    Ctrl+Shift U            Transform the selection to upper case.
    Ctrl V                  Paste the contents of the clipboard into the
                            document replacing the selection.
    Ctrl X                  Cut the selection to the clipboard
    Ctrl Y                  Redoes the next action on the undo history
    Ctrl Z                  Undo one action in the undo history
    Down Arrow              Move cursor down one line.
    Shift Down Arrow        Move cursor down one line extending selection 
                            to new cursor position.
    Ctrl Down Arrow         Scroll the document down, keeping the cursor
                            visible.
    Up Arrow                Move cursor up one line.
    Shift Up Arrow          Move cursor up one line extending selection to 
                            new cursor position.
    Ctrl Up Arrow           Scroll the document up, keeping the cursor 
                            visible.
    Left Arrow              Move cursor left one character.
    Shift Left Arrow        Move cursor left one character extending 
                            selection to new cursor position.
    Ctrl Left Arrow         Move cursor left one word.
    Ctrl+Shift Left Arrow   Move cursor left one word extending selection 
                            to new cursor position.
    Alt Left Arrow          Move to the previous change in capitalisation.
    Alt+Shift Left Arrow    Move to the previous change in capitalisation.
                            extending selection to new cursor position.
    Right Arrow             Move cursor right one character.
    Shift Right Arrow       Move cursor right one character extending 
                            selection to new cursor position.
    Ctrl Right Arrow        Move cursor right one word.
    Ctrl+Shift Right Arrow  Move cursor right one word extending selection 
                            to new cursor position.
    Alt Right Arrow         Move to the next change in capitalisation.
    Alt+Shift Right Arrow   Move to the next change in capitalisation
                            extending selection to new cursor position.
    Home                    Move cursor to before first visible character 
                            on line. If already there move to first character 
                            on line.
    Shift Home              Like Home but extending selection to new 
                            cursor position.
    Ctrl Home               Move cursor to first position in document.
    Ctrl+Shift Home         Move cursor to first position in document 
                            extending selection to new cursor position.
    Alt Home                Move cursor to first position on display line.
    Alt+Shift Home          Move cursor to first position on display line
                            extending selection to new cursor position.
    End                     Move cursor to last position on line.
    Shift End               Move cursor to last position on line extending
                            selection to new cursor position.
    Ctrl End                Move cursor to last position in document.
    Ctrl+Shift End          Move cursor to last position in document 
                            extending selection to new cursor position.
    Alt End                 Move cursor to last position on display line.
    Alt+Shift End           Move cursor to last position on display line
                            extending selection to new cursor position.
    Page up                 Move cursor one page up.
    Shift Page up           Move cursor one page up extending selection to 
                            new cursor position.
    Page down               Move cursor one page down.
    Shift Page down         Move cursor one page down extending selection 
                            to new cursor position.
    Shift Backspace         Cut the selection to the clipboard.
    Ctrl Delete             Delete the word to the left of the cursor.
    Ctrl Backspace          Delete the word to the right of the cursor
    Ctrl+Shift Delete       Delete backwards from the current position to 
                            the beginning of the line.
    Ctrl+Shift Backspace    Delete forwards from the current position to 
                            the end of the line.
    Insert                  Switch from insert to overtype mode or the 
                            reverse.
    Shift Insert            Paste the contents of the clipboard into the 
                            document replacing the selection.
    Ctrl Insert             Copy the selection to the clipboard
    Tab                     If selection is empty or all on one line 
                            replace the selection with a tab character. If
                            more than one line is selected, indent the 
                            lines.
    Shift Tab               Dedent the selected lines
    Return                  Insert a new line, may use a CRLF, CR or LF
                            depending on EOL mode.
    Shift Return            Insert a new line, may use a CRLF, CR or LF
                            depending on EOL mode.

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
    display panel. When you are finished, press Ctrl-S to save the 
    note either to an existing notes file or to a new file. The dialog will 
    offer the opportunity to create new folders if necessary.

    To delete a note, select the note and then press Delete. You will be
    prompted to confirm the deletion. If the last note in a file were removed,
    then the file itself would be deleted.

    To move a note, select the note and then press Ctrl-M. You will be 
    prompted to select a notes file. The note will then be appended to the new 
    file and deleted from the existing file. If the last note in a file were 
    moved, then the file itself would be deleted. 

    When making any of the changes listed above, nts will first make a backup
    of the existing file - see 'Rotating backup files' below. 

    You can also make changes to notes files using the editor you specified in
    your ~/.nts/rc file. Press F5 with a note selected and the file will be
    opened in your editor with the cursor on the relevant line. When the file
    containing the selected note is encoded, a temporary, plain text version
    of the file is created for editing. When finished editing the original
    file is replaced with an encoded version of the saved temporary file and
    the temporary file is then removed.

    Please use your favorite file manager to reorganize your nts date
    directory structure. If you press F5 on a node with any children, your
    system default application will be called with the relevant path. Normally
    this will open your file manager at the relevent directory.

Hierarchical notes:
    Notes files either have the extension '%(ntstxt)s' (plain text) or the
    extension '%(ntsenc)s' (base 64 encoded) and are located in or below 

        %(ntsdata)s

    Note that these settings reflect those in the rc file currently in use,
    '%(ntsrc)s'.

    Both file types support unicode characters with normal, readable display
    both in the GUI and in command line output. The base 64 encoding is
    intended to provide only VERY LIGHT WEIGHT protection (obfuscation) for
    encoded files outside nts.

    The directory structure below ntsdata provides the hierarchy for your
    notes. E.g., suppose you have the notes file:

            %(grandchild)s

    with the following content:

        ----------- begin grandchild.txt ----------------------
        + note a (tag 1, tag 2)
        the body of my first note

        + note b (tag 2, tag 3)
        the body of my second note
        ----------- end grandchild.txt ------------------------

    Then when outlining by **path** you would see:

        parent
            child
                grandchild
                    note a
                    note b

    and when outlining by **tag** you would see:

        tag 1
            note a
        tag 2
            note a
            note b
        tag 3
            note b

    Each notes file can contain one or more notes using the following format
    for each::

        + note title (optional tags)
        one or more lines containing the body of the note
        with all white space preserved.

    In the note title, the '+' must be in the first column. If given, tags
    must be comma separated and enclosed in parentheses. White space in the
    note body is preserved but whitespace between notes is ignored. The note
    body continues until another note line or the end of the file is reached.

Rotating backup files:
    A backup is made of any file before nts makes any changes to it. For
    example, before saving a change to the base 64 encoded file,
    'mynotes.enc', the exising file would first be copied to '.mynotes.bk1'.
    If '.mynotes.bk1' already exists and it is more than one day old, it would
    first be moved to '.mynotes.bk2'. Similarly, if '.mynotes.bk2' already
    exists, then it would be first be moved to '.mynotes.bk3' and so forth. In
    this way, up to 'numbaks' (3 by default) rotating backups of are kept with
    '.bk1' the most recent.

    The process is similar for a plain text file but the copy is encoded
    before saving. Thus all backups are base 64 encoded.

Markup:
    Either 'markdown' or 'restructured text' markup can be used in the body of
    notes. Moreover, by setting either

        markup = "md"  

    or 

        markup = "rst"

    in your nts rc file, nts will provide consistent markup when exporting
    selected notes. Further, if markdown (or docutils for restructured text)
    is installed on your system, you will be able to display selected notes as
    html with an option to print.

    There are many similarities between the two types of markup, e.g., *this
    would be emphasized* and **this would be bold-faced** under either. More
    generally, markdown is somewhat simpler to use but also somewhat less
    powerful. For details, see

          http://daringfireball.net/projects/markdown/syntax

          http://docutils.sourceforge.net/docs/user/rst/quickref.html

    Using the standard tools that come with python's docutils module, rst
    output can be easily converted to a number of formats including HTML,
    Latex and OpenOffice ODF. Similarly, md output can be converted to other
    formats using 'pandoc':

          http://johnmacfarlane.net/pandoc/ 
</pre>
"""
