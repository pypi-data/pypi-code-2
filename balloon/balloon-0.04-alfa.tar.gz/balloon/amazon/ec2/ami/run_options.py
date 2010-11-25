
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
    return " --instance-type='m1.large' --image-id='ami-1cdb2c75'"


#--------------------------------------------------------------------------------------
from balloon.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.ec2.ami.run' )

a_container.add_option( PersistentOption( "--instance-type",
                                          metavar = "< EC2 instance type : 'c1.xlarge' or 'm1.large', for example >",
                                          choices = [ 'm1.large', 'c1.xlarge', 'm1.xlarge', ' m2.xlarge', 'm2.2xlarge', 'm2.4xlarge', 'c1.medium' ],
                                          action = "store",
                                          dest = "instance_type",
                                          help = "('%default', by default)",
                                          default = "c1.xlarge" ) )

a_container.add_option( PersistentOption( "--image-id",
                                          metavar = "< Amazon EC2 AMI ID >",
                                          action = "store",
                                          dest = "image_id",
                                          help = "('%default', by default)",
                                          default = None ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    an_options, an_args = the_option_parser.parse_args()

    an_instance_type = an_options.instance_type
    an_image_id = an_options.image_id

    return an_instance_type, an_image_id


#--------------------------------------------------------------------------------------
def compose( the_instance_type, the_image_id ) :
    return "--instance-type='%s' --image-id='%s'" % ( the_instance_type, the_image_id )


#--------------------------------------------------------------------------------------
from balloon.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from balloon.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#------------------------------------------------------------------------------------------
