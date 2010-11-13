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
Deletes the appointed Amazon EC2 reservation and release all its incorporated resources
"""


#--------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_e, sh_command
from balloon.common import Timer, WorkerPool

from balloon import amazon
from balloon.amazon import ec2


#--------------------------------------------------------------------------------------
def execute( the_ec2_conn, the_reservation_id ) :
    a_reservation = ec2.use.get_reservation( the_ec2_conn, the_reservation_id )
    if a_reservation == None :
        return
    print_d( '< %r > : %s\n' % ( a_reservation, a_reservation.instances ) )
        
    a_security_group = None
    try:
        a_security_group = ec2.use.get_security_group( the_ec2_conn, a_reservation )
        print_d( "< %r > : %s\n" % ( a_security_group, a_security_group.rules ) )
    except:
        from balloon.common import print_traceback
        print_traceback()
        pass
        
    an_instance = a_reservation.instances[ 0 ]
    an_identity_file = ec2.run.get_identity_filepath( an_instance.key_name )
        
    a_reservation.stop_all()
    
    try:
        the_ec2_conn.delete_key_pair( an_instance.key_name )
        import os; os.remove( an_identity_file )
    except:
        from balloon.common import print_traceback
        print_traceback()
        pass
    
    try:
        the_ec2_conn.delete_security_group( a_security_group.name )
    except:
        from balloon.common import print_traceback
        print_traceback()
        pass
    
    print_d( '%s ' % an_instance.update() )
        
    while an_instance.update() != 'terminated' :
        print_d( '.' )
        continue
    
    print_d( ' %s\n' % an_instance.update() )
    pass


#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------    
    an_usage_description = "%prog"

    from reservation_delete_options import usage_description as usage_description_options
    an_usage_description += usage_description_options()

    from balloon import VERSION
    a_version = "%s" % VERSION

    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )

    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )


    #----------------------- Definition of the command line arguments ------------------------
    ec2.use.options.add( an_option_parser )

    amazon.security_options.add( an_option_parser )
    
    common.options.add( an_option_parser )
  
 
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()

    common.options.extract( an_option_parser )
    
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )
    
    from reservation_delete_options import extract as extract_options
    a_reservation_ids = extract_options( an_option_parser )
    
    from balloon.preferences import get
    an_image_location = get( 'amazon.image_location' )
   

    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]
    
    from reservation_delete_options import compose as compose_options
    a_call = "%s %s" % ( an_engine, compose_options( a_reservation_ids ) )
    print_d( a_call + '\n' )
 
 
    print_d( "\n----------------------- Running actual functionality ----------------------\n" )
    a_spent_time = Timer()
    
    an_ec2_conn = ec2.common.region_connect( an_image_location, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )

    a_worker_pool = WorkerPool( len( a_reservation_ids ) )

    for a_reservation_id in a_reservation_ids :
        a_worker_pool.charge( execute, ( an_ec2_conn, a_reservation_id ) )
        pass
    
    a_worker_pool.shutdown()
    a_worker_pool.join()

    print_d( "a_spent_time = %s, sec\n" % a_spent_time )
    
    
    print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
    # There are no - it is a terminal step
    
    
    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    print_d( a_call + '\n' )
    
    
    print_d( "\n-------------------------------------- OK ---------------------------------\n" )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
