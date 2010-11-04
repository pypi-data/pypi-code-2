#!/usr/bin/python
# -*- coding: utf8 -*-

import story_parser
import re
from story_parser import InvalidScenarioException

story_parser.RegexInternationalized._all_regexes[ 'en-us' ][ 'given_regex' ] = 'Given:'
story_parser.RegexInternationalized._all_regexes[ 'en-us' ][ 'when_regex' ] = 'When:'
story_parser.RegexInternationalized._all_regexes[ 'en-us' ][ 'then_regex' ] = 'Then:'
story_parser.RegexInternationalized._all_regexes[ 'en-us' ][ 'no_and_regex' ] = '(.+)'
story_parser.RegexInternationalized._all_regexes[ 'en-us' ][ 'scenario_regex' ] = r'Scenario(?: (\d+))?: (.+)'


story_parser.RegexInternationalized._all_regexes[ 'pt-br' ][ 'given_regex' ] = 'Dado que:'
story_parser.RegexInternationalized._all_regexes[ 'pt-br' ][ 'when_regex' ] = 'Quando:'
story_parser.RegexInternationalized._all_regexes[ 'pt-br' ][ 'then_regex' ] = 'Então:'
story_parser.RegexInternationalized._all_regexes[ 'pt-br' ][ 'no_and_regex' ] = '(.+)'
story_parser.RegexInternationalized._all_regexes[ 'pt-br' ][ 'scenario_regex' ] = r'Cenário(?: (\d+))?: (.+)'

def get_indentation_level( line ):
    match = re.match( '^([\s\t]*)', line )
    indentation_chars = match.group( 1 )
    indentation_level = indentation_chars.count( '\t' ) * 4 + indentation_chars.count( ' ' )
    return indentation_level

def extasy__remove_blank_lines(self):
    lines = self._story_text.split('\n')
    self._orig_lines = [line for line in lines if line.strip()][4:]
    self._lines = [line.strip() for line in lines if line.strip()]

def extasy__get_scenario_blocks(self, lines):
    index = 0
    scenario_blocks = []
    while index < len(lines):
        scenario_title = re.match(self._regexes['scenario_regex'], lines[index])
        accepted_lines_regexes = (self._regexes['given_regex'],
                                  self._regexes['when_regex'],
                                  self._regexes['then_regex'],
                                  self._regexes['and_regex'],
                                  self._regexes['no_and_regex'])
        scenario_block = []
        if scenario_title:
            orig_line = self._orig_lines[ index ]
            indentation_level = get_indentation_level( orig_line )
            scenario_block.append( ( lines[index], indentation_level ) )
            index += 1
            while index < len(lines):
                orig_line = self._orig_lines[ index ]
                indentation_level = get_indentation_level( orig_line )
                if re.match(self._regexes['scenario_regex'], lines[index]):
                    break
                for accepted_line_regex in accepted_lines_regexes:
                    if re.match(accepted_line_regex, lines[index]):
                        scenario_block.append( ( lines[index], indentation_level ) )
                        break
                else:
                    raise InvalidScenarioException("Invalid Step!")
                index += 1
            scenario_blocks.append(scenario_block)
        else:
            raise InvalidScenarioException("Invalid Scenario!")
    return scenario_blocks


def extasy_parse_scenarios(self, lines):
    scenario_blocks = self._get_scenario_blocks(lines)
    scenarios = []
    for scenario_block in scenario_blocks:
        steps = {'given': [],  'when': [], 'then': []}
        scenario_title = re.match(self._regexes['scenario_regex'], scenario_block[0][0])
        last_step = None
        for line,intendation_level in scenario_block[1:]:
            is_scenario_group_line = False
            for step_name in ['given', 'when', 'then']:
                if re.match(self._regexes[step_name+'_regex'], line):
                    is_scenario_group_line = True
                    last_step = step_name
                    break
                elif re.match(self._regexes['and_regex'], line) or re.match(self._regexes['no_and_regex'], line):
                    for step_name in ['given', 'when', 'then']:
                        if re.match(self._regexes[step_name+'_regex'], line):
                            is_scenario_group_line = True
                            
                    if is_scenario_group_line:
                        continue
                        
                    step_line = re.match(self._regexes['and_regex'], line)
                    if not step_line:
                        step_line = re.match(self._regexes['no_and_regex'], line)
                        
                    if last_step is None:
                        raise InvalidScenarioException('Invalid Step!')
                    step_name = last_step
                    break
#                else:
#                    raise InvalidScenarioException("Invalid Step!")
            if is_scenario_group_line:
                pass
            else:
                steps[step_name].append( ( step_line.group(1), intendation_level ) )
        scenarios.append((scenario_title.group(2), steps, scenario_title.group(1)))
    return scenarios

story_parser.StoriesParser._remove_blank_lines = extasy__remove_blank_lines
story_parser.StoriesParser._get_scenario_blocks = extasy__get_scenario_blocks
story_parser.StoriesParser._parse_scenarios = extasy_parse_scenarios