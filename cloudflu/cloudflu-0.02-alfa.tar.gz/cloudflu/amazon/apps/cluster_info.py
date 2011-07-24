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
## See http://sourceforge.net/apps/mediawiki/cloudflu
##
## Author : Alexey Petrov
##


#--------------------------------------------------------------------------------------
"""
This utility is used for connection to appointed ''cluster'' node by its ''cluster'' 
identifier and order number. The cluster identifier can be obtained as result of 
: ''a_cluster_id=`[[cloudflu-cluster-start]]` && echo ${a_cluster_id}'' 
command or extracted from output of ''[[cloudflu-cluster-ls]]'' utility. 
"""


#--------------------------------------------------------------------------------------
import cloudflu.common as common
from cloudflu.common import print_d, print_i, print_e, sh_command, Timer

from cloudflu import amazon
from cloudflu.amazon import ec2

# To hack standard printing functionality
import cloudflu.common.options as common_options


#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------    
    import instance_extract_options

    an_usage_description = "%prog"
    an_usage_description += ec2.use.options.usage_description()

    from cloudflu import VERSION
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
    
    common_options.ENABLE_DEBUG = False

    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )
    
    a_cluster_id = ec2.use.options.extract( an_option_parser )

    from cloudflu.preferences import get
    a_cluster_location = get( 'amazon.cluster.location' )
    a_host_port = int( get( 'amazon.cluster.host_port' ) )
    a_login_name = get( 'amazon.cluster.login_name' )


    #------------------------------------------------------------------------------------------
    a_spent_time = Timer()
    
    an_ec2_conn = ec2.common.region_connect( a_cluster_location, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
    a_reservation = ec2.use.get_reservation( an_ec2_conn, a_cluster_id )
    
    common_options.ENABLE_DEBUG = True

    print_i( 'The following commands can be used to login to the corresponding cluster nodes :\n' )
    print_d( '------------------------------------------------------------------------------\n' )
    for an_instance in a_reservation.instances :
        a_password = None
        a_host_name = an_instance.public_dns_name
        an_identity_file = ec2.run.get_identity_filepath( an_instance.key_name )
        common.ssh.options.echo( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
        pass
    
    from cloudflu.preferences import get
    a_hostfile = get( 'amazon.openmpi_config.hostfile' )

    print_i( 'The following command can be used to run solver in parallel on this cluster :\n' )
    print_d( '---------------------------------------------------------------------------\n' )
    print_d( 'mpirun --hostfile %s -np <number processors> <solver> <its args>\n' % a_hostfile )

    print_i( '---------------------------------------------------------------------------\n' )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
