

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
    from balloon import common

    an_usage_description = ''
    an_usage_description += " mpirun --hostfile ~/.openmpi_hostfile -x LD_LIBRARY_PATH -x PATH -x WM_PROJECT_DIR -x MPI_BUFFER_SIZE -np ${a_number_processors} ${application} -case . -parallel"
    an_usage_description += " --case-dir='.'"
    an_usage_description += " --solver-log='log.solver-run'"
    an_usage_description += " --watched-keyword='ExecutionTime = '"
    an_usage_description += " --study-name='my favorite study'"
    an_usage_description += " --upload-item-size=5160"
    
    return an_usage_description


#--------------------------------------------------------------------------------------
from balloon.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.apps.timestamps_upload' )

a_container.add_option( TransientOption( "--case-dir",
                                         metavar = "< location of files inside of the study >",
                                         action = "store",
                                         dest = "case_dir",
                                         help = "(\"%default\", by default)",
                                         default = '.' ) )

a_container.add_option( TransientOption( "--solver-log",
                                         metavar = "< location of files inside of the study >",
                                         action = "store",
                                         dest = "solver_log",
                                         help = "(\"%default\", by default)",
                                         default = 'log.solver-run' ) )

a_container.add_option( TransientOption( "--watched-keyword",
                                         metavar = "< location of files inside of the study >",
                                         action = "store",
                                         dest = "watched_keyword",
                                         help = "(\"%default\", by default)",
                                         default = 'ExecutionTime = ' ) )

a_container.add_option( TransientOption( "--study-name",
                                         metavar = "< referenced name of the user study >",
                                         action = "store",
                                         dest = "study_name",
                                         default = None ) )

a_container.add_option( TransientOption( "--upload-seed-size",
                                         metavar = "< size of file pieces to be uploaded, in bytes >",
                                         type = "int",
                                         action = "store",
                                         dest = "upload_seed_size",
                                         help = "(\"%default\", by default)",
                                         default = 65536 ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    from balloon.common import print_d, print_i, print_e
    
    an_options, an_args = the_option_parser.parse_args()

    if len( an_args ) != 0 :
        a_solver_run = ' '.join( an_args )
    else:
        a_solver_run = 'cat ./log.interFoam.balloon'
        pass
    print_d( "a_solver_run = '%s'\n" % a_solver_run )

    import os.path; a_case_dir = os.path.abspath( os.path.expanduser( an_options.case_dir ) )
    if not os.path.isdir( a_case_dir ) :
        the_option_parser.error( "--case-dir='%s' should be a folder\n" % a_case_dir )
        pass

    a_solver_log = an_options.solver_log

    a_watched_keyword = an_options.watched_keyword
    print_d( "a_watched_keyword = '%s'\n" % a_watched_keyword )

    a_study_name = an_options.study_name
    if a_study_name == None :
        import uuid; a_study_name = 'timestamps-' + str( uuid.uuid4() )
        pass
    print_d( "a_study_name = '%s'\n" % a_study_name )

    an_upload_seed_size = an_options.upload_seed_size
    print_d( "an_upload_seed_size = %d, bytes\n" % an_upload_seed_size )

    return a_solver_run, a_case_dir, a_solver_log, a_watched_keyword, a_study_name, an_upload_seed_size


#--------------------------------------------------------------------------------------
def compose( the_solver_run, the_case_dir, the_solver_log, the_watched_keyword, the_study_name, the_upload_seed_size ) :
    a_compose = "'%s'" % the_solver_run
    a_compose += " --case-dir='%s'" % the_case_dir
    a_compose += " --solver-log='%s'" % the_solver_log
    a_compose += " --watched-keyword='%s'" % the_watched_keyword
    a_compose += " --study-name='%s'" % the_study_name
    a_compose += " --upload-item-size=%d" % the_upload_seed_size
    
    return a_compose


#--------------------------------------------------------------------------------------
from balloon.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from balloon.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#------------------------------------------------------------------------------------------
