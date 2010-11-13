#!/usr/bin/env python

#------------------------------------------------------------------------------------------
## Copyright 2010 Alexey Petrov
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## See http://sourceforge.net/apps/mediawiki/balloon-foam
##
## Author : Alexey Petrov
##


#------------------------------------------------------------------------------------------
"""
Removes whole appointed cloud study or just given files from this study
"""

#--------------------------------------------------------------------------------------
def usage_description() :
    from balloon import common
    
    an_usage_description = ""
    an_usage_description += " --study-name=<my uploaded study>"
    an_usage_description += " <file path 1>[ <file path 2>]"

    return an_usage_description


#------------------------------------------------------------------------------------------
from balloon.preferences import OptionGroup
a_container = OptionGroup( 'amazon.apps.rm', 'application specific' )

a_container.add_option( "--study-name",
                        metavar = "< name of the uploaded study >",
                        action = "store",
                        dest = "study_name",
                        default = None )


#------------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    from balloon.common import print_d, print_i, print_e

    an_options, an_args = the_option_parser.parse_args()

    a_study_name = an_options.study_name
    if a_study_name == None :
        the_option_parser.error( "Use --study-name option to define proper value\n" )
        pass
    
    print_d( "a_study_name = '%s'\n" % a_study_name )

    from balloon.preferences import get_inputs
    a_located_files = get_inputs( an_args )

    print_d( "a_located_files = %r\n" % a_located_files )

    return a_study_name, a_located_files


#--------------------------------------------------------------------------------------
from balloon.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from balloon.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#--------------------------------------------------------------------------------------
