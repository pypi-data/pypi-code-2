import re
from termcolor import colored
from StringIO import StringIO
from util import MatchStatus
from yaml import ScalarNode, compose
from yaml.nodes import CollectionNode, SequenceNode, MappingNode
from serializer import YrepDumper

class Ygrep(object):
    
    def __init__(self, pattern, color):
        self.pattern = re.compile(pattern) 
        self.color = color
    
    def do_it(self, istream):
        node = compose(istream)
        self.process_node(node)
        node = self.crop(node)
        if node != None:
            self.decorate(node)
            return self.serialize(node)

    def process_node(self, node, ancestor_matched = False):
        if isinstance(node, CollectionNode):
            return self.process_col(node, ancestor_matched)
        elif isinstance(node, ScalarNode):
            return self.process_scalar(node, ancestor_matched)
        elif isinstance(node, tuple):
            return self.process_tuple(node, ancestor_matched)
        else:
            raise Exception("Unknown class" + str(node.__class__))
    
    def process_col(self, node, ancestor_matched):
        descendant_matched = False
        for item in node.value:
            descendant_matched |= self.process_node(item, ancestor_matched)
        
        if ancestor_matched:
            node.status = self.max_status(node, MatchStatus.descendant)
        elif descendant_matched:
            node.status = self.max_status(node, MatchStatus.ancestor)
        else:
            node.status = self.max_status(node, MatchStatus.unrelated)
        
        return descendant_matched
    
    def process_tuple(self, node, ancestor_matched):
        key, value = node
        key_matched = self.process_node(key, ancestor_matched)
        value_matched = self.process_node(value, key_matched or ancestor_matched)
        if not key_matched:
            if value_matched:
                key.status = self.max_status(key, MatchStatus.ancestor)
            elif ancestor_matched:
                key.status = self.max_status(key, MatchStatus.descendant)  
            else:
                key.status = self.max_status(key, MatchStatus.unrelated)
        # If the value of the tuple matched, key is marked as an ancestor, even while
        # it's actually a sibling in the internal tree structure
        if value.status == MatchStatus.matched:
            self.set_status(key, MatchStatus.ancestor)
        elif value.status == MatchStatus.ancestor:
            self.set_status(key, MatchStatus.ancestor)
        return key_matched or value_matched

    def process_scalar(self, node, ancestor_matched):
        node.matches = list(self.pattern.finditer(node.value))
        matched = len(node.matches) > 0
        if matched:
            node.status = self.max_status(node, MatchStatus.matched)
        elif ancestor_matched:
            node.status = self.max_status(node, MatchStatus.descendant)
        else:
            node.status = self.max_status(node, MatchStatus.unrelated)
        return matched
    
    def max_status(self, node, new_status):
        old_status = getattr(node, 'status', MatchStatus.unrelated)
        return max(old_status, new_status)
        
    def crop(self, node):
        if node.status == MatchStatus.unrelated:
            return None
        if isinstance(node, SequenceNode):
            node.value = [self.crop(item) for item in node.value]
            node.value = [item for item in node.value if item != None]
        elif isinstance(node, MappingNode):
            aux = []
            for key, value in node.value:
                aux_key = self.crop(key)
                aux_value = self.crop(value)
                aux.append((aux_key, aux_value))
            node.value = [(key, value) for key, value in aux if key != None]
        return node

    def set_status(self, node, status):
        if isinstance(node, SequenceNode):
            for item in node.value:
                self.set_status(item, status)
        elif isinstance(node, MappingNode):
            for key, value in node.value:
                self.set_status(key, status)
                self.set_status(value, status)
        elif isinstance(node, ScalarNode):
            node.status = self.max_status(node, status)
        else:
            raise Exception("Unknown class" + str(node.__class__))
    
    def decorate(self, node):
        if isinstance(node, SequenceNode):
            for item in node.value:
                self.decorate(item)
        elif isinstance(node, MappingNode):
            for key, value in node.value:
                self.decorate(key)
                self.decorate(value)
        elif isinstance(node, ScalarNode):
            if self.color:
                if node.status == MatchStatus.ancestor:
                    node.decorated_value = self.colorize_ancestor(node.value)
                elif node.status == MatchStatus.matched:
                    node.decorated_value = self.colorize_match(node.value, node.matches)
                else:
                    node.decorated_value = node.value
            else:
                node.decorated_value = node.value
        else:
            raise Exception("Unknown class" + str(node.__class__))

    def colorize_ancestor(self, value):
        return colored(value, 'white', attrs=['dark'])
        
    def colorize_match(self, value, matches):
        buffer = StringIO()
        pre_pos = 0
        for match in matches:
            buffer.write(value[pre_pos:match.start()])
            # Only color non-space characters. Otherwise the line-wrapping 
            # algorithm of folded style is confused
            replacement = r'\1' + colored(r'\2', 'red', attrs=['bold']) + r'\3'
            matched_value = re.sub(r'^(\s*)(\S+)(\s*)$', replacement, value[match.start():match.end()])
            buffer.write(matched_value)
            pre_pos = match.end()
        buffer.write(value[pre_pos:])
        return buffer.getvalue()

    def serialize(self, node):
        stream = StringIO()
        getvalue = stream.getvalue
        dumper = YrepDumper(stream)
        dumper.open()
        dumper.serialize(node)
        dumper.close()
        return getvalue()
