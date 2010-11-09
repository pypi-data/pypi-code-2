#!/usr/bin/python
# -*- coding: utf8 -*-

from finder import (extasy_find_steps_modules,
                    find_text_specs,
                    find_before_all,
                    find_before_each,
                    find_after_all,
                    find_after_each,
                    extasy_find_hook_steps,)


import pyhistorian
from pyhistorian.output import colored
import sys
from unicodedata import normalize
import locale
import codecs

def _extasy_story_colored(self, msg, color):
    if not isinstance( msg, unicode):
        msg = msg.decode( 'utf8' )
    
    msg = msg.encode( sys.stdin.encoding )
    
    if 'windows' in os.environ.get( 'OS', '' ).lower():
        set_terminal_color( 'white' )
    
    if self.colored == False:
        return msg
    return colored( msg, color, _pyhistorian_story_colored, self )

def _extasy_outputwriter_colored(self, msg, color):
    if not isinstance( msg, unicode):
        msg = msg.decode( 'utf8' )
    
    msg = msg.encode( sys.stdin.encoding )
    
    if 'windows' in os.environ.get( 'OS', '' ).lower():
        set_terminal_color( 'white' )
    
    if self._should_be_colored:
        return colored(msg, color, _pyhistorian_output_colored, self )
        
    return msg
    
import os
if 'windows' in os.environ.get( 'OS', '' ).lower(): 
    import ctypes
    def set_terminal_color(color):
        colors = [ 'black', 'blue', 'green', 'aqua', 'red', 'purple', 'yellow', 'white', 'gray', 'light blue', 'light green', 'light aqua', 'light red', 'light purple', 'light yellow' ]
        std_out_handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, colors.index( color ) )
    

import termcolor
def colored(msg, color, method = None, instance = None):
    if color == 'term':
        return msg
        
    if 'windows' in os.environ.get( 'OS', '' ).lower():
        set_terminal_color( color.lower() )
        return msg
    
    return method( instance, msg, color )
    
_pyhistorian_output_colored = pyhistorian.output.OutputWriter._colored
_pyhistorian_story_colored = pyhistorian.story.Story._colored
    
pyhistorian.output.OutputWriter._colored = _extasy_outputwriter_colored
pyhistorian.story.Story._colored = _extasy_story_colored
                    
from pycukes.runner import StoryRunner

from optparse import OptionParser
import os
import extasy
from subcommand_optparser import *
import re

def extasy_console(stories_dir, steps_dir, output, colored=False, settings = None):
    modules = extasy_find_steps_modules(steps_dir)
    extasy.settings.setValues( settings )
    extasy.selenium.getDriver().start_test()
    for spec in find_text_specs(stories_dir):
        StoryRunner(spec, output, colored=colored, modules=modules).run()
    extasy.selenium.getDriver().stop_test()

    
stories_dirname = '.'

    
def main():   
    create_cmd = Subcommand( 'create', optparse.OptionParser(usage='%prog [OPTIONS] "Story title"...' ), 'creates a new .story file' )
    run_cmd = Subcommand( 'run', optparse.OptionParser(usage='%prog [OPTIONS] [Story_file]...' ), 'runs stories' )

    parser = SubcommandsOptionParser(
        subcommands = ( create_cmd, run_cmd )
    )
    
    parser.add_option( '-s', '--stories-dir', default=None, dest='stories_dir' )
    parser.add_option('-l', '--language', default='en-us', dest='language')
    
    run_cmd.parser.add_option('-t', '--steps-dir', default=None, dest='steps_dir')
    run_cmd.parser.add_option('-n', '--no-colors', default=None, action='store_true', dest='no_colors')
    run_cmd.parser.add_option('', '--selenium-server', default='localhost', dest='selenium-server')
    run_cmd.parser.add_option('', '--selenium-port', default='4444', dest='selenium-port')
    run_cmd.parser.add_option('', '--browser', default='firefox', dest='browser')
    run_cmd.parser.add_option('', '--base-url', default=None, dest='base-url')
    
    
    options, subcommand, suboptions, subargs = parser.parse_args()
    
    for x in dir( options ):
        if not x.startswith( '_' ):
            if x not in dir( suboptions ):
                setattr( suboptions, x, getattr( options, x ) )
                
    extasy.settings.setValues( suboptions )
    
    if subcommand is create_cmd:
        extasy_create_command( subargs, suboptions )
        
    elif subcommand is run_cmd:
        extasy_run_command( subargs, suboptions )
    

    
def extasy_create_command( args, options ):
    stories_dirname = extasy.settings.get( 'stories_dir', '.' )
    numberedFileRe = re.compile( r'^(\d)+' )
    path = os.path.dirname( __file__ )
    
    templatePath = '%s/lang/%s-template.story' % ( path, extasy.settings.get( 'language', 'en-us' ) )
    template = codecs.open( templatePath, encoding='utf-8' ).read()
    
    for storyTitle in args:
        storyTitle = storyTitle.decode( locale.getdefaultlocale()[1] )
        fileName = re.sub( '\W+', '_', normalize( 'NFKD', storyTitle ).encode( 'ASCII', 'ignore' ) ) + '.story'
        filePath = '%s/%s' % ( stories_dirname, fileName )
        
        if os.path.exists( fileName ):
            print 'Story file "%s" already exists' % fileName
            continue
            
        f = codecs.open( filePath, 'w', encoding='utf-8' )
        f.write( template % { 'title' : storyTitle } )
        f.close()

    
def extasy_run_command( args, values ):
    steps_modules = []
    files = []
    before_all_methods = []
    before_each_methods = []
    after_all_methods = []
    after_each_methods = []

    for arg in args:
        files.append(arg)
        stories_dirname = os.path.dirname(arg) or '.'
        extasy.settings.set( '_stories_dir', stories_dirname )
    
    try:
        if values.stories_dir:
            files.extend([values.stories_dir+'/'+filename for filename in os.listdir(values.stories_dir)
                            if filename.endswith('.story')])
            stories_dirname = values.stories_dir
            extasy.settings.set( '_stories_dir', stories_dirname )
        elif files == []:
            files.extend([stories_dirname+'/'+filename for filename in os.listdir(stories_dirname)
                                              if filename.endswith('.story')])

        steps_modules = extasy_find_steps_modules(values.steps_dir or stories_dirname+'/step_definitions')
        extasy.runner._steps_modules = steps_modules
    except OSError, e:
        pass

    if os.path.exists(stories_dirname+'/support'):
        before_all_methods = find_before_all(stories_dirname+'/support')
        after_all_methods = find_after_all(stories_dirname+'/support')
        before_each_methods = find_before_each(stories_dirname+'/support')
        after_each_methods = find_after_each(stories_dirname+'/support')

    colored = True
    if values.no_colors:
        colored = False

    exit_code = True
    
    extasy.selenium.getDriver().start_test()
    for index, story in enumerate(files):
        hook_steps = extasy_find_hook_steps( story )
        before_all_methods += hook_steps.get( '_before_alls', [] )
        after_all_methods += hook_steps.get( '_after_alls', [] )
        before_each_methods += hook_steps.get( '_before_eachs', [] )
        after_each_methods += hook_steps.get( '_after_eachs', [] )
        
        story_runner = StoryRunner(open(story).read(),
                                         sys.stdout,
                                         colored=colored,
                                         modules=steps_modules,
                                         language=values.language,
                                         before_all=before_all_methods,
                                         before_each=before_each_methods,
                                         after_all=after_all_methods,
                                         after_each=after_each_methods)
        
        story_runner._story_file = story
        
        story_status = story_runner.run()
        exit_code = exit_code and story_status
        if index < len(files)-1:
            sys.stdout.write('\n\n')

    extasy.selenium.getDriver().stop_test()
    
    exit(int(not exit_code))
