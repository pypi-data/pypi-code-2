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
This script is responsible for the task packaging and sending it for execution in a cloud
"""


#--------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_e, sh_command, Timer

from balloon import amazon
from balloon.amazon import ec2


#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------    
    an_usage_description = "%prog"

    from reservation_run_options import usage_description as usage_description_options
    an_usage_description += usage_description_options()
    
    an_usage_description += ec2.ami.run_options.usage_description()

    from balloon import VERSION
    a_version = "%s" % VERSION

    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )

    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )


    #----------------------- Definition of the command line arguments ------------------------
    from reservation_run_options import add as add_options
    add_options( an_option_parser )

    ec2.ami.run_options.add( an_option_parser )
    
    amazon.security_options.add( an_option_parser )

    common.options.add( an_option_parser )
  
 
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()

    common.options.extract( an_option_parser )

    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )

    an_instance_type, an_image_id = ec2.ami.run_options.extract( an_option_parser )

    from reservation_run_options import extract as extract_options
    a_min_count, a_max_count = extract_options( an_option_parser )

    from balloon.preferences import get
    an_image_location = get( 'amazon.image_location' )
    a_host_port = get( 'amazon.ec2.host_port' )
    

    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]

    from reservation_run_options import compose as compose_options
    a_call = "%s %s %s" % ( an_engine, compose_options( a_min_count, a_max_count ),
                            ec2.ami.run_options.compose( an_instance_type, an_image_id ) )
    print_d( a_call + '\n' )


    print_d( "\n----------------------- Running actual functionality ----------------------\n" )
    a_spent_time = Timer()

    a_reservation, an_identity_file = ec2.run.run_reservation( an_image_id, an_image_location, an_instance_type, 
                                                               a_min_count, a_max_count, a_host_port,
                                                               AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )

    print_d( "a_spent_time = %s, sec\n" % a_spent_time )
    

    print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
    an_image_location = a_reservation.region.name
    a_reservation_id = a_reservation.id
    
    ec2.use.options.track( a_reservation_id )


    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    print_d( a_call + '\n' )


    print_d( "\n-------------------------------------- OK ---------------------------------\n" )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
