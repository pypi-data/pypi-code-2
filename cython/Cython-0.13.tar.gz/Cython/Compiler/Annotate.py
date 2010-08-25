# Note: Work in progress

import os
import re
import time
import codecs
from StringIO import StringIO

import Version
from Code import CCodeWriter
from Cython import Utils

# need one-characters subsitutions (for now) so offsets aren't off
special_chars = [(u'<', u'\xF0', u'&lt;'),
                 (u'>', u'\xF1', u'&gt;'), 
                 (u'&', u'\xF2', u'&amp;')]
                 
line_pos_comment = re.compile(r'/\*.*?<<<<<<<<<<<<<<.*?\*/\n*', re.DOTALL)

class AnnotationCCodeWriter(CCodeWriter):

    def __init__(self, create_from=None, buffer=None, copy_formatting=True):
        CCodeWriter.__init__(self, create_from, buffer, copy_formatting=True)
        if create_from is None:
            self.annotation_buffer = StringIO()
            self.annotations = []
            self.last_pos = None
            self.code = {}
        else:
            # When creating an insertion point, keep references to the same database
            self.annotation_buffer = create_from.annotation_buffer
            self.annotations = create_from.annotations
            self.code = create_from.code
            self.last_pos = create_from.last_pos
    
    def create_new(self, create_from, buffer, copy_formatting):
        return AnnotationCCodeWriter(create_from, buffer, copy_formatting)

    def write(self, s):
        CCodeWriter.write(self, s)
        self.annotation_buffer.write(s)
        
    def mark_pos(self, pos):
        if pos is not None:
            CCodeWriter.mark_pos(self, pos)
        if self.last_pos:
            pos_code = self.code.setdefault(self.last_pos[0].get_description(),{})
            code = pos_code.get(self.last_pos[1], "")
            pos_code[self.last_pos[1]] = code + self.annotation_buffer.getvalue()
        self.annotation_buffer = StringIO()
        self.last_pos = pos

    def annotate(self, pos, item):
        self.annotations.append((pos, item))
        
    def save_annotation(self, source_filename, target_filename):
        self.mark_pos(None)
        f = Utils.open_source_file(source_filename)
        lines = f.readlines()
        for k in range(len(lines)):
            line = lines[k]
            for c, cc, html in special_chars:
                line = line.replace(c, cc)
            lines[k] = line
        f.close()
        all = []
        if False:
            for pos, item in self.annotations:
                if pos[0].filename == source_filename:
                    start = item.start()
                    size, end = item.end()
                    if size:
                        all.append((pos, start))
                        all.append(((source_filename, pos[1], pos[2]+size), end))
                    else:
                        all.append((pos, start+end))
                
        all.sort()
        all.reverse()
        for pos, item in all:
            _, line_no, col = pos
            line_no -= 1
            col += 1
            line = lines[line_no]
            lines[line_no] = line[:col] + item + line[col:]
        
        html_filename = os.path.splitext(target_filename)[0] + ".html"
        f = codecs.open(html_filename, "w", encoding="UTF-8")
        f.write(u'<html>\n')
        f.write(u"""
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style type="text/css">

body { font-family: courier; font-size: 12; }

.code  { font-size: 9; color: #444444; display: none; margin-left: 20px; }
.py_c_api  { color: red; }
.py_macro_api  { color: #FF7000; }
.pyx_c_api  { color: #FF3000; }
.pyx_macro_api  { color: #FF7000; }
.refnanny  { color: #FFA000; }

.error_goto  { color: #FFA000; }

.tag  {  }

.coerce  { color: #008000; border: 1px dotted #008000 }

.py_attr { color: #FF0000; font-weight: bold; }
.c_attr  { color: #0000FF; }

.py_call { color: #FF0000; font-weight: bold; }
.c_call  { color: #0000FF; }

.line { margin: 0em }

</style>
<script>
function toggleDiv(id) {
    theDiv = document.getElementById(id);
    if (theDiv.style.display == 'none') theDiv.style.display = 'block';
    else theDiv.style.display = 'none';
}
</script>
</head>
        """)
        f.write(u'<body>\n')
        f.write(u'<p>Generated by Cython %s on %s\n' % (Version.version, time.asctime()))
        c_file = Utils.decode_filename(os.path.basename(target_filename))
        f.write(u'<p>Raw output: <a href="%s">%s</a>\n' % (c_file, c_file))
        k = 0
        
        py_c_api = re.compile(u'(Py[A-Z][a-z]+_[A-Z][a-z][A-Za-z_]+)\(')
        py_marco_api = re.compile(u'(Py[A-Z][a-z]+_[A-Z][A-Z_]+)\(')
        pyx_c_api = re.compile(u'(__Pyx_[A-Z][a-z_][A-Za-z_]+)\(')
        pyx_macro_api = re.compile(u'(__Pyx_[A-Z][A-Z_]+)\(')
        error_goto = re.compile(ur'((; *if .*)? \{__pyx_filename = .*goto __pyx_L\w+;\})')
        refnanny = re.compile(u'(__Pyx_X?(GOT|GIVE)REF|__Pyx_RefNanny[A-Za-z]+)')
        
        code_source_file = self.code[source_filename]
        for line in lines:

            k += 1
            try:
                code = code_source_file[k]
            except KeyError:
                code = ''
            
            code = code.replace('<', '<code><</code>')
            
            code, py_c_api_calls = py_c_api.subn(ur"<span class='py_c_api'>\1</span>(", code)
            code, pyx_c_api_calls = pyx_c_api.subn(ur"<span class='pyx_c_api'>\1</span>(", code)
            code, py_macro_api_calls = py_marco_api.subn(ur"<span class='py_macro_api'>\1</span>(", code)
            code, pyx_macro_api_calls = pyx_macro_api.subn(ur"<span class='pyx_macro_api'>\1</span>(", code)
            code, refnanny_calls = refnanny.subn(ur"<span class='refnanny'>\1</span>", code)
            code, error_goto_calls = error_goto.subn(ur"<span class='error_goto'>\1</span>", code)
            
            code = code.replace(u"<span class='error_goto'>;", u";<span class='error_goto'>")
            
            score = 5*py_c_api_calls + 2*pyx_c_api_calls + py_macro_api_calls + pyx_macro_api_calls - refnanny_calls
            color = u"FFFF%02x" % int(255/(1+score/10.0))
            f.write(u"<pre class='line' style='background-color: #%s' onclick='toggleDiv(\"line%s\")'>" % (color, k))

            f.write(u" %d: " % k)
            for c, cc, html in special_chars:
                line = line.replace(cc, html)
            f.write(line.rstrip())
                
            f.write(u'</pre>\n')
            code = re.sub(line_pos_comment, '', code) # inline annotations are redundant
            f.write(u"<pre id='line%s' class='code' style='background-color: #%s'>%s</pre>" % (k, color, code))
        f.write(u'</body></html>\n')
        f.close()
        

# TODO: make this cleaner
def escape(raw_string):
    raw_string = raw_string.replace(u"\'", ur"&#146;")
    raw_string = raw_string.replace(u'\"', ur'&quot;')
    raw_string = raw_string.replace(u'\n', ur'<br>\n')
    raw_string = raw_string.replace(u'\t', ur'\t')
    return raw_string


class AnnotationItem(object):
    
    def __init__(self, style, text, tag="", size=0):
        self.style = style
        self.text = text
        self.tag = tag
        self.size = size
        
    def start(self):
        return u"<span class='tag %s' title='%s'>%s" % (self.style, self.text, self.tag)
    
    def end(self):
        return self.size, u"</span>"
