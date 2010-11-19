
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
import optparse
class OptionGroup( optparse.OptionContainer ) :
    def __init__( self, the_namespace, the_title = None, the_description = None ) :
        optparse.OptionContainer.__init__( self, optparse.Option, "error", the_description )
        self._create_option_mappings()

        self._namespace = the_namespace
        self._title = the_title
        pass

    def _create_option_list( self ) :
        self.option_list = []
        pass

    def get_namespace( self ) :
        return self._namespace
    
    def get_subnamespace( self ) :
        return self._namespace.split( '.' )[ -1 ]
    
    def get_title( self ) :
        return self._title
    
    def __len__( self ) :
        return len( self.option_list )
    
    pass


#--------------------------------------------------------------------------------------
import optparse
class PersistentOption( optparse.Option ) :
    def __init__( self, *opts, **attrs ) :
        optparse.Option.__init__( self, *opts, **attrs )
        pass

    pass


#--------------------------------------------------------------------------------------
import optparse
class TransientOption( optparse.Option ) :
    def __init__( self, *opts, **attrs ) :
        optparse.Option.__init__( self, *opts, **attrs )
        pass

    pass


#--------------------------------------------------------------------------------------
def resource_filename() :
    # If user explicitly appointed a specific resource file - use it
    import os; an_rcfilename = os.getenv( "BALLOON_RCFILE" )

    if an_rcfilename == None or an_rcfilename == '' : # If no user defined file, generate a proper one
        import balloon; an_rcfilename = "~/.%src-%s.py" % ( balloon.NAME, balloon.VERSION )
        pass

    return an_rcfilename


#--------------------------------------------------------------------------------------
IDENTATION_PREFFIX = "    "

def ident( the_identation_level ) :
    an_identation = ""
    for id in range( the_identation_level ) :
        an_identation += IDENTATION_PREFFIX
        pass
    
    return an_identation


#--------------------------------------------------------------------------------------
def dump_resume( the_identation_level, the_option_group, the_output ) :
    for an_option in the_option_group.option_list :
        if not isinstance( an_option, PersistentOption ) :
            continue
        
        a_dest = an_option.dest
        a_default = an_option.default
        a_metavar = an_option.metavar
        a_metavar = a_metavar.replace( '< ', '' )
        a_metavar = a_metavar.replace( ' >', '' )
        # a_metavar = a_metavar.title()
        a_metavar = a_metavar[ 0 ].upper() + a_metavar[ 1 : ]
        a_value_format = "%r"
        if isinstance( a_default, str ) :
            a_value_format = "'%s'"
            pass
        a_formatted_value = a_value_format % a_default
        the_output.write( ident( the_identation_level + 1 ) + "%s = %s # %s\n" %
                          ( a_dest, a_formatted_value, a_metavar ) )

        pass
    pass


#--------------------------------------------------------------------------------------
def dump_begin( the_identation_level, the_option_group, the_output ) :
    # if len( the_option_group ) == 0 :
    #     return
    
    a_section_comment = ''
    a_title = the_option_group.get_title()
    if a_title != None :
        a_section_comment = ' # %s' % a_title
        pass

    a_section_name = the_option_group.get_subnamespace();
    the_output.write( ident( the_identation_level ) + "class %s :%s\n" % ( a_section_name, a_section_comment ) )

    a_description = the_option_group.get_description()
    if a_description != None :
        the_output.write( ident( the_identation_level + 1 ) + "\"\"\" %s \"\"\"\n" % ( a_description ) )
        pass
    
    dump_resume( the_identation_level, the_option_group, the_output )

    # the_output.write( "\n" )
    pass
    

#--------------------------------------------------------------------------------------
def dump_end( the_identation_level, the_option_group, the_output ) :
    # if len( the_option_group ) == 0 :
    #     return

    the_output.write( ident( the_identation_level + 1 ) + "pass\n\n" )
    pass


#--------------------------------------------------------------------------------------
PREFERENCES = None

def pickup() :
    global PREFERENCES
    if PREFERENCES != None:
        return PREFERENCES
    
    from preferences import resource_filename
    an_rcfilename = resource_filename()

    import os.path;
    an_rcfilename = os.path.expanduser( an_rcfilename )
    an_rcfilename = os.path.abspath( an_rcfilename )
    if not os.path.isfile( an_rcfilename ) :
        # If resource file does not exist - write a predefined one
        an_rcfile = open( an_rcfilename, "w" )
        import balloon; an_rcfile.write( """
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
## Author : Automatically generated (%s-%s)
##


#--------------------------------------------------------------------------------------
\"""
Balloon User Preferences
\"""


#--------------------------------------------------------------------------------------
""" % ( balloon.NAME, balloon.VERSION ) )

        import cStringIO
        an_output = cStringIO.StringIO()

        from common.options import dump as common_dump;  common_dump( 0, an_output )

        from amazon.options import dump as amazon_dump;  amazon_dump( 0, an_output )
        
        an_rcfile.write( an_output.getvalue() )

        an_rcfile.write( '\n' )
        an_rcfile.write( '#--------------------------------------------------------------------------------------' )
        an_rcfile.write( '\n' )
    
        an_rcfile.close()

        import stat
        # os.chmod( an_rcfilename, stat.S_IRUSR ) # To protect user data
        pass

    an_rcfile = open( an_rcfilename )
    PREFERENCES = compile( "".join( an_rcfile.readlines() ), an_rcfilename, 'exec' )
    an_rcfile.close()

    return PREFERENCES

    
#--------------------------------------------------------------------------------------
def get( the_namespace ) :
    a_value = None
    try:
        exec pickup()

        an_expression = 'a_value = %s' % ( the_namespace )

        exec an_expression

        if a_value != None and a_value != 'None' :
            return a_value
        
        pass
    except :
        import sys, traceback
        traceback.print_exc( file = sys.stderr )
        pass
    
    return None


#--------------------------------------------------------------------------------------
def add_options( the_option_parser, the_option_group ) :
    exec pickup()

    an_option_prefix = the_option_group.get_namespace()

    a_title = the_option_group.get_title()
    if a_title == None :
        a_title = an_option_prefix
        pass
    
    a_description = the_option_group.get_description()
    
    an_option_group = optparse.OptionGroup( the_option_parser, a_title, a_description )
    for an_option in the_option_group.option_list :
        if isinstance( an_option, PersistentOption ) :
            try:
                a_value = None
                an_expression = 'a_value = %s.%s' % ( an_option_prefix, an_option.dest )
                
                exec an_expression
                
                if a_value != None and a_value != 'None' :
                    an_option.default = a_value
                    pass
                
                pass
            except :
                import sys, traceback
                traceback.print_exc( file = sys.stderr )
                pass
            
            pass

        an_option_group.add_option( an_option )
        pass

    if len( the_option_group ) > 0 :
        the_option_parser.add_option_group( an_option_group )
        pass
    
    pass


#--------------------------------------------------------------------------------------
def template_add( the_option_parser, the_container ) :
    add_options( the_option_parser, the_container)
    pass


#------------------------------------------------------------------------------------------
def template_dump( the_identation_level, the_container, the_output ) :
    from balloon.preferences import dump_begin
    dump_begin( the_identation_level, the_container, the_output )

    from balloon.preferences import dump_end
    dump_end( the_identation_level, the_container, the_output )
    pass


#--------------------------------------------------------------------------------------
def correct_value( the_value ) :
    if the_value == "" or the_value == "''" :
        return None
    
    return the_value


#--------------------------------------------------------------------------------------
def get_input( the_args ) :
    if len( the_args ) > 0 :
        return correct_value( the_args[ 0 ] ), the_args[ 1 : ]

    try:
        a_values = raw_input()
    except:
        import sys, os; sys.exit( os.EX_UNAVAILABLE )
        pass

    a_values = a_values.split( ' ' )

    return correct_value( a_values[ 0 ] ), a_values[ 1 : ]


#--------------------------------------------------------------------------------------
def correct_values( the_values ) :
    a_values = []
    for a_value in the_values :
        if a_value == "" or a_value == "''" :
            a_values.append( None )
        else:
            a_values.append( a_value )
            pass
        pass
    
    return a_values


#--------------------------------------------------------------------------------------
def get_inputs( the_args ) :
    if len( the_args ) > 0 :
        return correct_values( the_args )

    try:
        a_values = [ raw_input() ]
    except:
        import sys, os; sys.exit( os.EX_UNAVAILABLE )
        pass
    
    return correct_values( a_values )


#--------------------------------------------------------------------------------------
