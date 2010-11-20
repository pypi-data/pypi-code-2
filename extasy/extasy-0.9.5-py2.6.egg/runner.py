#!/usr/bin/python
# -*- coding: utf8 -*-

import pycukes
from pycukes.runner import StoryRunner
from pycukes.runner import Scenario
from pycukes.runner import TEMPLATE_PATTERN
import re
import extasy.selenium
import extasy
import StringIO
import os, sys

_steps_modules = []

from extasy.finder import (extasy_find_steps_modules,
                    find_text_specs,
                    find_before_all,
                    find_before_each,
                    find_after_all,
                    find_after_each,
                    extasy_find_hook_steps,)

def run_story_scenario( storyfile, scenario = None, before_all_methods = None, after_all_methods = None, before_each_methods = None, after_each_methods = None ):
    global _steps_modules
    steps_modules = _steps_modules
    
    if not os.path.exists( storyfile ):
        storyfile = extasy.settings.get( '_stories_dir' ) + '/' + storyfile
        
    if not os.path.exists( storyfile ):
        raise Exception( 'Story file "%s" does not exist' % storyfile )

    hook_steps = extasy_find_hook_steps( storyfile )
    
    before_all_methods = before_all_methods or []
    after_all_methods = after_all_methods or []
    before_each_methods = before_each_methods or []
    after_each_methods = after_each_methods or []
    
    before_all_methods += hook_steps.get( '_before_alls', [] )
    after_all_methods += hook_steps.get( '_after_alls', [] )
    before_each_methods += hook_steps.get( '_before_eachs', [] )
    after_each_methods += hook_steps.get( '_after_eachs', [] )
    
    colored = True
    if extasy.settings.get( 'no_colors' ):
        colored = False
    
    story_output = StringIO.StringIO()
    story_runner = StoryRunner(open(storyfile).read(),
        story_output,
        colored = colored,
        modules = steps_modules,
        language = extasy.settings.get( 'language', 'en-us' ),
        before_all = before_all_methods,
        before_each = before_each_methods,
        after_all = after_all_methods,
        after_each = after_each_methods
    )
    story_runner._story_file = storyfile
    
    story_status = story_runner.run( scenarios = [ scenario ] )
    
    if not story_status:
        print story_output.read()
    return story_status



def extasy_run( self, scenarios = None ):
    _scenarios_to_run = scenarios or []
    SCENARIO_NAME = 0
    SCENARIO_NUMBER = 2
    
    
    if _scenarios_to_run:
        titles, steps, numbers = zip(*self._parsed_story.get_stories()[0].scenarios)
        titles = [ x.decode( 'utf8' ) for x in titles ]
        
        scenarios = []
        for _scenario_to_run in _scenarios_to_run:
            _scenario_to_run = _scenario_to_run.decode( sys.stdin.encoding )
            
            if _scenario_to_run in titles:
                index = titles.index( _scenario_to_run )
            elif _scenario_to_run in numbers:
                index = numbers.index( _scenario_to_run )
            else:
                raise Exception( 'Scenario "%s" not found in story "%s"' % ( _scenario_to_run, self._story_file ) )
                
            scenarios.append( self._parsed_story.get_stories()[0].scenarios[ index ] )
    else:
        scenarios = self._parsed_story.get_stories()[0].scenarios
    
    for scenario_title, steps, scenario_number in scenarios:
        new_scenario = type('EXTasyScenario',
                            (Scenario,),
                            {'__doc__': scenario_title,
                            '_givens': [],
                            '_whens': [],
                            '_thens': [],
                            
                            '_extasy_givens': [],
                            '_extasy_whens': [],
                            '_extasy_thens': [],
                            })

        for step_name in ['given', 'when', 'then']:
            for step_message, indentation_level in steps[step_name]:
                scenario_steps = getattr(new_scenario, '_%ss' % step_name)
                extasy_scenario_steps = getattr(new_scenario, '_extasy_%ss' % step_name)
                all_runner_steps = getattr(self, '_all_%ss' % step_name)
                                    
                actual_scenario = (None, step_message, ())
                extasy_actual_scenario = (None, step_message, (), indentation_level)
                for step_regex, (step_method, step_args) in all_runner_steps.items():
                    step_message = step_message.strip()
                    msg_pattern = re.sub( '\\$([a-zA-Z]\\w*)', r'(?P<\1>[^"]*?)', step_regex)
                    msg_pattern = re.escape(msg_pattern).replace( r'\_', '_' )
                    msg_pattern = re.sub( r'\\\(\\\?P\\\<(.*?)\\\>\\\[\\\^\\\"\\\]\\\*\\\?\\\)', r'(?P<\1>[^"]*?)', msg_pattern )
                    
                    if re.match(msg_pattern, step_message, re.IGNORECASE ):
                        params = re.match(msg_pattern, step_message, re.IGNORECASE).groupdict()
                        for x in params:
                            params[ x ] = params[ x ].decode( 'utf-8' )
                            
                        actual_scenario = (step_method,
                                           step_message,
                                           params )
                        extasy_actual_scenario = (step_method,
                                           step_message,
                                           params, indentation_level )
                scenario_steps.append( actual_scenario )
                extasy_scenario_steps.append( extasy_actual_scenario )

        self._pycukes_story.scenarios.append( new_scenario )
        
    return self._pycukes_story.run()
    

pycukes.runner.StoryRunner.run = extasy_run

