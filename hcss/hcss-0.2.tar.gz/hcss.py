#!/usr/bin/env python
import sys
import re
from HTMLParser import HTMLParser
from optparse import OptionParser

__license__ = 'BSD'
__author__ = ('Jonas Galvez', 'jonasgalvez@gmail.com', 'http://jonasgalvez.com.br')
__version__ = '0.1'

class HCSSParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.selector_chain = []
        self.current_rule = None
        self.rules = {'list': []}
        self.subrules = []
    
    def add_rule(self, rule):
        rule['selector'] = self.unredundantize_selector(rule['selector'])
        self.rules['list'].append(rule)
        self.rules[rule['selector']] = rule
        for subrule in self.subrules:
            self.rules['list'].append(subrule)
            self.rules[subrule['selector']] = subrule
        self.subrules = []
        
    def add_subrule(self, rule):
        rule['selector'] = self.unredundantize_selector(rule['selector'])
        self.subrules.append(rule)
    
    def unredundantize_selector(self, selector):
        s = re.split('([\d\w_+-]+#[\d\w_+-]+)', selector)
        n = []
        for i in s[::-1]:
            if i.count('#'):
                n.insert(0, i)
                break
            n.insert(0, i)
        return ''.join(n)
        
    def parse_selector_from_starttag(self, tag, attrs):
        selector = [tag]
        attrs = dict(attrs)
        if 'id' in attrs:
            selector.append('#%s' % attrs['id'])
        elif 'class' in attrs:
            selector.append('.%s' % attrs['class'].split(' ')[0])
        return ''.join(selector)
        
    def flexibly_parse_css(self, css_chunk):
        rules = []
        is_selector = False
        inside_selector = False
        for line in css_chunk.split('\n'):
            is_selector = re.search('(.*)\s*{\s*$', line)
            if is_selector:
                rules.append([is_selector.group(1).strip()])
                is_selector = False
                inside_selector = True
            elif not is_selector and not inside_selector:
                rules.append(line.strip())
            elif inside_selector:
                closes_selector = re.search('^\s*};?\s*$', line)
                if closes_selector:
                    inside_selector = False
                else:
                    rules[-1].append(line.strip())
        return [rule for rule in rules if rule != '']
        
    def compile_rule(self, rule):
        printed_rule = ['%s {' % rule['selector'] ]
        for line in '\n'.join(rule['css']).split('\n'):
            printed_rule.append('  %s' % line)
        printed_rule.append('}')
        return '\n'.join(printed_rule)
        
    def handle_starttag(self, tag, attrs):
        if self.current_rule is not None:
            self.add_rule(self.current_rule)
        this_selector = self.parse_selector_from_starttag(tag, attrs)
        selector = this_selector
        if len(self.selector_chain):
            selector = ' > '.join(self.selector_chain + [selector])
        self.current_rule = {'selector': selector, 'css': []}
        self.selector_chain.append(this_selector)
        
    def handle_startendtag(self, tag, attrs):
        pass
        
    def handle_endtag(self, tag):
        if self.current_rule is not None:
          self.add_rule(self.current_rule)
          self.current_rule = None
        self.selector_chain.pop()
        
    def handle_data(self, data):
        css_tree = self.flexibly_parse_css(data)
        rules, selectors = [], []
        for css_token in css_tree:
            if type(css_token) is list:
                selectors.append(css_token)
            else:
                if css_token.startswith('!'):
                    referenced_selector = css_token[1:-1]
                    for selector in self.rules.keys():
                        if selector[1:] == referenced_selector:
                            for referenced_rule in self.rules[selector]['css']:
                                rules.append(referenced_rule)
                        elif selector[1:].startswith(referenced_selector):
                            new_selector = ''.join([self.current_rule['selector']] + re.split('([:.])', selector)[-2:])
                            self.add_subrule({'selector': new_selector, 'css': self.rules[selector]['css']})
                else:
                    rules.append(css_token)
        if self.current_rule is not None:
            for rule in rules:
                self.current_rule['css'].append(rule)
            for rule in selectors:
                selector = rule[0]  
                if selector[0] in (':', '.', '#'):
                    if selector[0] in ('.', '#') and re.search('[#.][\d\w_+-]+$', self.current_rule['selector']):
                        selector = re.sub('[#.][\d\w_+-]+$', selector, self.current_rule['selector'])
                    else:
                        selector = ''.join((self.current_rule['selector'], selector))
                else: 
                    selector = ' '.join((self.current_rule['selector'], selector))
                self.add_subrule({'selector': selector, 'css': rule[1:]})
        else:
            for rule in selectors:
                self.add_rule({'selector': rule[0], 'css': rule[1:]})
        
    def css(self):
        css = []
        for rule in self.rules['list']:
            css.append('%s {' % rule['selector'])
            for rule_prop in rule['css']:
                css.append('  %s' % rule_prop)
            css.append('}')
        return '\n'.join(css)

def main():
    '''
    Usage: 
  
    % hcss source.hcss > target.css
    % cat common.css source.hcss | hcss > target.css    
    '''
    if len(sys.argv) > 1:
        if True in [opt in ('--help', '-h') for opt in sys.argv[1:]]:
            print('\n'.join(main.__doc__.split('\n')[:-1]))
            sys.exit()
        source = sys.argv[1]
        hcss_file = open(source)
        parser = HCSSParser()
        parser.feed(hcss_file.read())
        hcss_file.close()
        sys.stdout.write(parser.css())
        sys.exit()
    else:
        sources = sys.stdin.read()
        parser = HCSSParser()
        parser.feed(sources)
        sys.stdout.write(parser.css())
        sys.exit()

if __name__ == '__main__':
    main()