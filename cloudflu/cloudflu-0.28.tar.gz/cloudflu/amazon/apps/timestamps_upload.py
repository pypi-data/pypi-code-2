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


#------------------------------------------------------------------------------------------
"""
Automatically extracts and uploads specified output solver data into ''study''. 
Usually appears in context of ''run-hook'' of ''[[cloudflu-solver-start]]'' utility.
"""


#------------------------------------------------------------------------------------------
from cloudflu import amazon

import cloudflu.common as common
from cloudflu.common import print_d, print_e, sh_command


#------------------------------------------------------------------------------------------
def upload_timedata( the_root_object, the_study_name, the_booked,
                     the_upload_seed_size, the_number_threads, the_socket_timeout,
                     the_case_dir, the_item, the_current_dir_list ) :
    try:
        sh_command( "reconstructPar -case '%s' -time %s >> log.reconstructPar 2>&1" % ( the_case_dir, the_item ) )

        import os.path; a_timestamp = os.path.join( the_case_dir, the_item )
        import os.path; a_timestamp = os.path.abspath( a_timestamp )
    
        import data_upload; data_upload.entry_point( the_root_object, { a_timestamp : '' }, 
                                                     the_upload_seed_size, the_number_threads, the_socket_timeout,
                                                     the_study_name, the_booked )
        return
    except OSError, exc :
        print "filename = %s\nstrerror = %s\errno = %s" % \
            ( exc.filename, exc.strerror, exc.errno )
    except Exception :
        from cloudflu.common import print_traceback
        print_traceback()
        pass

    # Try once again, recursively (it might be the only chance before solver finish)
    import time; time.sleep( the_socket_timeout )
    upload_timedata( the_root_object, the_study_name, the_booked,
                     the_upload_seed_size, the_number_threads, the_socket_timeout,
                     the_case_dir, the_item, the_current_dir_list )
    # the_current_dir_list.remove( the_item )
    pass


#------------------------------------------------------------------------------------------
def upload_timelog( the_root_object, the_study_name, the_booked,
                    the_upload_seed_size, the_number_threads, the_socket_timeout,
                    the_item, the_log_file ) :
    a_time_log_file = "%s-%s" % ( the_log_file, the_item )
    sh_command( "cp %s %s" % ( the_log_file, a_time_log_file ) )

    import data_upload; data_upload.entry_point( the_root_object, { a_time_log_file : '' }, 
                                                 the_upload_seed_size, the_number_threads, the_socket_timeout,
                                                 the_study_name, the_booked )    
    pass


#------------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------
    import timestamps_upload_options
    import data_upload_options
    import study_book_options
    import data_seeding_options

    an_usage_description = "%prog"
    an_usage_description += timestamps_upload_options.usage_description()
    an_usage_description += study_book_options.usage_description()
    an_usage_description += data_upload_options.usage_description()
    
    from cloudflu import VERSION
    a_version = "%s" % VERSION
    
    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )
    
    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )
    

    #----------------------- Definition of the command line arguments ------------------------
    timestamps_upload_options.add( an_option_parser )

    study_book_options.add( an_option_parser )

    data_upload_options.add( an_option_parser )

    data_seeding_options.add( an_option_parser )

    common.concurrency_options.add( an_option_parser )

    common.communication_options.add( an_option_parser )

    amazon.security_options.add( an_option_parser )

    common.options.add( an_option_parser )

    
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()

    common.options.extract( an_option_parser )
    
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )
    
    a_socket_timeout = common.communication_options.extract( an_option_parser )

    a_number_threads = common.concurrency_options.extract( an_option_parser )
    
    an_upload_seed_size = data_seeding_options.extract( an_option_parser )

    a_study_name = study_book_options.extract( an_option_parser )
    
    a_booked = data_upload_options.extract( an_option_parser )

    a_solver_run, a_case_dir, a_solver_log, a_watched_keyword, a_watching_timeout, a_time_log, a_finish_hook = \
        timestamps_upload_options.extract( an_option_parser )
    

    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]

    a_call = "%s %s %s %s %s" % ( an_engine, 
                                  timestamps_upload_options.compose( a_solver_run, a_case_dir, a_solver_log, a_watched_keyword, a_watching_timeout, a_time_log, a_finish_hook ),
                                  data_upload_options.compose( a_booked ),
                                  study_book_options.compose( a_study_name ),
                                  data_seeding_options.compose( an_upload_seed_size ) )
    print_d( a_call + '\n' )


    print_d( "\n----------------------- Running actual functionality ----------------------\n" )
    a_spent_time = common.Timer()

    import os.path; a_watched_dir = os.path.join( a_case_dir, 'processor0' )
    if not os.path.isdir( a_watched_dir ) :
        print_e( "Folder - '%s' does not exists\n(it seems that the case folder "
                 "is not ready for the parallel solver run)\n" % a_watched_dir )
        pass
    import os; a_current_dir_list = set( os.listdir( a_watched_dir ) )
    
    from cloudflu.amazon.s3 import TRootObject
    a_root_object = TRootObject.get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
    print_d( "a_root_object = %s\n" % a_root_object )

    from cloudflu.common import WorkerPool
    a_worker_pool = WorkerPool( a_number_threads )
    
    import pexpect; a_child = pexpect.spawn( a_solver_run )
    
    import os.path; a_log_file = os.path.join( a_case_dir, a_solver_log )
    a_child.logfile = file( a_log_file, 'w' )

    while True :
        try:
            try:
                a_child.expect( a_watched_keyword, timeout = a_watching_timeout )
            except:
                break
            
            # print_d( "a_current_dir_list = %s\n" % a_current_dir_list )
            import os; a_fresh_dir_list = set( os.listdir( a_watched_dir ) )
            # print_d( "a_fresh_dir_list = %s\n" % a_fresh_dir_list )

            a_diff_dir_list = a_fresh_dir_list.difference( a_current_dir_list )
            if a_diff_dir_list == set() :
                continue

            a_current_dir_list = a_fresh_dir_list

            for an_item in a_diff_dir_list :
                print_d( "an_item = %s\n" % an_item )
                a_worker_pool.charge( upload_timedata, ( a_root_object, a_study_name, a_booked,
                                                         an_upload_seed_size, a_number_threads, a_socket_timeout,
                                                         a_case_dir, an_item, a_current_dir_list ) )
                if a_time_log == True :
                    a_worker_pool.charge( upload_timelog, ( a_root_object, a_study_name, a_booked,
                                                            an_upload_seed_size, a_number_threads, a_socket_timeout,
                                                            an_item, a_log_file ) )
                    pass
                pass
            pass
        except:
            import sys, traceback
            traceback.print_exc( file = sys.stderr )
            break
        
        pass

    a_worker_pool.shutdown()
    a_worker_pool.join()


    print_d( "\n------------------------ Running timestamps hook --------------------------\n" )
    an_additional_args = "--study-name='%s'" % ( a_study_name )
    an_additional_args += " --number-threads=%d" % ( a_number_threads )
    an_additional_args += " --upload-seed-size=%d" % ( an_upload_seed_size )

    if a_booked == True :
        an_additional_args += " --booked"
        pass

    try:
        sh_command( "%s %s" % ( a_finish_hook, an_additional_args ) )
    except OSError, exc :
        print "filename = %s\nstrerror = %s\errno = %s" % \
            ( exc.filename, exc.strerror, exc.errno )
    except Exception :
        from cloudflu.common import print_traceback
        print_traceback()
        pass


    print_d( "\n------------------------ Sealing the given study --------------------------\n" )
    an_additional_args = "--study-name='%s'" % ( a_study_name )
    sh_command( "cloudflu-study-seal %s" % ( an_additional_args ) )


    print_d( "a_spent_time = %s, sec\n" % a_spent_time )


    print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
    print a_study_name


    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    print_d( a_call + '\n' )
    

    print_d( "\n-------------------------------------- OK ---------------------------------\n" )
    import sys, os; sys.exit( os.EX_OK )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
