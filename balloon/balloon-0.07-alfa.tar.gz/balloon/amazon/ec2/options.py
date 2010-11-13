

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
from balloon.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.ec2' )

a_container.add_option( PersistentOption( "--host-port",
                                          metavar = "< ssh port >",
                                          type = "int",
                                          action = "store",
                                          dest = "host_port",
                                          help = "(\"%default\", by default)",
                                          default = 22 ) )


#------------------------------------------------------------------------------------------
def dump( the_identation_level, the_output ) :
    from balloon.preferences import dump_begin
    dump_begin( the_identation_level, a_container, the_output )

    from ami.options import dump as ami_dump
    ami_dump( the_identation_level + 1, the_output )
    
    # from use_options import dump as use_dump
    # use_dump( the_identation_level + 1, the_output )
    
    from balloon.preferences import dump_end
    dump_end( the_identation_level, a_container, the_output )
    pass


#------------------------------------------------------------------------------------------
