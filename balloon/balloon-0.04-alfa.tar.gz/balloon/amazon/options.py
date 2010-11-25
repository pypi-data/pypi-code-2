

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
    return " --image-location='us-east-1'"


#--------------------------------------------------------------------------------------
from balloon.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon' )

a_container.add_option( PersistentOption( "--image-location",
                                          metavar = "< location of the cluster nodes : 'eu-west-1', 'us-east-1', 'us-west-1' or 'ap-southeast-1' >",
                                          choices = [ 'eu-west-1', 'us-east-1', 'us-west-1', 'ap-southeast-1' ],
                                          action = "store",
                                          dest = "image_location",
                                          help = "('%default', by default)",
                                          default = "us-east-1" ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    an_options, an_args = the_option_parser.parse_args()

    an_image_location = an_options.image_location

    return an_image_location


#--------------------------------------------------------------------------------------
def compose( the_image_location ) :
    return "--image-location='%s'" % ( the_image_location )


#--------------------------------------------------------------------------------------
from balloon.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
def dump( the_identation_level, the_output ) :
    from balloon.preferences import dump_begin
    dump_begin( the_identation_level, a_container, the_output )

    from security_options import dump as security_dump
    security_dump( the_identation_level + 1, the_output )
    
    from ec2.options import dump as ec2_dump
    ec2_dump( the_identation_level + 1, the_output )
    
    from s3_options import dump as s3_dump
    s3_dump( the_identation_level + 1, the_output )
    
    from apps.options import dump as apps_dump
    apps_dump( the_identation_level + 1, the_output )
    
    from balloon.preferences import dump_end
    dump_end( the_identation_level, a_container, the_output )
    pass


#------------------------------------------------------------------------------------------
