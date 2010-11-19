

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
    return " --study-name=< an unique study name >"


#--------------------------------------------------------------------------------------
from balloon.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.apps.data_transfer.upload' )

a_container.add_option( TransientOption( "--study-name",
                                         metavar = "< an unique study name >",
                                         action = "store",
                                         dest = "study_name",
                                         help = "(generated, by default)",
                                         default = None ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    from balloon.common import print_d, print_i, print_e
    
    an_options, an_args = the_option_parser.parse_args()

    a_study_name = an_options.study_name
    if a_study_name == None :
        import uuid; a_study_name = 'tmp-' + str( uuid.uuid4() )
        pass
    
    print_d( "a_study_name = '%s'\n" % a_study_name )

    return a_study_name


#--------------------------------------------------------------------------------------
def compose( the_study_name ) :
    return "--study-name='%s'" % the_study_name


#--------------------------------------------------------------------------------------
from balloon.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from balloon.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#------------------------------------------------------------------------------------------
