#!/usr/bin/env python

import sys
import os
import re
import time

from datetime import datetime
from HTMLParser import HTMLParser
from optparse import OptionParser

__license__ = 'BSD'
__author__ = 'Jonas Galvez <http://jonasgalvez.com.br>'
__version__ = '0.3'

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

def _find_and_prepare_hcss_files(source_dir, target_dir):
    hcss_files = []
    for n, d, files in os.walk(source_dir):
        for f in files:
            if f.endswith('.hcss'):
                hcss_file_path = os.path.join(n, f)
                hcss_file_dict = {}
                hcss_file_dict['source_path'] = hcss_file_path
                try:
                    hcss_file_dict['mtime'] = os.stat(hcss_file_path).st_mtime
                except OSError:
                    continue
                hcss_file_dict['target_path'] = hcss_file_path.replace(
                    source_dir,
                    target_dir
                )
                hcss_file_dict['target_path'] = list(hcss_file_dict['target_path'])
                hcss_file_dict['target_path'][-4:] = list('css')
                hcss_file_dict['target_path'] = ''.join(hcss_file_dict['target_path'])
                hcss_files.append(hcss_file_dict)
    return hcss_files
        
def _recompile_loop(source_dir, target_dir):
    mtimes = {}
    source_dir = os.path.abspath(source_dir)
    target_dir = os.path.abspath(target_dir)
    source_files = _find_and_prepare_hcss_files(source_dir, target_dir)
    for source_file in source_files:
        mtimes[source_file['source_path']] = source_file['mtime']
    while True:
        try:
            source_files = _find_and_prepare_hcss_files(source_dir, target_dir)
            for hcss_file in source_files:
                source_file_path = hcss_file['source_path']
                source_file_name = os.path.split(source_file_path)[-1]
                try:
                    mtime = os.stat(source_file_path).st_mtime
                except OSError:
                    continue
                old_time = mtimes.get(source_file_path)
                if old_time is None or mtime > old_time:
                    source_hcss_file = open(source_file_path)
                    source_hcss = source_hcss_file.read()
                    source_hcss_file.close()
                    hcss_parser = HCSSParser()
                    hcss_parser.feed(source_hcss)
                    target_file_name = '%s.css' % os.path.splitext(
                        source_file_name
                    )[0]
                    target_file_path = hcss_file['target_path']
                    target_file_directory = os.path.split(target_file_path)[0]
                    if not os.path.exists(target_file_directory):
                        os.makedirs(target_file_directory)
                    target_file = open(target_file_path, 'w')
                    target_file.write(hcss_parser.css())
                    target_file.close()
                    timestamp = datetime.now().strftime('%Y:%m:%d %H:%M:%S')
                    mtimes[source_file_path] = mtime
                    current_dir = os.getcwd()
                    print('  * %s Compiled %s to %s' % (
                        timestamp, 
                        re.sub('^%s' % re.escape(current_dir), '.', source_file_path),
                        re.sub('^%s' % re.escape(current_dir), '.', target_file_path)
                    ))
            time.sleep(2)
        except KeyboardInterrupt:   
            sys.exit()

def main():
    '''
    Compiles hcss stylesheets to css.
    '''
    parser = OptionParser(
        version = "%prog " + __version__, 
        description = main.__doc__.strip(),
        usage = '''\n  %prog [options] [arg1, [arg2]]\n'''
                '''  %prog -o source.css > target.css\n'''
                '''  cat a.css b.css | %prog -i target.css\n'''
                '''  cat a.css b.css | %prog -io > target.css'''
    )
    parser.add_option(
        '-v', 
        action = 'store_true',
        dest = 'print_version'
    )
    parser.add_option(
        '-i', '--stdin', 
        action = 'store_true', 
        dest = 'stdin', 
        help = 'read from standard input'
    )
    parser.add_option(
        '-o', '--stdout', 
        action = 'store_true',
        dest = 'stdout', 
        help = 'write to standard output'
    )
    parser.add_option(
        '-s', '--source-dir',
        dest = 'source_dir',
        help = 'monitor directory for changes in *.hcss files and compile to *.css'
    )
    parser.add_option(
        '-t', '--target-dir',
        dest = 'target_dir',
        help = '(optional) directory where to put compiled *.hcss files'
    )
    options, args = parser.parse_args()
    if options.print_version:
        parser.print_version()
        sys.exit()
    hcss_parser = HCSSParser()
    if options.source_dir:
        source_dir = options.source_dir
        target_dir = source_dir
        if options.target_dir:
            target_dir = options.target_dir
        print('  * Watching directory %s for changes in .hcss files' % source_dir)
        _recompile_loop(options.source_dir, target_dir)
    elif options.target_dir:
        print('--source-dir needs to be set')
    elif options.stdin:
        sources = sys.stdin.read()
        hcss_parser.feed(sources)
        if options.stdout:
            sys.stdout.write(hcss_parser.css())
            sys.exit()
        elif len(args):
            target = open(args[0], 'w')
            target.write(hcss_parser.css())
            target.close()
        else:
            parser.print_help()
    elif options.stdout:
        if len(args):
            source_file = open(args[0])
            source = source_file.read()
            source_file.close()
            hcss_parser.feed(source)
            print(hcss_parser.css())
        else:
            parser.print_help()
    elif len(args) == 2:
        source_file = open(args[0])
        source = source_file.read()
        source_file.close()
        hcss_parser.feed(source)
        target = open(args[1], 'w')
        target.write(hcss_parser.css())
        target.close()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()