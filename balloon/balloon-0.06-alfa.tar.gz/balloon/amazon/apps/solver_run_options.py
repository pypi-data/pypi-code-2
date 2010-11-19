#!/usr/bin/env python

#--------------------------------------------------------------------------------------
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


#--------------------------------------------------------------------------------------
"""
This script is responsible for cluster environment setup for the given Amazon EC2 reservation
"""


#--------------------------------------------------------------------------------------
def usage_description() :
    return " --case-dir='./damBreak' --output-suffix='.out' --before-hook='balloon-foam2vtk-before' --time-hook='balloon-foam2vtk' --after-hook='balloon-foam2vtk-after'"


#--------------------------------------------------------------------------------------
from balloon.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.apps.solver_run' )

a_container.add_option( TransientOption( "--case-dir",
                                         metavar = "< location of the source OpenFOAM case dir >",
                                         action = "store",
                                         dest = "case_dir",
                                         default = None ) )

a_container.add_option( PersistentOption( "--output-suffix",
                                          metavar = "< folder suffix for the output results >",
                                          action = "store",
                                          dest = "output_suffix",
                                          help = "('%default', by default)",
                                          default = '.out' ) )

a_container.add_option( PersistentOption( "--run-hook",
                                          metavar = "< case dir executable in to be run in the cluster >",
                                          action = "store",
                                          dest = "run_hook",
                                          help = "('%default', by default)",
                                          default = 'Allrun' ) )

a_container.add_option( PersistentOption( "--before-hook",
                                          metavar = "< executable to be run 'before' any results will be downloaded >",
                                          action = "store",
                                          dest = "before_hook",
                                          help = "('do nothing', by default)",
                                          default = None ) )

a_container.add_option( PersistentOption( "--time-hook",
                                          metavar = "< executable to be run on each timestamp download >",
                                          action = "store",
                                          dest = "time_hook",
                                          help = "('do nothing', by default)",
                                          default = None ) )

a_container.add_option( PersistentOption( "--after-hook",
                                          metavar = "< executable to be run 'after' all results will be downloaded >",
                                          action = "store",
                                          dest = "after_hook",
                                          help = "('do nothing', by default)",
                                          default = None ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    an_options, an_args = the_option_parser.parse_args()

    if an_options.case_dir == None :
        the_option_parser.error( "Use '--case-dir' option to define folder containing solver case\n" )
        pass

    import os.path; a_case_dir = os.path.abspath( os.path.expanduser(an_options.case_dir ) )
    if not os.path.isdir( a_case_dir ) :
        the_option_parser.error( "--case-dir='%s' should be a folder\n" % a_case_dir )
        pass

    an_output_suffix = an_options.output_suffix

    a_run_hook = an_options.run_hook

    a_before_hook = an_options.before_hook
    a_time_hook = an_options.time_hook
    a_after_hook = an_options.after_hook

    return a_case_dir, an_output_suffix, a_run_hook, a_before_hook, a_time_hook, a_after_hook


#--------------------------------------------------------------------------------------
def compose( the_case_dir, the_output_suffix, the_run_hook, the_before_hook, the_time_hook, the_after_hook ) :
    a_compose = "--case-dir='%s' --output-suffix='%s' --run-hook='%s'" % ( the_case_dir, the_output_suffix, the_run_hook )

    if the_before_hook != None :
        a_compose += " --before-hook='%s'" % the_before_hook
        pass

    if the_time_hook != None :
        a_compose += " --time-hook='%s'" % the_time_hook
        pass

    if the_after_hook != None :
        a_compose += " --after-hook='%s'" % the_after_hook
        pass

    return a_compose


#--------------------------------------------------------------------------------------
from balloon.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from balloon.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#------------------------------------------------------------------------------------------
