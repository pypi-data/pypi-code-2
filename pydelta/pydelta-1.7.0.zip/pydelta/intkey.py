# -*- coding: utf-8 -*-
## Thomas Kluyver, March 2010.
## With thanks to Eric Zurcher for providing documentation.
"""
This module is capable of reading data from the binary intkey file formats.
It returns a pydelta.Delta object, which can be used like a loaded DELTA file.

Usage example:
from pydelta import intkey

# N.B. Downloading and parsing the data may take a few seconds.
grassgen = intkey.webload("http://delta-intkey.com/grass/webstart.ink")
print len(grassgen.chars), "Characters:"
for char in grassgen.chars:
	print char.feature, len(char.states)

print "\\n",len(items), "Items:
for item in grassgen.items:
	print char.name,
	if 9 in char.attributes:
		print char.attributes[9].replace("1","annual").replace("2","perennial")
	else:
		print
"""

import pydelta
import struct
# Lazy importing: libraries for webload will only be imported if used
#    (urllib, tempfile, zipfile).

class IKCharDescr(pydelta.CharDescr):
	"""A character description for use with IntKey. Like standard DELTA 
character descriptions, with .min and .max (for integer numerics)"""
	def __init__(self):
		super(IKCharDescr, self).__init__()
		self.min = None
		self.max = None

CT = {1:'UM', 2:'OM', 3:'IN', 4:'RN', 5:'TE'}
# These will allow us to extract individual bit values later on:
pot = [2**x for x in range(8)]
bitvalues = {}
for x in range(256):
	bitvalues[chr(x)] = [(x & y) != 0 for y in pot]

def _read_records(binfile):
	"""Reads the file in 128-byte chunks. Returns a list with a 1-based index."""
	records = [None] #First item so we get the 1-based index Intkey uses
	a = binfile.read(128)
	while a:
		records.append(a)
		a = binfile.read(128)
	return records
	
def _get_num_array(records, start, N, fmt = "l"):
	"""Returns an array of #N integers from record #start"""
	needed = int(N/32)+1
	padding = (32- (N % 32))*4
	data = "".join(records[start:start+needed])
	return struct.unpack("<"+str(N)+fmt+ str(padding)+"x",data)
	
def _get_strings(records, start, lengths):
	"""Returns a tuple of strings of the given lengths, reading from the record at # start"""
	#Build unpack format string
	unpackfmt = "<"
	for length in lengths:
		unpackfmt += str(length)+"s"
	all_str_len = struct.calcsize(unpackfmt)
	needed = int(all_str_len/128)+1
	padding = 128 - (all_str_len % 128)
	unpackfmt += str(padding)+"x"
	data = "".join(records[start:start+needed])
	return struct.unpack(unpackfmt, data)
	
def _get_strings_via_lengths(records, start,N):
	"""Starting at a series of integers to be interpreted as length, returns
the strings they describe."""
	lengths = _get_num_array(records, start, N)
	start += int(N/32)
	if N % 32: start += 1
	
	return _get_strings(records, start, lengths)
	
def _get_strings_via_offsets(records, start, N):
	"""Starting at a series of N+1 integers to be interpreted as offsets from
the start position of the string data, return the N strings they describe."""
	N += 1
	offsets = _get_num_array(records, start, N)
	previous = offsets[0]
	lengths = []
	for offset in offsets[1:]:
		lengths.append(offset - previous)
		previous = offset
	start += int(N/32)
	if N % 32: start += 1
	
	return _get_strings(records, start, lengths)
	
def _get_bit_array(records, start, N):
	"""Unpacks an array of bits, returning a list of N Booleans."""
	# struct doesn't let us unpack individual bits, so we do one character
	#     at a time, and use a prebuilt dictionary of the bit-values for these.
	numchrs = int(N/8) + 1
	needed = int(numchrs/128) + 1
	padding1 = 8 - (N % 8) #Padding within the final char
	padding2 = 128 - (numchrs % 128) #Padding to the end of the record
	data = "".join(records[start:start+needed])
	chrdata = struct.unpack("<"+str(numchrs)+"c"+str(padding2)+"x", data)
	
	values = []
	for character in chrdata:
		values += bitvalues[character]

	return values[:-padding1] #Trim the last few values off.
	

def load(charsfn, itemsfn, datazip=None):
	"""
Load data from the binary intkey chars and items files. If datazip is 
specified (as a zipfile.ZipFile), the file names refer to files within that.
Otherwise, the filenames will be opened as regular files.
	"""
	# Set up structure.
	charlist = pydelta.DeltaCharList(charsfn)
	itemlist = pydelta.DeltaItemList(itemsfn)
	
	# Get raw data from files for random access
	if datazip:
		chard = _read_records(datazip.open(charsfn))
		itemd = _read_records(datazip.open(itemsfn))
	else:
		chard = _read_records(open(charsfn, "rb"))
		itemd = _read_records(open(itemsfn, "rb"))
	
	# Get header information from both files.
	NC, maxDes, rnCdes, rnStat, rnCnotes, rnCnotesGrp, rnCnotesFmt1, rnCnotesFmt2,\
	rnCimages, rnStartupImages, rnCkeyImages, rnTKeyImages, rnHeading, rnSubHeading,\
	rnValidationString, rnCharacterMask, rnOrWord, rnCDCheck, rnFont, fnItemSubHeadings\
		= struct.unpack("<20l48x",chard[1])
		
	NI,NC1,MS,Maxdat,Lrec,rnTnam,rnSpec,rnMinmax,Ldep,rnCdep,Linvdep,rnInvdep,rnCdat,\
	Numbnd,MaxKstat,MajorVer,rnKbnd,Maxint,Maxtxt1,Maxtxt2,MinorVer,dummy,rnCimages,\
	rnTimages,enableDeltaOutput,chineseFormat,rnCsynon,rnOmitOr,rnNext = \
		struct.unpack("<29l12x",itemd[1])
	assert NC1 == NC #Num chars is specified in both files, and should be the same.
	rnUseCc, rnTlink, rnOmitPeriod, rnnewParagraph, rnNonAutoCc,rnTlinks1 = \
		struct.unpack("<6l104x",itemd[2])
		
	# Pull out the record numbers of the character descriptions.
	rnsCdes = _get_num_array(chard, rnCdes, NC)
	NumsStates = _get_num_array(chard, rnStat, NC)
	rnsCnotes = _get_num_array(chard, rnCnotes, NC)
	#Character types--no idea why they are stored in the items data file.
	CTypes = _get_num_array(itemd, rnSpec, NC)
	#Mins and maxes (can be entirely missing, somehow, according to the spec).
	if rnMinmax:
		CMins = _get_num_array(itemd, rnMinmax, NC)
		start = rnMinmax + int(NC/32)
		if NC % 32: start += 1
		CMaxs = _get_num_array(itemd, start, NC)
	else:
		CMins = CMaxs = [0] * NC
	Cindex = zip(rnsCdes, rnsCnotes, NumsStates, CTypes, CMins, CMaxs)
	
	# Extract the character information and put it into the CharList.
	for rnDes, rnNote, NS, CType, CMin, CMax in Cindex:
		descriptions = _get_strings_via_lengths(chard, rnDes, NS+1)
		
		newchar = IKCharDescr()
		newchar.feature = descriptions[0]
		
		# This is confusing. CType is the integer as stored in intkey
		#  files. This is converted to a text code, e.g. 'TE' or 'UM',
		#  then to Freedelta's integer representation.
		CType = abs(CType) #No idea why they can be negative, but that's the spec.
		newchar.char_type = pydelta.CT[CT[CType]]
		if CT[CType] == 'TE':
			assert NS == 0, "Text characters should not have states"
		elif CT[CType] == 'RN' or CT[CType] == 'IN':
			assert NS < 2, "Numeric characters may only have one 'state' (their unit)"
			if NS == 1:
				newchar.unit = descriptions[1]
			if CT[CType] == 'IN':
				newchar.min = CMin
				newchar.max = CMax
		else:
			assert NS > 0, "Multistate characters should have at least one state."
			newchar.states = pydelta.DeltaList(descriptions[1:])
		
		# Add character note (if blank, record number will be 0)
		if rnNote:
			newchar.notes = _get_strings_via_lengths(chard, rnNote,1)[0]
		
		charlist.append(newchar)
		
	# Extract item information and put it in the ItemList
	ItemNames = _get_strings_via_offsets(itemd, rnTnam, NI)
	for Name in ItemNames:
		newitem = pydelta.ItemDescr()
		newitem.charlist = charlist
		newitem.name = Name
		itemlist.append(newitem)
	
	# Character state information:
	rnsCdata = _get_num_array(itemd, rnCdat, NC)
	for i, rnCdata in enumerate(rnsCdata):
		# Text character
		if charlist[i+1].char_type == pydelta.CT['TE']:
			inapplic = _get_bit_array(itemd, rnCdata, NI)
			start = rnCdata + int((NI/8)/128)
			if NI % (128*8): start += 1
			
			values = zip(inapplic, _get_strings_via_offsets(itemd, start, NI))
			
			for j, (inapplic, value) in enumerate(values):
				if value and not inapplic:
					itemlist[j+1].attributes[i+1] = value
					
		# Multistate data.
		elif (charlist[i+1].char_type == pydelta.CT['UM']) or \
				(charlist[i+1].char_type == pydelta.CT['OM']):
				
			NS = len(charlist[i+1].states)
			nbits = (NS + 1) * NI
			allvalues = zip(*[iter(_get_bit_array(itemd, rnCdata, nbits))] *(NS+1))
			
			for item in itemlist:
				values = allvalues.pop(0)
				if values[-1]:
					continue
				states = []
				for j, value in enumerate(values[:-1]):
					if value:
						states.append(str(j+1))
				item.attributes[i+1] = "/".join(states)
				
		# Real numeric data.
		elif charlist[i+1].char_type == pydelta.CT['RN']:
			inapplicability = _get_bit_array(itemd, rnCdata, NI)
			start = rnCdata + NI/(8*128)
			if NI % (8*128): start += 1
			values = zip(*[iter(_get_num_array(itemd, start, NI*2, fmt="f"))]*2)
			for item in itemlist:
				inapplicable = inapplicability.pop(0)
				min, max = values.pop(0)
				if inapplicable or min > max:
					continue
				item.attributes[i+1] = str(min) +"-"+ str(max)
	
		# Integer numeric data.
		elif charlist[i+1].char_type == pydelta.CT['IN']:
			min = charlist[i+1].min
			NS = charlist[i+1].max - min
			
			assert NS > 0, "Integer character (%i) without min/max" % i+1
			nbits = (NS + 4)  * NI #Spec says +3, but file seems to disagree.
			statedata = zip(*[iter(_get_bit_array(itemd, rnCdata, nbits))] *(NS+4))
			for item in itemlist:
				itemstate = statedata.pop(0)
				# Is it inapplicable?
				if itemstate[-1]:
					continue
				valuestr = ""
				if itemstate[0]:
					valuestr += "..."
				inrange = False
				rangestart = 0
				for value, on in enumerate(itemstate[1:-2]):
					if inrange and (not on):
						inrange = False
						if value > rangestart+1:
							valuestr += "-"+str(value+min-1)
					elif (not inrange) and on:
						valuestr += " " + str(value+min)
						rangestart = value
						inrange = True
				
				if inrange: #Range went up to maximum.
					valuestr += "-"+str(value+min)
				if itemstate[-2]: # "And above" bit.
					valuestr += "..."
				item.attributes[i+1] = valuestr
		
	return pydelta.Delta(charlist, itemlist)
	
def webload(inkfileURL):
	"""Load intkey data from the web, starting with a .ink file which
describes where to get more data.
	"""
	if inkfileURL.startswith("http://"):
		import urllib
		inkfile = urllib.urlopen(inkfileURL)
	else:
		inkfile = open(inkfileURL, "r")
	metadata = {}
	for line in inkfile:
		if line.strip().startswith(";"):
			continue
		name, dummy, value = line.partition("=")
		metadata[name.strip().lower()] = value.strip()
	inkfile.close()
	
	if metadata['datafile'].startswith("http://"):
		import urllib, tempfile
		datafile = tempfile.TemporaryFile()
		datafile.write(urllib.urlopen(metadata['datafile']).read())
	else:
		datafile = open(metadata['datafile'],"rb")
	import zipfile
	datazip = zipfile.ZipFile(datafile)
	initfile = datazip.open(metadata['initializationfile'], "rU")
	for line in initfile:
		if line.find("FILE TAXA") != -1:
			itemfilename = line.partition("FILE TAXA")[2].strip()
		elif line.find("FILE CHAR") != -1:
			charfilename = line.partition("FILE CHAR")[2].strip()
	
	return load(charfilename, itemfilename, datazip=datazip)
		
if __name__ == "__main__":
	eg = load("grassgen/ichars","grassgen/iitems")
