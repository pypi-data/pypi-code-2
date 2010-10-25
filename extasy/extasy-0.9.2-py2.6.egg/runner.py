#!/usr/bin/python
# -*- coding: utf8 -*-

import pycukes
from pycukes.runner import Scenario
from pycukes.runner import TEMPLATE_PATTERN
import re
import extasy.selenium

def extasy_run(self):
    scenarios = self._parsed_story.get_stories()[0].scenarios
    for scenario_title, steps in scenarios:
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
                    msg_pattern = re.sub(TEMPLATE_PATTERN, r'([^"]*?)', step_regex)
                    msg_pattern = re.escape(msg_pattern)
                    msg_pattern = r'^%s$' % msg_pattern.replace(re.escape(r'([^"]*?)'), r'([^"]*?)')
                    
                    if re.match(msg_pattern, step_message, re.IGNORECASE ):
                        actual_scenario = (step_method,
                                           step_message,
                                           re.match(msg_pattern,
                                                    step_message, re.IGNORECASE).groups() )
                        extasy_actual_scenario = (step_method,
                                           step_message,
                                           re.match(msg_pattern,
                                                    step_message, re.IGNORECASE).groups(), indentation_level )
                scenario_steps.append( actual_scenario )
                extasy_scenario_steps.append( extasy_actual_scenario )

        self._pycukes_story.scenarios.append( new_scenario )
        
    return self._pycukes_story.run()
    

pycukes.runner.StoryRunner.run = extasy_run
