# Contains modified code from the PyYaml project
# (http://pyyaml.org/wiki/PyYAML)
# Original copyright (c) 2006 Kirill Simonov

from yaml.events import SequenceStartEvent, MappingStartEvent, SequenceEndEvent,\
    MappingEndEvent, AliasEvent, ScalarEvent
from yaml.serializer import Serializer
from yaml.emitter import Emitter
from yaml.nodes import ScalarNode, SequenceNode, MappingNode
from yaml.dumper import Dumper
from ygrep.util import printable_len

class YrepEmitter(Emitter):
    
    def process_scalar(self):
        if self.analysis is None:
            self.analysis = self.analyze_scalar(self.event.value)
        if self.style is None:
            self.style = self.choose_scalar_style()
        split = (not self.simple_key_context)
        #if self.analysis.multiline and split    \
        #        and (not self.style or self.style in '\'\"'):
        #    self.write_indent()
        if self.style == '"':
            self.write_double_quoted(self.event.decorated_value, split)
        elif self.style == '\'':
            self.write_single_quoted(self.event.decorated_value, split)
        elif self.style == '>':
            self.write_folded(self.event.decorated_value)
        elif self.style == '|':
            self.write_literal(self.event.decorated_value)
        else:
            self.write_plain(self.event.decorated_value, split)
        self.analysis = None
        self.style = None
        
    def write_double_quoted(self, text, split=True):
        self.write_indicator(u'"', True)
        start = end = 0
        while end <= len(text):
            ch = None
            if end < len(text):
                ch = text[end]
            # Ygrep: Condition added in order to not escape ANSI color sequences
            if (ch is None or ch in u'"\\\x85\u2028\u2029\uFEFF' \
                    or not (u'\x20' <= ch <= u'\x7E'
                        or (self.allow_unicode
                            and (u'\xA0' <= ch <= u'\uD7FF'
                                or u'\uE000' <= ch <= u'\uFFFD')))) \
            and ch != u'\x1B': # Ygrep modification.
                if start < end:
                    data = text[start:end]
                    self.column += printable_len(data)
                    if self.encoding:
                        data = data.encode(self.encoding)
                    self.stream.write(data)
                    start = end
                if ch is not None:
                    if ch in self.ESCAPE_REPLACEMENTS:
                        data = u'\\'+self.ESCAPE_REPLACEMENTS[ch]
                    elif ch <= u'\xFF':
                        data = u'\\x%02X' % ord(ch)
                    elif ch <= u'\uFFFF':
                        data = u'\\u%04X' % ord(ch)
                    else:
                        data = u'\\U%08X' % ord(ch)
                    self.column += printable_len(data)
                    if self.encoding:
                        data = data.encode(self.encoding)
                    self.stream.write(data)
                    start = end+1
            if 0 < end < len(text)-1 and (ch == u' ' or start >= end)   \
                    and self.column+(end-start) > self.best_width and split:
                data = text[start:end]+u'\\'
                if start < end:
                    start = end
                self.column += printable_len(data)
                if self.encoding:
                    data = data.encode(self.encoding)
                self.stream.write(data)
                self.write_indent()
                self.whitespace = False
                self.indention = False
                if text[start] == u' ':
                    data = u'\\'
                    self.column += printable_len(data)
                    if self.encoding:
                        data = data.encode(self.encoding)
                    self.stream.write(data)
            end += 1
        self.write_indicator(u'"', False)        
    
    def write_single_quoted(self, text, split=True):
        self.write_indicator(u'\'', True)
        spaces = False
        breaks = False
        start = end = 0
        while end <= len(text):
            ch = None
            if end < len(text):
                ch = text[end]
            if spaces:
                if ch is None or ch != u' ':
                    if start+1 == end and self.column > self.best_width and split   \
                            and start != 0 and end != len(text):
                        self.write_indent()
                    else:
                        data = text[start:end]
                        self.column += printable_len(data)
                        if self.encoding:
                            data = data.encode(self.encoding)
                        self.stream.write(data)
                    start = end
            elif breaks:
                if ch is None or ch not in u'\n\x85\u2028\u2029':
                    if text[start] == u'\n':
                        self.write_line_break()
                    for br in text[start:end]:
                        if br == u'\n':
                            self.write_line_break()
                        else:
                            self.write_line_break(br)
                    self.write_indent()
                    start = end
            else:
                if ch is None or ch in u' \n\x85\u2028\u2029' or ch == u'\'':
                    if start < end:
                        data = text[start:end]
                        self.column += printable_len(data)
                        if self.encoding:
                            data = data.encode(self.encoding)
                        self.stream.write(data)
                        start = end
            if ch == u'\'':
                data = u'\'\''
                self.column += 2
                if self.encoding:
                    data = data.encode(self.encoding)
                self.stream.write(data)
                start = end + 1
            if ch is not None:
                spaces = (ch == u' ')
                breaks = (ch in u'\n\x85\u2028\u2029')
            end += 1
        self.write_indicator(u'\'', False)

    def write_plain(self, text, split=True):
        if self.root_context:
            self.open_ended = True
        if not text:
            return
        if not self.whitespace:
            data = u' '
            self.column += printable_len(data)
            if self.encoding:
                data = data.encode(self.encoding)
            self.stream.write(data)
        self.whitespace = False
        self.indention = False
        spaces = False
        breaks = False
        start = end = 0
        while end <= len(text):
            ch = None
            if end < len(text):
                ch = text[end]
            if spaces:
                if ch != u' ':
                    if start+1 == end and self.column > self.best_width and split:
                        self.write_indent()
                        self.whitespace = False
                        self.indention = False
                    else:
                        data = text[start:end]
                        self.column += printable_len(data)
                        if self.encoding:
                            data = data.encode(self.encoding)
                        self.stream.write(data)
                    start = end
            elif breaks:
                if ch not in u'\n\x85\u2028\u2029':
                    if text[start] == u'\n':
                        self.write_line_break()
                    for br in text[start:end]:
                        if br == u'\n':
                            self.write_line_break()
                        else:
                            self.write_line_break(br)
                    self.write_indent()
                    self.whitespace = False
                    self.indention = False
                    start = end
            else:
                if ch is None or ch in u' \n\x85\u2028\u2029':
                    data = text[start:end]
                    self.column += printable_len(data)
                    if self.encoding:
                        data = data.encode(self.encoding)
                    self.stream.write(data)
                    start = end
            if ch is not None:
                spaces = (ch == u' ')
                breaks = (ch in u'\n\x85\u2028\u2029')
            end += 1

    def write_literal(self, text):
        hints = self.determine_block_hints(text)
        self.write_indicator(u'|'+hints, True)
        if hints[-1:] == u'+':
            self.open_ended = True
        self.write_line_break()
        breaks = True
        start = end = 0
        while end <= len(text):
            ch = None
            if end < len(text):
                ch = text[end]
            if breaks:
                if ch is None or ch not in u'\n\x85\u2028\u2029':
                    for br in text[start:end]:
                        if br == u'\n':
                            self.write_line_break()
                        else:
                            self.write_line_break(br)
                    if ch is not None:
                        self.write_indent()
                    start = end
            else:
                if ch is None or ch in u'\n\x85\u2028\u2029':
                    data = text[start:end]
                    if self.encoding:
                        data = data.encode(self.encoding)
                    self.stream.write(data)
                    if ch is None:
                        self.write_line_break()
                    start = end
            if ch is not None:
                breaks = (ch in u'\n\x85\u2028\u2029')
            end += 1
            
    def write_folded(self, text):
        hints = self.determine_block_hints(text)
        self.write_indicator(u'>'+hints, True)
        if hints[-1:] == u'+':
            self.open_ended = True
        self.write_line_break()
        leading_space = True
        spaces = False
        breaks = True
        start = end = 0
        while end <= len(text):
            ch = None
            if end < len(text):
                ch = text[end]
            if breaks:
                if ch is None or ch not in u'\n\x85\u2028\u2029':
                    if not leading_space and ch is not None and ch != u' '  \
                            and text[start] == u'\n':
                        self.write_line_break()
                    leading_space = (ch == u' ')
                    for br in text[start:end]:
                        if br == u'\n':
                            self.write_line_break()
                        else:
                            self.write_line_break(br)
                    if ch is not None:
                        self.write_indent()
                    start = end
            elif spaces:
                if ch != u' ':
                    if start+1 == end and self.column > self.best_width:
                        self.write_indent()
                    else:
                        data = text[start:end]
                        # Ygrep modification
                        self.column += printable_len(data)
                        # End Ygrep modification
                        if self.encoding:
                            data = data.encode(self.encoding)
                        self.stream.write(data)
                    start = end
            else:
                if ch is None or ch in u' \n\x85\u2028\u2029':
                    data = text[start:end]
                    
                    self.column += printable_len(data)
                    
                    if self.encoding:
                        data = data.encode(self.encoding)
                    self.stream.write(data)
                    if ch is None:
                        self.write_line_break()
                    start = end
            if ch is not None:
                breaks = (ch in u'\n\x85\u2028\u2029')
                spaces = (ch == u' ')
            end += 1

class YrepScalarEvent(ScalarEvent):
    def __init__(self, anchor, tag, implicit, value, decorated_value, 
            start_mark=None, end_mark=None, style=None, matched=False):
        self.anchor = anchor
        self.tag = tag
        self.implicit = implicit
        self.value = value
        self.decorated_value = decorated_value
        self.start_mark = start_mark
        self.end_mark = end_mark
        self.style = style
        self.matched = matched

class YrepSerializer(Serializer):
    def serialize_node(self, node, parent, index):
        alias = self.anchors[node]
        if node in self.serialized_nodes:
            self.emit(AliasEvent(alias))
        else:
            self.serialized_nodes[node] = True
            self.descend_resolver(parent, index)
            if isinstance(node, ScalarNode):
                detected_tag = self.resolve(ScalarNode, node.value, (True, False))
                default_tag = self.resolve(ScalarNode, node.value, (False, True))
                implicit = (node.tag == detected_tag), (node.tag == default_tag)
                # Start Yrep modificaation
                self.emit(YrepScalarEvent(alias, node.tag, implicit, node.value, node.decorated_value,
                    style=node.style))
                # End Yrep modification
            elif isinstance(node, SequenceNode):
                implicit = (node.tag
                            == self.resolve(SequenceNode, node.value, True))
                self.emit(SequenceStartEvent(alias, node.tag, implicit,
                    flow_style=node.flow_style))
                index = 0
                for item in node.value:
                    self.serialize_node(item, node, index)
                    index += 1
                self.emit(SequenceEndEvent())
            elif isinstance(node, MappingNode):
                implicit = (node.tag
                            == self.resolve(MappingNode, node.value, True))
                self.emit(MappingStartEvent(alias, node.tag, implicit,
                    flow_style=node.flow_style))
                for key, value in node.value:
                    self.serialize_node(key, node, None)
                    self.serialize_node(value, node, key)
                self.emit(MappingEndEvent())
            self.ascend_resolver()

class YrepDumper(Dumper, YrepSerializer, YrepEmitter): pass
