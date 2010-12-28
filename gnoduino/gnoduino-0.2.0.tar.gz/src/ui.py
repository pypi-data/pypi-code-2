# gnoduino - Python Arduino IDE implementation
# Copyright (C) 2010  Lucian Langa
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import sys
import gconf
import glib
import gobject
import gtk
import subprocess
import select
import shutil

import gettext
_ = gettext.gettext

import board
import config
import compiler
import programmer
import misc
import prefs
import uploader
import serialio
import srcview
import gnoduino

import gtksourceview2
font = "Monospace 10"

MW = "/apps/gnoduino/width"
MH = "/apps/gnoduino/height"
user_library_key = "/apps/gnoduino/user_library"
serial_port_key = "/apps/gnoduino/serial_port"
serial_baud_rate_key = "/apps/gnoduino/serial_baud_rate"

def setupPage(w, page, p):
	misc.set_widget_font(getCurrentView(), config.cur_font)
	getCurrentPage().queue_resize()
	pg = w.get_nth_page(p)
	cl = pg.get_data("close");
	if cl == None: return
	accel = gtk.AccelGroup()
	cl.add_accelerator("activate", accel, ord("w"), gtk.gdk.CONTROL_MASK, 0)
	mainwin.add_accel_group(accel)
	srcview.updatePos(pg.get_data("buffer"), sb2)

def replacePage(page):
	nb.remove_page(nb.page_num(page))

def destroyPage(w, b):
	f = b.get_data("file")
	buf = b.get_data("buffer")
	if misc.bufferModified(buf, f) is True:
		save = misc.createPopup("Save document", mainwin, \
			_("Save changes to document\n%s\n before closing?" % f))
		if save == gtk.RESPONSE_YES:
			csave(None, False)
	nb.remove_page(nb.page_num(b))
	if nb.get_n_pages() < 1:
		createPage(nb)

def updatePageTitle(w, status):
	page = getCurrentPage()
	f = page.get_data("file")
	l = page.get_data("label")
	if f != None:
		name = os.path.basename(f)
	else:
		fh = 0
		name = "Untitled"

	if (misc.bufferModified(w, f)):
		l.set_text(name+"*")
	else:
		l.set_text(name)
	srcview.updatePos(w, status)

def switchPage(page, a, b, c):
	nb.set_current_page(int(chr(b-1)))

def createPage(nb, f=None):
	hbox = gtk.HBox(False, 0)
	flabel = gtk.Label(os.path.basename(f) if f else "Untitled")
	hbox.pack_start(flabel, True, False, 3)
	b = gtk.Button()
	img = gtk.Image()
	img.set_from_icon_name(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
	img.set_pixel_size(11)
	b.set_image(img)
	b.set_relief(gtk.RELIEF_NONE)
	hbox.pack_start(b, True, True)
	hbox.show_all()
	(sbuf,sv) = srcview.createsrcview(sb2, f)
	sbuf.connect("changed", updatePageTitle, sb2)
	sw = gtk.ScrolledWindow()
	sw.add(sv)
	sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	sw.set_placement(gtk.CORNER_BOTTOM_LEFT)
	sw.set_shadow_type(gtk.SHADOW_IN)
	sw.show_all()
	p = nb.append_page(sw, hbox)
	wp = nb.get_nth_page(p)
	wp.set_data("file", f)		#add file information to the page widget
	wp.set_data("buffer", sbuf)	#add buffer information to the page widget
	wp.set_data("view", sv)	#add buffer information to the page widget
	wp.set_data("label", flabel)	#add source view widget to the page widget
	wp.set_data("close", b)	#add close widget to the page widget
	nb.set_current_page(p)
	page = nb.get_nth_page(p)
	nb.set_scrollable(True);
	nb.set_tab_reorderable(page, True);
	accel = gtk.AccelGroup()
	for i in range(1, 10):
		accel.connect_group(ord(str(i)), gtk.gdk.MOD1_MASK, 0,
			switchPage)
	mainwin.add_accel_group(accel)
	sv.grab_focus()
	b.connect("clicked", destroyPage, sw)
	accel = gtk.AccelGroup()
	b.add_accelerator("activate", accel, ord("w"), gtk.gdk.CONTROL_MASK, 0)
	mainwin.add_accel_group(accel)
	srcview.updatePos(sbuf, sb2)
	return sv

def cnew(widget, data=None):
	createPage(nb, data)

def searchFile(nb, f):
	for i in range(nb.get_n_pages()):
		of = nb.get_nth_page(i).get_data("file")
		if of == f:
			nb.set_current_page(i)
			return True
	return False

def processFile(w):
	if searchFile(nb, w.get_filename()) == True:
		w.destroy()
		return
	page = getCurrentPage()
	createPage(nb, w.get_filename())
	if page.get_data("label").get_text() == "Untitled":
		replacePage(page)

def saveAs():
	p = gtk.FileChooserDialog("Save file", None, gtk.FILE_CHOOSER_ACTION_OPEN,
		(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
		gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
	p.set_size_request(650, 500)
	p.show_all()
	if p.run() == gtk.RESPONSE_ACCEPT:
		f = p.get_filename()
		p.destroy()
		return f
	p.destroy()
	return None

def copen(widget, data=None):
	p = gtk.FileChooserDialog("Open file", None, gtk.FILE_CHOOSER_ACTION_OPEN,
		(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
		gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
	p.set_size_request(650, 500)
	p.show_all()
	if p.run() == gtk.RESPONSE_ACCEPT:
		processFile(p)
	p.destroy()

def csave_as(w, data=None):
	csave(w, True)

def csave(w, data=None):
	page = getCurrentPage()
	l = page.get_data("label")
	b = page.get_data("buffer")
	f = page.get_data("file")
	if f == None or data == True:
		f = saveAs()
		if f == None: return
		else:
			if os.path.exists(f):
				p = misc.MessageBox()
				res = p.show("""<b>A file named %s already exists. Do you want to replace it?</b>""" % f,
				"The file already exists in \"%s\". Replacing it will overwrite its contents." % os.path.dirname(f))
				if not res: return
			l.set_text(os.path.basename(f))
			page.set_data("file", f)
	F = open(f, "w")
	F.write(b.get_text(b.get_start_iter(), b.get_end_iter()))
	F.close()
	updatePageTitle(b, sb2)

def quit(widget, data=None):
	shutil.rmtree(id, True)
	gtk.main_quit()

def find(widget, data=None):
	find = gui.get_object("find")
	find_text = gui.get_object("find-text")
	find_text.child.select_region(0, -1)
	cbs = ["checkbutton1", "checkbutton2","checkbutton3", "checkbutton4"]
	find_text.connect("key-release-event", srcview.findText, [gui.get_object(i) for i in cbs])
	find.set_default_response(gtk.RESPONSE_OK)
	r =  find.run()
	if r == 1:
		srcview.findText(find_text, -1, [gui.get_object(i) for i in cbs])
	find.hide()

def compile(widget, data=file):
	cserial(None, 0, sctw)
	page = getCurrentPage()
	obj = compiler.compile(page.get_data("view"), id, tw, sb) #page.get_data("buffer")
	return obj

def upload(widget, serial, data=file):
	obj = compile(widget, data)
	if obj == -1: return
	while (gtk.events_pending()):
		gtk.main_iteration()
	uploader.upload(obj, serial, tw, sb)

def menuUpload(widget, data=None):
	upload(widget, ser, data)

def about(widget, data=None):
	about = gui.get_object("about")
	about.set_version(gnoduino.__version__)
	about.run()
	about.hide()

def menuResetBoard(widget, data=None):
	ser.resetBoard()

def preferences(widget, data=None):
	global client
	pref = gui.get_object("preferences")
	fs = gui.get_object("fontsize")
	p = prefs.preferences()
	if config.cur_font != -1:
		fs.set_value(float(config.cur_font.split(",")[2]))
	else:
		fs.set_value(float(p.getValue("editor.font").split(",")[2]))
	bv = gui.get_object("build.verbose")
	if config.build_verbose != -1:
		bv.set_active(bool(config.build_verbose))
	else:
		bv.set_active(bool(p.getValue("build.verbose")))
	ul = gui.get_object("user.library")
	if (config.user_library != None and config.user_library != -1):
		ul.set_text(str(config.user_library))
	else:
		ul.set_text(str(client.get_string(user_library_key)) if client.get_string(user_library_key) != None else "")
	r = pref.run()
	if r == 1:
		config.cur_font =  p.getValue("editor.font").split(",")[0] + \
			"," + p.getValue("editor.font").split(",")[1] + \
			"," + str(int(fs.get_value()))
		misc.set_widget_font(tw, config.cur_font)
		misc.set_widget_font(sctw, config.cur_font)
		misc.set_widget_font(getCurrentView(), config.cur_font)
		config.user_library = ul.get_text()
		client.set_string(user_library_key, config.user_library)
	pref.hide()

def stop(widget, data=None):
	print "stop"

def cserial(w, st, data=None):
	global sertime
	"""inhibit function"""
	if st == 0:
		if sertime:
			glib.source_remove(sertime)
			sertime = None
			vbox.remove(scon)
			vbox.add(con)
		return
	if (sertime == None):
		sertime = glib.timeout_add(1000,
			ser.updateConsole,
			data)
		vbox.remove(con)
		vbox.add(scon)
	else:
		glib.source_remove(sertime)
		sertime = None
		vbox.remove(scon)
		vbox.add(con)

def burnBootloader(w, id):
	uploader.burnBootloader(ser, tw, sb, id)

def setBaud(w, data=None):
	ser.resetBoard()
	ser.serial.close()
	if config.serial_baud_rate == -1:
		config.serial_baud_rate = client.get_string(serial_baud_rate_key)
		if config.serial_baud_rate: defbaud = config.serial_baud_rate
		else: defbaud = p.getValue("serial.debug_rate")
	else:
		if w: defbaud = ser.getBaudrates()[w.get_active()]
	ser.serial.baudrate = [i for i in ser.getBaudrates() if i == defbaud][0]
	ser.serial.open()
	client.set_string(serial_baud_rate_key, defbaud)

def serSendText(w, data=None):
	ser.serial.write(w.get_text())
	w.set_text("")

def undo(w, data=None):
	page = getCurrentPage()
	b = page.get_data("buffer")
	if b.can_undo(): b.undo()

def redo(w, data=None):
	page = getCurrentPage()
	b = page.get_data("buffer")
	if b.can_redo(): b.redo()

menus = [
		("menu-new", cnew, (ord('n'), gtk.gdk.CONTROL_MASK)),
		("menu-open", copen, (ord('o'), gtk.gdk.CONTROL_MASK)),
		("menu-save", csave, (ord('s'), gtk.gdk.CONTROL_MASK)),
		("menu-save-as", csave_as, (ord('s'), gtk.gdk.CONTROL_MASK|gtk.gdk.SHIFT_MASK)),
		("menu-quit", quit, (ord('q'), gtk.gdk.CONTROL_MASK)),
		("menu-find", find, (ord('f'), gtk.gdk.CONTROL_MASK)),
		("menu-undo", undo, (ord('z'), gtk.gdk.CONTROL_MASK)),
		("menu-redo", redo, (ord('z'), gtk.gdk.CONTROL_MASK|gtk.gdk.SHIFT_MASK)),
		("menu-compile", compile, (ord('r'), gtk.gdk.CONTROL_MASK)),
		("menu-reset-board", menuResetBoard, (ord('m'), gtk.gdk.CONTROL_MASK)),
		("menu-preferences", preferences, (None, None)),
		("menu-upload", menuUpload, (ord('u'), gtk.gdk.CONTROL_MASK)),
		("menu-about", about, (None, None)),

	]

def menu(gui):
	[gui.get_object(i[0]).connect("activate", i[1]) for i in menus]
	accel = gtk.AccelGroup()
	[gui.get_object(i[0]).add_accelerator("activate", \
		accel, i[2][0], i[2][1], 0) for i in menus if i[2][0] != None]
	mainwin.add_accel_group(accel)

def createCon():
	sw = gtk.ScrolledWindow()
	sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	sw.set_shadow_type(gtk.SHADOW_IN)
	tmp = gtk.TextView()
	tmp.set_size_request(-1, 150)
	tmp.set_editable(False)
	twbuf = gtk.TextBuffer()
	tmp.set_buffer(twbuf)
	tmp.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
	tmp.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color("#ffffff"))
	misc.set_widget_font(tmp, p.getValue("editor.font").replace(",", " "))
	sw.add(tmp)
	sw.show_all()
	return (sw, tmp)

def createScon():
	global baud
	sw = gtk.ScrolledWindow()
	sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	sw.set_shadow_type(gtk.SHADOW_IN)
	tmp = gtk.TextView()
	tmp.set_size_request(-1, 150)
	tmp.set_editable(False)
	twbuf = gtk.TextBuffer()
	tmp.set_buffer(twbuf)
	tmp.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
	tmp.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color("#ffffff"))
	misc.set_widget_font(tmp, p.getValue("editor.font").replace(",", " "))
	sw.add(tmp)
	hbox = gtk.HBox(False, 0)
	s = gtk.Button("Send")
	c = gtk.Button("Clear")
	c.connect("clicked", ser.clearConsole, tmp)
	bb = gtk.HBox(False, 0)
	gui.set_data("baudHBox", bb)
	text = gtk.Entry()
	text.connect("activate", serSendText)
	hbox.pack_start(bb, False, False, 3)
	hbox.pack_start(text, True, True, 3)
	hbox.pack_start(s, False, False, 3)
	hbox.pack_start(c, False, False, 3)
	vbox = gtk.VBox(False, 0)
	vbox.pack_start(hbox, False, False, 3)
	vbox.pack_start(sw, True, True, 3)
	vbox.show_all()
	createBaudCombo(None, config.cur_serial_port)
	return (vbox, tmp)

buttons = [
		("compile", "compile.png", compile),
		("stop", "stop.png", stop),

		("open", "open.png", copen),
		("new", "new.png", cnew),

		("save", "save.png", None),
		("upload", "upload.png", None),
		("serial", "serial.png", None)
	]

def createBaudCombo(w, port):
	hb = gui.get_data("baudHBox")
	if hb:
		bw = gui.get_data("baudWidget")
		if bw: bw.destroy()
		b = gtk.combo_box_new_text()
		[b.append_text(i+" baud") for i in ser.getBaudrates()]
		b.connect("changed", setBaud)
		b.set_active(ser.getBaudrates().index(config.serial_baud_rate))
		hb.pack_start(b, False, False, 3)
		gui.set_data("baudWidget", b)
		hb.show_all()

def selectBoard(w, id):
	b.setBoard(id)

def setSerial(w, id):
	createBaudCombo(w, id)
	try:
		config.cur_serial_port = id
		ser.resetBoard()
		ser.serial.close()
		ser.serial.port = id
		ser.serial.open()
		client.set_string(serial_port_key, id)
	except: None

def getCurrentPage():
	return nb.get_nth_page(nb.get_current_page())

def getCurrentView():
	p = nb.get_nth_page(nb.get_current_page())
	return p.get_data("view")


def getGui():
	return gui

def cb_configure_event(widget, event):
	client.set_int(MW, event.width)
	client.set_int(MH, event.height)

def run():
	try:
		global gui
		global mainwin
		global sb2
		global ser
		global id
		global nb
		global tw
		global sctw
		global sb
		global sertime
		global vbox
		global con
		global scon
		global p
		global b
		global client
		client = gconf.client_get_default()
		id = misc.makeWorkdir()
		ser = serialio.sconsole()
		p = prefs.preferences()
		sertime = None
		gui = gtk.Builder()
		try:
			path = os.path.join(os.getcwd(), "ui", "main.ui")
			if os.path.exists(path):
				gui.add_from_file(path)
			else: raise
		except:
			try:
				path = os.path.join(sys.prefix, "share", "gnoduino", "ui", "main.ui")
				if os.path.exists(path):
					gui.add_from_file(path)
			except Exception,e:
				print(e)
				raise SystemExit(_("Cannot load ui file"))
		mainwin = gui.get_object("top_win")
		mainwin.set_default_size(client.get_int(MW), client.get_int(MH))
		mainwin.connect("configure-event", cb_configure_event)
		vbox = gui.get_object("vpan")
		sb = gui.get_object("statusbar1")
		sb2 = gui.get_object("statusbar2")
		config.cur_font = p.getValue("editor.font")
		config.build_verbose = p.getValue("build.verbose")
		config.user_library = client.get_string(user_library_key)
		menu(gui)
		"""build menus"""
		sub = gtk.Menu()
		b = board.Board()
		maingroup = gtk.RadioMenuItem(None, None)
		for i in b.getBoards():
			menuItem = gtk.RadioMenuItem(maingroup, i['desc'])
			if i['id'] == b.getBoard() + 1:
				menuItem.set_active(True)
			menuItem.connect('toggled', selectBoard, i['id'])
			sub.append(menuItem)
		gui.get_object("board").set_submenu(sub)

		sub = gtk.Menu()
		maingroup = gtk.RadioMenuItem(None, None)
		config.serial_port = client.get_string(serial_port_key)
		for i in ser.scan():
			menuItem = gtk.RadioMenuItem(maingroup, i)
			if config.serial_port: defport = config.serial_port
			else: defport = p.getValue("serial.port")
			if defport:
				if i == defport:
					menuItem.set_active(True)
					if config.cur_serial_port == -1:
						config.cur_serial_port = i
					setSerial(None, i)
			else:
				if i == "/dev/ttyS0":
					if config.cur_serial_port == -1:
						config.cur_serial_port = i
					menuItem.set_active(True)
					setSerial(None, i)
			menuItem.connect('activate', setSerial, i)
			sub.append(menuItem)

		if config.serial_baud_rate == -1:
			config.serial_baud_rate = client.get_string(serial_baud_rate_key)
			if config.serial_baud_rate: defbaud = config.serial_baud_rate
			else: defbaud = p.getValue("serial.debug_rate")
			config.serial_baud_rate = defbaud

		gui.get_object("serial_port").set_submenu(sub)

		sub = gtk.Menu()
		pgm = programmer.Programmer()
		for i in pgm.getProgrammers():
			menuItem = gtk.MenuItem(i['desc'])
			menuItem.connect('activate', burnBootloader, i['id'])
			sub.append(menuItem)
		gui.get_object("burn").set_submenu(sub)

		nb = gtk.Notebook()
		nb.connect("switch-page", setupPage)
		sv = createPage(nb)
		vbox.add(nb)

		(con, tw) = createCon()
		(scon,sctw) = createScon()
		vbox.add(con)

		mainwin.set_focus(sv)
		mainwin.show_all()
		mainwin.set_title("Arduino")
		mainwin.connect("destroy", quit)
		gui.get_object("ser_monitor").connect("activate", cserial, sertime, sctw)
		gui.get_object("serial").connect("clicked", cserial, sertime, sctw)
		gui.get_object("upload").connect("clicked", upload, ser)
		for i in buttons:
			w = gtk.Image()
			try:
				path = os.path.join(os.getcwd(), "pixmaps", i[1])
				if os.path.exists(path):
					w.set_from_file(path)
				else: raise
			except:
				try:
					path = os.path.join(sys.prefix, 'share', 'gnoduino', "pixmaps", i[1])
					if os.path.exists(path):
						w.set_from_file(path)
					else: raise
				except Exception,e:
					print(e)
					raise SystemExit(_("Cannot load pixmap files"))
			o = gui.get_object(i[0])
			o.set_icon_widget(w)
			o.show_all()
			if i[2] != None:
				o.connect("clicked", i[2])
		gtk.main()
	except KeyboardInterrupt:
		print "\nExit on user cancel."
		sys.exit(1)
