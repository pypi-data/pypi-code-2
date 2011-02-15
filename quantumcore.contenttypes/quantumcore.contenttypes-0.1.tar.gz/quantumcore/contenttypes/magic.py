import pkg_resources
import re
import struct

# [ indent ] ">" start-offset "=" value
# [ "&" mask ] [ "~" word-size ] [ "+" range-length ] "\n"

HEADER_RE = re.compile("\[([0-9]+):([\w\+\/\.]+)\]")

class FormatError(Exception):
    """file has the wrong format"""

class DataReader(object):
    """a helper class for reading the binary magic file properly"""
    
    def __init__(self, data):
	self.data = data
	self.p = 0
	self.l = len(data)

    def consume(self, s="\n"):
	"""return the substring from the current position to the next occurrence of ``s``"""
	i=0
	while True:
	    if self.p+i>=self.l:
		return None # not found, EOF
	    if self.data[self.p+i]==s:
		break
	    i=i+1
	res = self.data[self.p:self.p+i]
	self.p = self.p+i+1
	return res

    def consume_amount(self, length):
	"""consume ``length`` bytes"""
	res = self.data[self.p:self.p+length]
	self.p=self.p+length
	return res

    @property
    def next(self):
	"""return next character"""
	return self.data[self.p]

    @property
    def eof(self):
	"""are we eof?"""
	return self.p>=self.l


class MagicRegistry(object):
    """a registry for mapping magic file contents to mimetypes"""

    def __init__(self):
	"""initialize the MagicRegistry"""

	self.magics = []
        fp = pkg_resources.resource_stream(__name__,"data/sharedmime/magic")
	data = fp.read()
	fp.close()
	self.reader = DataReader(data)


    def read(self):
	"""read the magic file"""

	header = self.reader.consume("\n")
	assert header=="MIME-Magic\x00"

	mimetype = None
	prio = None

	while True:
	    # we always start with a header
	    line = self.reader.consume("\n")
	    if line is None:
		print "stopping"
		break 

	    # extract prio and mimetype from the header
	    header = HEADER_RE.search(line)
	    if header is None and mimetype is None: # we have no active mimetype? something's wrong
		raise FormatError()

	    if header is not None:
		prio, mimetype = header.groups()
		print prio, mimetype

	    # now we continue line by line
	    self.parse_pattern()

    def parse_pattern(self):
	"""parse any patterns we detect until [ is encountered"""

	while True: 
	    # indent available?
	    indent = self.reader.consume(">") 
	    if indent=='':
		indent = 0
	    else:
		indent = int(indent)
	
	    # search for offset (between > and =)
	    offset = int(self.reader.consume("="))

	    value_length = struct.unpack(">h", self.reader.consume_amount(2))[0]
	    value = self.reader.consume_amount(value_length)
	    rest = self.reader.consume()

	    #print "!", indent,offset, value_length, repr(value)

	    if self.reader.eof:
		break

	    if self.reader.next == "[":
		return

"""
00000000  4d 49 4d 45 2d 4d 61 67  69 63 00 0a 5b 39 30 3a  |MIME-Magic..[90:|
00000010  61 70 70 6c 69 63 61 74  69 6f 6e 2f 64 6f 63 62  |application/docb|
00000020  6f 6f 6b 2b 78 6d 6c 5d  0a 3e 30 3d 00 05 3c 3f  |ook+xml].>0=..<?|
00000030  78 6d 6c 0a 31 3e 30 3d  00 19 2d 2f 2f 4f 41 53  |xml.1>0=..-//OAS|
00000040  49 53 2f 2f 44 54 44 20  44 6f 63 42 6f 6f 6b 20  |IS//DTD DocBook |
00000050  58 4d 4c 2b 31 30 31 0a  31 3e 30 3d 00 17 2d 2f  |XML+101.1>0=..-/|
00000060  2f 4b 44 45 2f 2f 44 54  44 20 44 6f 63 42 6f 6f  |/KDE//DTD DocBoo|
00000070  6b 20 58 4d 4c 2b 31 30  31 0a 5b 39 30 3a 61 70  |k XML+101.[90:ap|
00000080  70 6c 69 63 61 74 69 6f  6e 2f 76 6e 64 2e 73 74  |plication/vnd.st|
00000090  61 72 64 69 76 69 73 69  6f 6e 2e 77 72 69 74 65  |ardivision.write|

"""


mr = MagicRegistry()
mr.read()
