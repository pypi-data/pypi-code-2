
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
from cloudflu.common import sh_command, print_d


#--------------------------------------------------------------------------------------
def get_archivator( the_api_number ):
    if the_api_number <= '0.5':
       return Gzip()
    
    return Bzip2()


#--------------------------------------------------------------------------------------
class ArchivatorBase:
    def pack( self, the_working_directory, the_archive_name, the_source_file, the_printing_depth ):
        raise NotImplementedError("It is abstract method")
        
    def unpack( self, the_archive_file, the_output_dir, the_printing_depth ):
        raise NotImplementedError("It is abstract method")
    
    def suffix( self ):
        raise NotImplementedError("It is abstract method")

#--------------------------------------------------------------------------------------
class Gzip( ArchivatorBase ):
    def pack( self, the_working_directory, the_archive_name, the_source_file, the_printing_depth ):
        sh_command( "cd '%s' &&  tar -czf %s '%s'" % 
                ( the_working_directory, the_archive_name, the_source_file ), the_printing_depth )
        pass
    
    def unpack( self, the_archive_file, the_output_dir, the_printing_depth ):
        sh_command( "tar -xzf '%s' -C '%s'" % ( the_archive_file, the_output_dir ), the_printing_depth + 1 )
        pass

    def suffix( self ):
        
        return "tgz"


#--------------------------------------------------------------------------------------
class Bzip2( ArchivatorBase ):
    def pack( self, the_working_directory, the_archive_name, the_source_file, the_printing_depth ):
        sh_command( "cd '%s' &&  tar c %s | bzip2 -f --best >'%s'" % 
                ( the_working_directory, the_source_file, the_archive_name ), the_printing_depth )
        pass
    
    def unpack( self, the_archive_file, the_output_dir, the_printing_depth ):
        sh_command( "tar -xjf '%s' -C '%s'" % ( the_archive_file, the_output_dir ), the_printing_depth + 1 )
        pass

    def suffix( self ):
        
        return "bz2"


#--------------------------------------------------------------------------------------
