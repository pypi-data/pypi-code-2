

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
Contains the package dedicated preferences
"""


#--------------------------------------------------------------------------------------
def usage_description() :
    return " --min-count=1 --max-count=1"


#--------------------------------------------------------------------------------------
from balloon.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.apps.cluster_run' )

a_container.add_option( PersistentOption( "--min-count",
                                          metavar = "< minimum number of instances to start >",
                                          type = "int",
                                          action = "store",
                                          dest = "min_count",
                                          help = "(%default, by default)",
                                          default = 1 ) )

a_container.add_option( TransientOption( "--max-count",
                                         metavar = "< minimum number of instances to start >",
                                         type = "int",
                                         action = "store",
                                         dest = "max_count",
                                         help = "(%default, by default)",
                                         default = 1 ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    an_options, an_args = the_option_parser.parse_args()

    a_min_count = an_options.min_count
    a_max_count = an_options.max_count
    if a_min_count > a_max_count :
        import math
        print_d( '--min-count=%d > --max-count=%d : --max-count will be corrected to %d' 
                 % ( a_min_count, a_max_count, a_min_count ) )
        an_options.max_count = a_max_count = a_min_count
        pass

    return a_min_count, a_max_count


#--------------------------------------------------------------------------------------
def compose( the_min_count, the_max_count ) :
    return "--min-count=%d --max-count=%d" % ( the_min_count, the_max_count )


#--------------------------------------------------------------------------------------
from balloon.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from balloon.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#------------------------------------------------------------------------------------------
