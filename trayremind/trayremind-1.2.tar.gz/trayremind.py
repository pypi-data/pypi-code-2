#!/usr/bin/env python

import gtk, gobject, signal
import subprocess as sp


#Command to be run on activating icon.
calviewer = ['tkremind']
#Remind daemon command
caldaemon = ['remind', '-z0']

iconTheme = gtk.icon_theme_get_default()
#Sets icon defaults.  First checks if icon is present; if not, falls back on stock icons.
defaultIcon = 'stock_calendar'
if not iconTheme.has_icon(defaultIcon):
	defaultIcon = gtk.STOCK_INFO

notifyingIcon = 'appointment'
if not iconTheme.has_icon(notifyingIcon):
	notifyingIcon = gtk.STOCK_DIALOG_WARNING

clearIcon = notifyingIcon

viewCalendarIcon = defaultIcon

closeCalendarIcon = gtk.STOCK_STOP

rereadIcon = gtk.STOCK_REFRESH



class TrayRemind(gtk.StatusIcon):
	def __init__(self):
		gtk.StatusIcon.__init__(self)
		self.set_from_icon_name(defaultIcon)
		self.notifying = False

		self.window = None
		#Open the Remind daemon.
		self.daemon = sp.Popen(caldaemon, stdin=sp.PIPE, stdout=sp.PIPE)
		#Watch what the daemon says.
		gobject.io_add_watch(self.daemon.stdout, gobject.IO_IN, self.onData)
		#Quit if the daemon does.
		gobject.child_watch_add(self.daemon.pid, gtk.main_quit)

		self.connect('activate', TrayRemind.onActivate)
		self.connect('popup-menu', TrayRemind.onPopup)
	
	def onActivate(self):
		#Silence an active alarm.
		if self.notifying: self.onClear()
		#Or open/close tkremind.
		else: self.onView()

	def onPopup(self, button, activate_time):
		menu = gtk.Menu()

		if self.notifying:
			clear = gtk.ImageMenuItem('{0}\nClear _warning'.format(self.msg))
			clear.set_image(gtk.image_new_from_icon_name(clearIcon, gtk.ICON_SIZE_LARGE_TOOLBAR))
			menu.append(clear)
			clear.connect('activate', self.onClear)

			separator = gtk.SeparatorMenuItem()
			menu.append(separator)

		if self.window is None or self.window.poll() is not None:
			label = 'View _calendar'
			icon = viewCalendarIcon
		else:
			label = 'Close _calendar'
			icon = closeCalendarIcon
		cal = gtk.ImageMenuItem(label)
		cal.set_image(gtk.image_new_from_icon_name(icon, gtk.ICON_SIZE_MENU))
		menu.append(cal)
		cal.connect('activate', self.onView)

		reread = gtk.ImageMenuItem('_Reread')
		reread.set_image(gtk.image_new_from_icon_name(rereadIcon, gtk.ICON_SIZE_MENU))
		menu.append(reread)
		reread.connect('activate', self.onReread)

		menu.show_all()
		menu.popup(None,None,None,button,activate_time)
	
	def onData(self, source, condition):
		note = source.readline()
		if note.split()[0:2] == ['NOTE', 'reminder']:
			msg = ''
			nextline = source.readline()
			while nextline != 'NOTE endreminder\n':
				msg = msg + nextline
				nextline = source.readline()
			self.reminder(note.split()[-3], msg.strip())
		else: print note,
		return True
	
	def onClear(self, widget=None):
		self.set_from_icon_name(defaultIcon)
		self.set_blinking(False)
		self.notifying = False
	
	def onView(self, widget=None):
		if self.window is None or self.window.poll() is not None:
			self.window = sp.Popen(calviewer)
		else:
			self.window.terminate()
			self.window = None
	
	def reminder(self, time, msg):
		self.msg = ' - '.join((time,msg))
		self.set_tooltip(self.msg)
		self.set_from_icon_name(notifyingIcon)
		self.set_blinking(True)
		self.notifying = True
	
	def onReread(self, signal=None, frame=None):
		self.daemon.stdin.write('REREAD\n')

if __name__ == '__main__':
	from sys import argv, exit
	try: remfile = argv[1]
	except IndexError:
		print "Usage: trayremind FILE"
		exit(1)

	calviewer.append(remfile)
	caldaemon.append(remfile)

	tr = TrayRemind()
	gtk.main()
