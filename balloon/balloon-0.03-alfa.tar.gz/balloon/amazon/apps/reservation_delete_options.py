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
Deletes the appointed Amazon EC2 reservation and release all its incorporated resources
"""

#--------------------------------------------------------------------------------------
def usage_description() :
    return " <reservation-id 1>[ <reservation-id 2>]"


#--------------------------------------------------------------------------------------
from balloon.preferences import OptionGroup
a_container = OptionGroup( 'amazon.cluster_rm' )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    an_options, an_args = the_option_parser.parse_args()

    from balloon.preferences import get_inputs
    a_reservation_ids = get_inputs( an_args )

    return a_reservation_ids


#--------------------------------------------------------------------------------------
def compose( the_reservation_ids ) :
    import balloon.common as common

    return common.print_args( the_reservation_ids, ' ' )


#--------------------------------------------------------------------------------------
from balloon.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from balloon.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#--------------------------------------------------------------------------------------
