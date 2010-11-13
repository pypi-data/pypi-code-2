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

    from instance_extract_options import usage_description as usage_description_options
    an_usage_description += usage_description_options()
    
    an_usage_description += ec2.use.options.usage_description()

    from balloon import VERSION
    a_version = "%s" % VERSION

    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )

    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )

    #----------------------- Definition of the command line arguments ------------------------
    from instance_extract_options import add as add_options
    add_options( an_option_parser )

    ec2.use.options.add( an_option_parser )

    amazon.security_options.add( an_option_parser )
    
    common.options.add( an_option_parser )

 
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()
    
    common.options.extract( an_option_parser )
    
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )
    
    a_reservation_id = ec2.use.options.extract( an_option_parser )

    from instance_extract_options import extract as extract_options
    an_instance_ord = extract_options( an_option_parser )

    from balloon.preferences import get
    an_image_location = get( 'amazon.image_location' )
    a_host_port = int( get( 'amazon.ec2.host_port' ) )
    a_login_name = get( 'amazon.ec2.ami.use.login_name' )


    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]

    from instance_extract_options import compose as compose_options
    a_call = "%s %s %s" % ( an_engine, compose_options( an_instance_ord ), ec2.use.options.compose( a_reservation_id ) )
    print_d( a_call + '\n' )


    print_d( "\n----------------------- Running actual functionality ----------------------\n" )
    a_spent_time = Timer()
    
    an_ec2_conn = ec2.common.region_connect( an_image_location, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )

    a_reservation = ec2.use.get_reservation( an_ec2_conn, a_reservation_id )
    print_d( '< %r > : %s\n' % ( a_reservation, a_reservation.instances ) )
    
    an_instance = a_reservation.instances[ an_instance_ord ]
    print_d( "an_instance = %s\n" % an_instance )
    
    an_identity_file = ec2.run.get_identity_filepath( an_instance.key_name )
    print_d( "an_identity_file = '%s'\n" % an_identity_file )
    
    import os.path
    if not os.path.exists( an_identity_file ) :
        print_d( "\n-------------------- There are no such identity files ---------------------\n" )
        import sys, os; sys.exit( os.EX_UNAVAILABLE )
        pass
    
    
    print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
    a_password = None
    a_host_name = an_instance.public_dns_name
    
    common.ssh.options.track( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
    
    
    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    common.ssh.options.echo( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
    print_d( a_call + '\n' )
    
    
    print_d( "\n-------------------------------------- OK ---------------------------------\n" )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
