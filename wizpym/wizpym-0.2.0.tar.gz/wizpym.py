# -*- coding: utf-8 -*-
#
# wizpym - The Wyzard Python Module, a tool to write Wizard-like apps.
# Copyright (C) 2010 David Soulayrol <david.soulayrol@gmail.com>
#
# wizpym is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""A tool to write Wizard-like apps.

This module provides classes to easily build wizard-type applications
with GTK. This kind of application is composed of a succession of
panes which asks the user for inputs, and processes them to achieve
some result. It is a quite natural way to propose a graphical view for
short and simple tasks, or batch processes.

Wizard applications thus are successions of short tasks which
cooperate to work on some subject, each one adding a value or choosing
the next step in the whole process. wizpym provides a framework for
the developers to focus on these tasks by providing the tools to plug
them together and to handle background activities.
"""

import gobject
import gtk
import threading

__all__ = ['InvalidPane', 'Pane', 'ActivePane', 'Frame']
__version_info__ = (0, 2, 0)
__version__ = '.'.join((str(i) for i in __version_info__))


class InvalidPane(Exception):
    """Raised when a wrong argument is given in pane manipulating methods."""
    pass


class Pane(gtk.VBox):
    """A single pane from a Wizard.

    Each pane of a wizard has zero or one predecessor and one or many
    successors. The successor is chosen upon an switch, which can be
    altered when the user interacts with the pane.

    All panes from one wizard share a subject. The subject is the
    object that forwards data from one pane to the other and can be a
    simple string as well as a complex structure. It is initially set
    by the wizard Frame when the first pane is created.

    A pane can also state that it is not ready to fulfill the next
    pane requirements. The frame will grey the Next button as long as
    its ready attribute is set to False.
    """

    def __init__(self, frame):
        """Constructor.

        A fresh pane is in a ready state and has no successors nor
        predecessor. The constructor doesn't either set the subject:
        the wizard frame takes care of setting it, and passing it from
        one pane to the other.

        Note that all wizard panes constructors should take no
        parameter since they are called automatically by the wizard
        frame. The developer should consider using the wizard subject
        or environment variables to configure the panes if necessary.
        """
        gtk.VBox.__init__(self, False, 5)

        self._frame = frame

        self._header = gtk.VBox()
        self.pack_start(self._header, False)

        self._error = gtk.VBox()
        self.pack_end(self._error, False)

        self._subject = None
        self._switch = None
        self._successors = {}
        self._ready = True

    def link_to(self, klass):
        """Add a successor to this pane.

        This method is intended to be called by the pane itself at
        construction time to set its successors, but nothing forbids
        to do it a different way.

        The switch is set to the first successor set. If the provided
        pane is already a successor of this pane, the InvalidPane
        exception is raised.
        """
        if klass is None or klass in self._successors:
            raise InvalidPane()
        self._successors[klass] = klass(self._frame)
        if len(self._successors) == 1:
            self._switch = klass

    def set_header(self, msg):
        """Add a help header to the pane with the given message.

        Since it is quite common that panes begin with a little guide
        explaining the current step, calling this method will ensure
        such panes all present the same header style.
        """
        self._header.foreach(lambda w: self._header.remove(w))
        if msg:
            help_label = gtk.Label(msg)
            help_label.set_justify(gtk.JUSTIFY_FILL)
            help_label.set_line_wrap(True)
            self._header.pack_start(help_label, False, False, 10)
            self._header.pack_start(gtk.HSeparator(), False)
            self._header.show_all()

    def set_error(self, msg):
        """Add a help header to the pane with the given message.

        Since it is quite common that panes begin with a little guide
        explaining the current step, calling this method will ensure
        such panes all present the same header style.
        """
        self._error.foreach(lambda w: self._error.remove(w))
        if msg:
            error_label = gtk.Label()
            error_label.set_markup(
                '<span foreground="red" weight="bold">' + msg + '</span>')
            error_label.set_justify(gtk.JUSTIFY_FILL)
            error_label.set_line_wrap(True)
            self._error.pack_start(error_label, False, False, 10)
            self._error.show_all()

    def clear(self, safe=None):
        """Clear all the pane children but internal widgets.

        If the safe parameter is a list, then its content should be
        widgets that should not be removed either. Invalid parameters
        are ignored.

        This method leaves the header and the error labels untouched
        (eg. if they were displayed, they remain displayed).
        """
        if safe is None or not isinstance(safe, list):
            safe = []
        safe.extend([self._header, self._error])
        for w in filter(lambda x: x not in safe, self.get_children()):
            self.remove(w)

    def switch(self, klass):
        """Update the switch using the given class.

        If the provided class is None or is not a successor of this
        pane, the InvalidPane exception is raised.
        """
        if klass is None or klass in [o.__class__ for o in self._successors]:
            raise InvalidPane()
        self._switch = klass

    def is_terminal(self):
        """Whether this pane has no successor."""
        return len(self._successors) == 0

    def enter(self):
        """Proceed to this pane initialization.

        This method is called by the wizard main frame when this pane
        is entered or reentered from its predecessor. It should be
        overriden if this pane needs to update itself with the received
        subject.
        """
        pass

    def leave(self):
        """Proceed to this pane finalization.

        This method is called when this pane is replaced by a
        successor. It should be overriden if this pane needs to
        compute or to retrieve some data to update the subject before
        it is passed to the successor.
        """
        pass

    def next(self):
        """Return the next pane as designated by the switch."""
        return self._successors.get(self._switch)

    def _get_subject(self):
        return self._subject

    def _set_subject(self, s):
        self._subject = s

    def _is_ready(self):
        return self._ready

    def _set_ready(self, v):
        self._ready = v
        self._frame.update()

    subject = property(_get_subject, _set_subject, None, 'This pane subject')
    ready = property(_is_ready, _set_ready, None, 'Whether the next pane can be called')


class ActivePane(Pane):
    """An active pane from a Wizard.

    ActivePane specializes the Pane class by providing a mean of
    running long tasks in the background. Applications using this kind
    of Pane should not forget to call gobject.threads_init before
    anything else.
    """

    def __init__(self, frame):
        """Constructor."""
        Pane.__init__(self, frame)

        self._progress_box = gtk.VBox()
        self.pack_end(self._progress_box, False)

        self._thread = None

    def update_progress_bar(self, fraction=None, text=None):
        """Update this pane's progress bar.

        The progress bar, when used, shows up at the bottom of the
        pane. When this method is called, it is first displayed is
        absent, and the updated with the given fraction, between 0.0
        and 1.0, and the given text if any. In the special case where
        the fraction is not provided, the ProgressBar.pulse method is
        invoked.

        Returns True, so that it can be used in a GObject timer.

        This method is non-GTK thread safe, which means that any
        thread can call it.
        """
        gobject.idle_add(self._do_update_progress_bar, fraction, text)
        return True

    def hide_progress_bar(self):
        """Hide this pane's progress bar.

        The progress bar is in fact destroyed, so its state is lost.

        This method is non-GTK thread safe, which means that any
        thread can call it. If no progress bar is currently displayed,
        it does nothing.
        """
        if len(self._progress_box.get_children()):
            gobject.idle_add(self._progress_box.remove,
                             self._progress_box.get_children()[0])

    def clear(self, safe=None):
        """Clear all the pane children but internal widgets.

        This method specializes Pane.clear so that the progress box is
        also left untouched.
        """
        if safe is None or not isinstance(safe, list):
            safe = []
        safe.append(self._progress_box)
        Pane.clear(self, safe)

    def enter(self):
        """Proceed to this pane initialization.

        See Pane.enter. All ActivePane instances that override this
        method should call thir parent one, since the background task
        start is handled here.
        """
        self._thread = threading.Thread(
            name=self.__class__.__name__, target=self._wrapper)
        self._thread.start()

    def is_running(self):
        """Whether this pane background task is running."""
        return not self._thread is None and self._thread.is_alive()

    def _runner(self):
        """The background task.

        All ActivePane instances should override this method to put
        their behaviour. It is up to the developer to handle
        synchronisation problems. Note in particular that all pane
        drawing invoked from there should be done through some helper
        like gobject.idle_add.
        """
        pass

    def _wrapper(self):
        """A internal wrapper around the pane task."""
        gobject.idle_add(self._frame.lock)
        self._runner()
        gobject.idle_add(self._frame.unlock)

    def _do_update_progress_bar(self, fraction, text):
        """An internal facility to update the progress bar.

        This private method is intended to be called in the GTK main
        thread.
        """
        if not len(self._progress_box.get_children()):
            self._progress_box.pack_start(gtk.ProgressBar())
            self._progress_box.show_all()
        bar = self._progress_box.get_children()[0]
        if text:
            bar.set_text(text)
        bar.pulse() if fraction is None else bar.set_fraction(fraction)


class Frame(gtk.Dialog):
    """The Wizard window.

    Each wizard application is built around exactly one Frame
    instance. The frame is responsible to show the panes and to
    forward the subject between them.
    """

    def __init__(self, start_klass, subject="", title='Wizard', min_size=(400, 200)):
        """Constructor.

        A frame must be provided at least the initial pane class. If
        no subject is set, then a (initially empty) string is provided
        to the first pane.
        """
        gtk.Dialog.__init__(self, title)

        # Members are all defined before calling the First pane so as
        # to be ready if the start pane constructor invokes the frame
        # (such as the ready attribute setting)
        self._locked = False
        self._track = []

        self._prev_button = gtk.Button('Previous')
        self._prev_button.set_sensitive(False)
        self._next_button = gtk.Button('Next')
        self._next_button.set_sensitive(False)
        self._quit_button = gtk.Button('Quit')
        self._quit_button.set_sensitive(True)

        self.set_default_size(min_size[0], min_size[1])
        self.set_position(gtk.WIN_POS_CENTER)
        self.has_separator = True
        self.add_action_widget(self._prev_button, gtk.RESPONSE_REJECT)
        self.add_action_widget(self._next_button, gtk.RESPONSE_ACCEPT)
        self.add_action_widget(self._quit_button, gtk.RESPONSE_CLOSE)
        self.connect('close', gtk.main_quit)
        self.connect('destroy', gtk.main_quit)
        self.connect("response", self._on_button)

        start_pane = start_klass(self)
        start_pane.subject = subject
        self._track = [start_pane]

        self._enter_pane(start_pane, True)

    def lock(self):
        """Freeze the previous and next buttons.

        This method is called by ActivePane instances when their
        background task is started.
        """
        self._locked = True
        self.update()

    def unlock(self):
        """Unfreeze the previous and next buttons.

        This method is called by ActivePane instances when their
        background task is terminated.
        """
        self._locked = False
        self.update()

    def update(self):
        """Update the frame buttons display."""
        # Beware that this method can be called early, before the track
        # contains the first pane
        if len(self._track):
            pane = self._track[-1]
            self._prev_button.set_sensitive(
                not self._locked and len(self._track) > 1)
            self._next_button.set_sensitive(
                not self._locked and pane.ready and not pane.is_terminal())
            self._quit_button.set_sensitive(not self._locked)

    def _on_button(self, w, response_id):
        """The frame buttons handler."""
        if response_id == gtk.RESPONSE_REJECT:
            if len(self._track) > 1:
                self._exit_pane(self._track.pop(), False)
                self._enter_pane(self._track[-1], False)
        elif response_id == gtk.RESPONSE_ACCEPT:
            p = self._track[-1].next()
            if p:
                self._exit_pane(self._track[-1], True)
                p.subject = self._track[-1].subject
                self._track.append(p)
                self._enter_pane(p, True)
        elif response_id == gtk.RESPONSE_CLOSE:
            gobject.idle_add(gtk.main_quit)

    def _enter_pane(self, pane, forward):
        """Handle a new pane display."""
        if forward:
            pane.enter()
        self.update()
        self.vbox.pack_start(self._track[-1], True, True)
        self.vbox.show_all()

    def _exit_pane(self, pane, forward):
        """Handle a pane exit."""
        if forward:
            pane.leave()
        self.vbox.remove(pane)


class AboutTestPane(Pane):
    def __init__(self, frame):
        Pane.__init__(self, frame)

        self.link_to(InputTestPane)

        self.pack_start(gtk.Label('A simple search tool.'), True, True, 10)
        self.pack_start(
            gtk.Label(
                'Copyright 2010  David Soulayrol <david.soulayrol@gmail.com>'), False)

        comment = gtk.Label()
        comment.set_markup('This wizard tests the main features of wizpym, '
                           'which are:\n\n'
                           '• The handling of a flow of panes, each one having '
                           'any number of successors.\n'
                           '• A full history to go back the full track down to '
                           'the beginning and to keep the status of the reverted panes.\n'
                           '• Data transfer from one pane to the next one.\n'
                           '• The possiblity to do heavy stuff in background on '
                           'each pane.\n\n\n'
                           'This program comes with ABSOLUTELY NO WARRANTY. '
                           'This is free software and you are welcome to '
                           'redistribute it under certain conditions. See '
                           '<a href="http://www.gnu.org/licenses">GNU licenses</a> '
                           'for details.')
        comment.set_line_wrap(True)
        self.pack_start(comment, True, True, 10)


class InputTestPane(Pane):
    def __init__(self, frame):
        Pane.__init__(self, frame)

        self.set_header('Please select your kind of search and fill in criteria fields.')
        self.ready = False

        self.link_to(GoogleSearchTestPane)
        self.link_to(LocalSearchTestPane)

        frame = gtk.Frame('Kind of search:')
        frame.set_border_width(10)
        self.pack_start(frame, padding=10)
        vbox = gtk.VBox()
        frame.add(vbox)

        button = gtk.RadioButton(None, 'Search Google Code')
        button.connect("toggled", self._on_button, GoogleSearchTestPane)
        button.set_active(True)
        vbox.pack_start(button)

        button = gtk.RadioButton(button, "Search Local Files")
        button.connect("toggled", self._on_button, LocalSearchTestPane)
        vbox.pack_start(button)

        box = gtk.HBox(False, 10)
        box.set_border_width(10)
        self._folder_entry = gtk.Entry()
        self._folder_entry.connect('changed', self._on_entry_update)
        box.pack_start(gtk.Label('Directory:'), False)
        box.pack_start(self._folder_entry)
        vbox.pack_start(box)

        box = gtk.HBox(False, 10)
        box.set_border_width(10)
        self._keywords_entry = gtk.Entry()
        self._keywords_entry.connect('changed', self._on_entry_update)
        box.pack_start(gtk.Label('Keywords:'), False)
        box.pack_start(self._keywords_entry)
        self.pack_start(box)

        self._update_status()

    def leave(self):
        self.subject[0] = self._keywords_entry.get_text()
        self.subject[1] = self._folder_entry.get_text()

    def _on_entry_update(self, w):
        self._update_status()

    def _on_button(self, w, klass):
        if w.get_active():
            self.switch(klass)
        self._update_status()

    def _update_status(self):
        r = len(self._keywords_entry.get_text())
        e = None if r else 'Please fill in the keywords field'

        if isinstance(self.next(), LocalSearchTestPane):
            if not len(self._folder_entry.get_text()):
                r = False
                e = 'Local search needs a root folder'
            else:
                try:
                    os.stat(self._folder_entry.get_text())
                except OSError:
                    r = False
                    e = self._folder_entry.get_text() + ' is not a valid path'

        self.set_error(e)
        self.ready = r


class GoogleSearchTestPane(ActivePane):
    PATH = 'https://www.google.com/codesearch/feeds/search?'
    XMLNS_ATOM = '{http://www.w3.org/2005/Atom}'
    XMLNS_GCS = '{http://schemas.google.com/codesearch/2006}'

    def __init__(self, frame):
        ActivePane.__init__(self, frame)

    def enter(self):
        self.set_header('Google Code results for: "' + self.subject[0] + '"')
        self.clear()

        # Start thread
        ActivePane.enter(self)

    def _runner(self):
        timer = gobject.timeout_add(100, lambda: self.update_progress_bar())
        self.update_progress_bar(text='Searching...')
        c = httplib.HTTPSConnection('www.google.com')
        c.request('GET', self.PATH + urllib.urlencode({'q': self.subject[0]}),
                  None, {'GData-Version': '2'})
        self.hide_progress_bar()
        gobject.source_remove(timer)
        gobject.idle_add(self._show_response, c.getresponse())

    def _show_response(self, r):
        lbl = None
        if r.status != 200:
            lbl = gtk.Label('Got error (' + r.reason + ') from google')
            lbl.show()
            self.pack_start(lbl)
        else:
            tree = etree.fromstring(r.read())
            for e in tree.findall(self.XMLNS_ATOM + 'entry'):
                lbl = gtk.Label(e.find(self.XMLNS_GCS + 'package').get('name'))
                lbl.show()
                self.pack_start(lbl)


class LocalSearchTestPane(ActivePane):
    def __init__(self, frame):
        ActivePane.__init__(self, frame)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()
        textview.set_editable(False)
        sw.add(textview)
        self.pack_start(sw)

        self._buffer = textview.get_buffer()

    def enter(self):
        self.set_header(
            'Grep results for: "' + self.subject[0].split()[0] + '" in ' + self.subject[1])

        # Start thread
        ActivePane.enter(self)

    def _runner(self):
        timer = gobject.timeout_add(100, lambda: self.update_progress_bar())
        self.update_progress_bar(0, 'Counting files...')
        nb_files = 0
        for root, dirs, files in os.walk(self.subject[1]):
            self._filter_directories(dirs)
            nb_files += len(files)
        gobject.source_remove(timer)

        # Tweak so that the division below operates on floats.
        count = float(0)
        item = self.subject[0].split()[0]
        for root, dirs, files in os.walk(self.subject[1]):
            self._filter_directories(dirs)
            for f in files:
                name = os.path.join(root, f)
                p = subprocess.Popen(['grep', '-iHn', item, name],
                                     stdout=subprocess.PIPE)
                gobject.idle_add(self._buffer.insert_at_cursor, p.communicate()[0])
                self.update_progress_bar(
                    count / nb_files,
                    name + '(' + str(int(count)) + '/' + str(nb_files) + ')')
                count += 1
        self.hide_progress_bar()

    def _filter_directories(self, dirs):
        for f in ['CVS', '.svn', '.git']:
            if f in dirs:
                dirs.remove(f)


if __name__ == '__main__':
    import httplib, os, subprocess, urllib
    import xml.etree.ElementTree as etree

    gobject.threads_init()
    Frame(AboutTestPane, ['', '']).run()
    gtk.main()

