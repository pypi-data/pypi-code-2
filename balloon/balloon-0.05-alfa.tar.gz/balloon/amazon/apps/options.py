

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
from balloon.preferences import OptionGroup
a_container = OptionGroup( 'amazon.apps' )


#--------------------------------------------------------------------------------------
def dump( the_identation_level, the_output ) :
    from balloon.preferences import dump_begin
    dump_begin( the_identation_level, a_container, the_output )

    from reservation_run_options import dump as reservation_run_dump
    reservation_run_dump( the_identation_level + 1, the_output )

    from solver_run_options import dump as solver_run_dump
    solver_run_dump( the_identation_level + 1, the_output )

    from instance_extract_options import dump as instance_extract_dump
    instance_extract_dump( the_identation_level + 1, the_output )
    
    from deploy_credentials_options import dump as deploy_credentials_dump
    deploy_credentials_dump( the_identation_level + 1, the_output )
    
    from openmpi_config_options import dump as openmpi_config_dump
    openmpi_config_dump( the_identation_level + 1, the_output )
    
    import data_transfer_options; data_transfer_options.dump( the_identation_level + 1, the_output )
     
    # from ls_options import dump as ls_dump
    # ls_dump( the_identation_level + 1, the_output )
    # 
    # from rm_study_options import dump as rm_study_dump
    # rm_study_dump( the_identation_level + 1, the_output )
    # 
    # from rm_options import dump as rm_dump
    # rm_dump( the_identation_level + 1, the_output )
    
    from balloon.preferences import dump_end
    dump_end( the_identation_level, a_container, the_output )
    pass


#------------------------------------------------------------------------------------------
