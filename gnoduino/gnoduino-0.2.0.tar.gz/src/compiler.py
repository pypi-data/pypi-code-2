# Arduino python implementation
# Copyright (C) 2010  Lucian Langa <cooly@gnome.eu.org>
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
#

import os
import glob
import gtk
import logging
import select
import subprocess
import sys
import time
import tempfile
import gettext
import hashlib
#gettext.bindtextdomain('myapplication', '/path/to/my/language/directory')
#gettext.textdomain('myapplication')
_ = gettext.gettext

LOG_FILENAME = 'arduino.out'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
_debug = 1

import board
import config
import misc
import prefs
import preproc

#output = output buffer
#notify = notification bar
cobj = [
	"wiring_digital.c",
	"wiring_shift.c",
	"wiring_analog.c",
	"wiring_pulse.c",
#	"wiring_serial.c",
	"pins_arduino.c",
	"WInterrupts.c",
	"wiring.c"
	]

cppobj = [
	"WMath.cpp",
	"HardwareSerial.cpp",
	"Print.cpp",
	"main.cpp",
	"Tone.cpp"
	]

defc = [
	"/usr/bin/avr-gcc",
	"-c",
#	"-w",
	"-g",
	"-Os",
	"-ffunction-sections",
	"-fdata-sections",
	]

defcpp = [
	"/usr/bin/avr-g++",
	"-c",
	"-w",
	"-g",
	"-Os",
	"-fno-exceptions",
	"-ffunction-sections",
	"-fdata-sections",
	]

defar = [
	"/usr/bin/avr-ar",
	"rcs"
	]

link = [
	"/usr/bin/avr-gcc",
	"-Os",
	"-Wl,--gc-sections",
	]

eep = [
	"/usr/bin/avr-objcopy",
	"-O",
	"ihex",
	"-j .eeprom",
	"--set-section-flags=.eeprom=alloc,load",
	"--no-change-warnings",
	"--change-section-lma",
	".eeprom=0"
	]
hex = [
	"/usr/bin/avr-objcopy",
	"-O",
	"ihex",
	"-R .eeprom"
	]

def stripOut(sout, pre):
	sout = sout.replace(pre+":", '').split(" ", 1)
	if len(sout) >= 2: return sout[1]
	else: return sout

def compile(tw, id, output, notify):
	buf =  tw.get_buffer()
	cont = buf.get_text(buf.get_start_iter(), buf.get_end_iter())
	if cont is "": return -1
	context = notify.get_context_id("main")
	notify.pop(context)
	notify.push(context, _("Compilling..."))
	if _debug: sys.stderr.write('start compile\n')
	misc.clearConsole(output)
	tmpdir = id
	tempobj = tempfile.mktemp("", "Tempobj", id)
	global p
	p = prefs.preferences()
	b = board.Board()
	#compile inter c objects
	try:
		"""preproces pde"""
		(pre_file, lines) = preproc.addHeaders(id, buf)
		"""compile C targets"""
		if p.getValue("build.verbose"): sys.stderr.write('process C targets\n')
		for i in cobj:
			compline=[j for j in defc]
			compline.append("-mmcu="+b.getBoardMCU(b.getBoard()))
			compline.append("-DF_CPU="+b.getBoardFCPU(b.getBoard()))
			compline.append("-I"+misc.getArduinoPath())
			compline.append(os.path.join(misc.getArduinoPath(), i))
			compline.append("-o"+id+"/"+i+".o")
			if p.getValue("build.verbose"): sys.stderr.write(' '.join(compline)+"\n")
			(run, sout) = misc.runProg(compline)
			if p.getValue("build.verbose"): sys.stderr.write(sout+"\n")
			if run == False:
				misc.printError(notify, output, stripOut(sout, pre_file))
				raise
		"""compile C++ targets"""
		if _debug: sys.stderr.write('process C++ targets\n')
		for i in cppobj:
			compline = [j for j in defcpp]
			compline.append("-mmcu="+b.getBoardMCU(b.getBoard()))
			compline.append("-DF_CPU="+b.getBoardFCPU(b.getBoard()))
			compline.append("-I" + misc.getArduinoPath())
			compline.append(os.path.join(misc.getArduinoPath(), i))
			compline.append("-o"+id+"/"+i+".o")
			if p.getValue("build.verbose"): sys.stderr.write(' '.join(compline)+"\n")
			(run, sout) = misc.runProg(compline)
			if p.getValue("build.verbose"): sys.stderr.write(sout+"\n")
			if run == False:
				misc.printError(notify, output, sout)
				raise
		"""generate archive objects"""
		if _debug: sys.stderr.write('gen ar obj\n')
		for i in cobj+cppobj:
			compline = [j for j in defar]
			compline.append(id+"/core.a")
			compline.append(id+"/"+i+".o")
			if p.getValue("build.verbose"): sys.stderr.write(' '.join(compline)+"\n")
			(run, sout) = misc.runProg(compline)
			if p.getValue("build.verbose"): sys.stderr.write(sout+"\n")
			if run == False:
				misc.printError(notify, output, stripOut(sout, pre_file))
				raise
		"""precompile pde"""
		if _debug: sys.stderr.write('pde compile\n')
		if _debug: sys.stderr.write('-----------\n')
		compline=[j for j in defcpp]
		compline.append("-mmcu="+b.getBoardMCU(b.getBoard()))
		compline.append("-DF_CPU="+b.getBoardFCPU(b.getBoard()))
		compline.append("-I" + misc.getArduinoPath())
		compline.extend(preproc.generateCFlags(id, cont))
		compline.extend(["-I" + os.path.join(i, "utility") for i in preproc.generateLibs(id, buf)])
		compline.append(pre_file)
		compline.append("-o"+pre_file+".o")
		if p.getValue("build.verbose"): sys.stderr.write(' '.join(compline)+"\n")
		(run, sout) = misc.runProg(compline)
		if p.getValue("build.verbose"): sys.stderr.write(sout+"\n")
		if run == False:
			misc.printError(notify, output, stripOut(sout, pre_file))
			moveCursor(tw, int(getErrorLine(sout, lines)))
			raise NameError('compile-error')

		"""compile all objects"""
		if _debug: sys.stderr.write('compile objects\n')
		if _debug: sys.stderr.write('---------------\n')
		compline = [i for i in link]
		compline.append("-mmcu="+b.getBoardMCU(b.getBoard()))
		compline.append("-o"+tempobj+".elf")
		compline.append(pre_file+".o")
		tmplibs = []
		for i in preproc.generateLibs(id, buf):
			tmplibs.extend(validateLib(os.path.basename(i), tempobj, output, notify))
		compline.extend(list(set(tmplibs)))
		compline.extend(["-I" + os.path.join(i, "utility") for i in preproc.generateLibs(id, buf)])
		compline.append(id+"/core.a")
		compline.append("-L"+id)
		compline.append("-lm")
		if p.getValue("build.verbose"): sys.stderr.write(' '.join(compline)+"\n")
		(run, sout) = misc.runProg(compline)
		if p.getValue("build.verbose"): sys.stderr.write(sout+"\n")
		if run == False:
			misc.printError(notify, output, stripOut(sout, pre_file))
			raise NameError('linking-error')
		compline=[i for i in eep]
		compline.append(tempobj+".elf")
		compline.append(tempobj+".eep")
		if p.getValue("build.verbose"): sys.stderr.write(' '.join(compline)+"\n")
		(run, sout) = misc.runProg(compline)
		if p.getValue("build.verbose"): sys.stderr.write(sout+"\n")
		if run == False:
			misc.printError(notify, output, stripOut(sout, pre_file))
			raise NameError('obj-copy')
		compline=[i for i in hex]
		compline.append(tempobj+".elf")
		compline.append(tempobj+".hex")
		if p.getValue("build.verbose"): sys.stderr.write(' '.join(compline)+"\n")
		(run, sout) = misc.runProg(compline)
		if p.getValue("build.verbose"): sys.stderr.write(sout+"\n")
		if run == False:
			misc.printError(notify, output, stripOut(sout, pre_file))
			raise NameError('obj-copy')
		size = computeSize(tempobj+".hex")
		notify.pop(context)
		notify.push(context, _("Done compilling."))
		if _debug: sys.stderr.write("compile done.\n")

		misc.printMessage(output, \
			_("Binary sketch size: %s bytes (of a %s bytes maximum)") % (size, b.getBoardMemory(b.getBoard())))
	except StandardError as e:
		print "Error: %s" % e
	except:
		print "Error compiling. Op aborted!"
	return tempobj

"""checks whether library exists (it has been compiled and tries to compile it otherwise"""
"""@returns a list of compiled objects"""
def validateLib(library, tempobj, output, notify):
	"""compile library also try to compile every cpp under libdir"""
	"""also try to compile utility dir if present"""
	paths = ["", misc.getArduinoPath()]
	if config.user_library != None and config.user_library != -1:
		paths.extend(i.strip() for i in config.user_library.split(';'))
	dirs = ["", "utility"]
	b = board.Board()
	res = []
	fl = []
	for d in dirs:
		for q in paths:
			fl = os.path.join(q, library, d)
			if os.path.exists(fl):
				try:
					for i in glob.glob(os.path.join(fl, "*.c")):
						"""compile library c modules"""
						compline = [j for j in defc]
						compline.append("-mmcu="+b.getBoardMCU(b.getBoard()))
						compline.append("-DF_CPU="+b.getBoardFCPU(b.getBoard()))
						compline.append("-I" + misc.getArduinoPath())
						compline.append("-I" + os.path.join(misc.getArduinoLibsPath(), library, "utility"))
						compline.extend(preproc.generateCFlags(id, open(i).read()))
						compline.append(i)
						compline.append("-o"+os.path.join(os.path.dirname(tempobj), \
							os.path.basename(i.replace(".c", ".o"))))
						if p.getValue("build.verbose"): sys.stderr.write(' '.join(compline)+"\n")
						(run, sout) = misc.runProg(compline)
						if p.getValue("build.verbose"): sys.stderr.write(sout+"\n")
						if run == False:
							misc.printError(notify, output, sout)
							raise NameError('libs compile error')
						res.append(os.path.join(os.path.dirname(tempobj), \
							os.path.basename(i.replace(".c", ".o"))))
				except StandardError as e:
					print "Error: %s" % e
				try:
					for i in glob.glob(os.path.join(fl, "*.cpp")):
						"""compile library cpp modules"""
						compline = [j for j in defcpp]
						compline.append("-mmcu="+b.getBoardMCU(b.getBoard()))
						compline.append("-DF_CPU="+b.getBoardFCPU(b.getBoard()))
						compline.append("-I" + misc.getArduinoPath())
						compline.extend(preproc.generateCFlags(id, open(i).read()))
						compline.append(i)
						compline.append("-I" + os.path.join(misc.getArduinoLibsPath(), library, "utility"))
						compline.append("-o"+os.path.join(os.path.dirname(tempobj), \
							os.path.basename(i.replace(".cpp", ".o"))))
						if p.getValue("build.verbose"): sys.stderr.write(' '.join(compline)+"\n")
						(run, sout) = misc.runProg(compline)
						if p.getValue("build.verbose"): sys.stderr.write(sout+"\n")
						if run == False:
							misc.printError(notify, output, sout)
							raise NameError('libs compile error')
						res.append(os.path.join(os.path.dirname(tempobj), \
							os.path.basename(i.replace(".cpp", ".o"))))
				except StandardError as e:
					print "Error: %s" % e
	return list(set(res))

def getErrorLine(buffer, offset=0):
	try:
		return int(buffer.splitlines()[1].split(":")[1])-offset-3 # substract added lines by preprocesor
	except:
		return int(buffer.splitlines()[0].split(":")[1])-offset-3 # substract added lines by preprocesor

def moveCursor(view, line):
	b = view.get_buffer()
	mark = b.get_insert()
	iter = b.get_iter_at_mark(mark)
	iter.set_line(line);
	b.place_cursor(iter)
	view.scroll_mark_onscreen(mark)

def computeSize(f):
	p = subprocess.Popen(["/usr/bin/avr-size", f],
		stdout = subprocess.PIPE,
		stderr = subprocess.STDOUT,
		stdin = subprocess.PIPE,
		close_fds = True)
	poll = select.poll()
	poll.register(p.stdout, select.POLLIN)
	(sout,serr) = p.communicate()
	return sout.splitlines()[1].split()[3]
