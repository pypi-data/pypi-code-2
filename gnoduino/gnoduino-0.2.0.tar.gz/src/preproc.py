
# Arduino python implementation
# Copyright (C) 2010  Lucian Langa
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import config
import prefs
import re
import os
import tempfile
import misc

MAIN = "hardware/arduino/cores/arduino/main.cpp"

"""Returns the index of the first character that's not whitespace, a comment
or a pre-processor directive."""
def firstStatement(instr):
	m = re.match(r"""\s+|
		/\*[^*]*(?:\*(?!/)[^*]*)*\*/
		|\s+|
		(//.*\n)+"""
		, instr, re.VERBOSE)
	if not m: return 0
	return m.end(0)

def findPrototype(instr):
	res = ""
	m = re.findall(r"^\w+\s+\w+\([^)]*\)[\s+/*\w*\s+]*{", instr, re.M)
	for z in m:
		q = re.findall("\w+\s+\w+\([^)]*\)", z)
		res = res + q[0]+";\n";
	return res

def findIncludes(instr, local=False):
	res = ""
	m = re.findall(r"^#include\s+[\w+\".<>\-]+", instr, re.M)
	l = [z.split()[1].strip('<>"') for z in m]
	my = []
	for z in l:
		if os.path.exists(os.path.join(misc.getArduinoLibsPath(), z.strip(".h"))):
			my.append(os.path.join(misc.getArduinoLibsPath(), z.strip(".h")))
		if config.user_library:
			for q in config.user_library.split(';'):
				if os.path.exists(os.path.join(q.strip(), z.strip(".h"))):
					my.append(os.path.join(q.strip(), z.strip(".h")))
		if local and os.path.exists(os.path.join(z.strip(".h"))):
			my.append(z.strip(".h"))
	if len(my) == 0:
		for z in l:
			for r, d, f in os.walk(misc.getArduinoLibsPath()):
				if len(f)>0:
					my.extend([r for file in f if file == z])
					for file in f:
						if file == z: break
	return list(set(my))

def makeBufferTempfile(buffer):
	pass


def addHeaders(path, b):
	line = 0
	cont = b.get_text(b.get_start_iter(), b.get_end_iter())
	fs = firstStatement(cont)
	if fs != None:
		proto = findPrototype(cont)
		result = cont[:fs:]+"\n#include \"WProgram.h\"\n" + proto + cont[fs:]+"\n\n"
	else:
		result = "\n#include \"WProgram.h\"\n"+cont+"\n\n"
	of = tempfile.mktemp(".cpp", "", path)
	w = file(of, "w")
	w.write(result)
	w.close()
	for l in proto.splitlines(): line += 1
	return (of, line)

def generateCFlags(path, b):
	#cont = b.get_text(b.get_start_iter(), b.get_end_iter())
	cont = b
	result = []
	result.extend(["-I"+os.path.join(misc.getArduinoLibsPath(), i) for i in findIncludes(cont)])
	result.extend(["-I"+os.path.join(config.user_library, i) for i in findIncludes(cont)])
	result.extend(["-I"+i for i in findIncludes(cont, True)])
	return result

def generateLibs(path, b):
	cont = b.get_text(b.get_start_iter(), b.get_end_iter())
	return [i for i in findIncludes(cont, True)]
