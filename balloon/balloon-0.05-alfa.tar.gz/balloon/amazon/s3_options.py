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


#------------------------------------------------------------------------------------------
"""
This script is responsible for efficient uploading of multi file data
"""


#--------------------------------------------------------------------------------------
def usage_description() :
    return "  --s3location=''"


#--------------------------------------------------------------------------------------
from balloon.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.s3' )

a_container.add_option( PersistentOption( "--s3location",
                                          metavar = "< location of the trasfered data : 'EU', ''( us-east ), 'us-west-1' or 'ap-southeast-1' >",
                                          choices = [ 'EU', '', 'us-west-1', 'ap-southeast-1' ],
                                          action = "store",
                                          dest = "s3location",
                                          help = "'%default', by default ",
                                          default = '' ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    from balloon.common import print_d
    an_options, an_args = the_option_parser.parse_args()

    a_s3location = an_options.s3location
    
    return a_s3location


#--------------------------------------------------------------------------------------
def compose( the_s3location ) :
    return "--s3location='%s'" % the_s3location


#--------------------------------------------------------------------------------------
from balloon.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from balloon.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#--------------------------------------------------------------------------------------
