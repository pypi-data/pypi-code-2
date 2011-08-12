# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

__version__ = '0.92dev'

import codecs
from   os.path                  import dirname
from   copy                     import deepcopy
from   datetime                 import datetime as dt

from   zope.component           import getGlobalSiteManager
import pkg_resources            as pkg

# Import macro-plugins so that they can register themselves.
import eazytext.macro
import eazytext.macro.anchor
import eazytext.macro.clear
import eazytext.macro.html
import eazytext.macro.image
import eazytext.macro.images
import eazytext.macro.redirect
import eazytext.macro.span
import eazytext.macro.toc
import eazytext.macro.yearsbefore
# Import extension-plugins so that they can register themselves.
import eazytext.extension

from   eazytext.interfaces      import IEazyTextMacroFactory, \
                                       IEazyTextTemplateTags, \
                                       IEazyTextExtensionFactory
from   eazytext.parser          import ETParser

DEFAULT_ENCODING = 'utf-8'

defaultconfig = {
    # Development mode settings
    'devmod': True,
    # List of directories to look for the .etx file
    'directories' : '.',
    # path to store the compiled .py file (intermediate file)
    'module_directory' : None,
    # CSV of escape filter names to be applied for expression substitution
    'escape_filters' : 'uni',
    # Default input endcoding for .etx file.
    'input_encoding': DEFAULT_ENCODING,
    # CSV list of plugin packages that needs to be imported, before compilation.
    'plugin_packages'   : '',
    # Default skin file to include translated html file, use this option along
    # with `include_skin`.
    'skinfile' : 'default.css',
    'include_skin' : False,
    # If set to true, the email-id generated using [[ mailto:... ]] markup will
    # be obfuscated.
    'obfuscatemail' : False,
    # Denotes that the parser is invoked by a parent parser, may be because of
    # a plugin
    'nested' : False,
    # Do not allow any <script> tag in the finally generated HTML text.
    'stripscript' : True,
    # If set to false generate the html text enclosed within <article> tag, else
    # wrap them withing <html><body> tag
    'ashtml' : False,
    # In memory cache for compiled etxfile
    'memcache'          : True,
    'text_as_hashkey'   : False,
}

macroplugins = {}           # { plugin-name : instance }
extplugins   = {}           # { plugin-name : instance }
ttplugins    = {}           # { plugin-name : instance }
init_status  = 'pending'
def initplugins( etxconfig, force=False ):
    """Collect and organize macro plugins and extension plugins implementing
    the interfaces,
        IEazyTextMacroFactory, IEazyTextExtensionFactory
    """
    global init_status, macroplugins, extplugins, ttplugins
    if init_status == 'progress' :
        return etxconfig

    if (force == True) or etxconfig.get( 'macroplugins', None ) == None :
        # Load and classify plugins
        init_status = 'progress'
        gsm = getGlobalSiteManager()

        # Load plugin packages
        packages = etxconfig['plugin_packages']
        packages = filter(None, [ x.strip(' \t') for x in packages.split(',') ])
        [ __import__(pkg) for pkg in filter(None, packages) ]

        # Gather plugins template tag handlers, filter-blocks
        for x in gsm.registeredUtilities() :
            if x.provided == IEazyTextMacroFactory :        # macro-plugins
                macroplugins[x.name] = x.component
            if x.provided == IEazyTextExtensionFactory :    # extension-plugins
                extplugins[x.name] = x.component
            if x.provided == IEazyTextTemplateTags :        # tt-plugins
                ttplugins[x.name] = x.component
            etxconfig['macroplugins'] = macroplugins
            etxconfig['extplugins']   = extplugins
            etxconfig['ttplugins']    = ttplugins
    init_status = 'done'
    return etxconfig


#---- APIs for executing Tayra Template Language

class Translate( object ):
    def __init__( self, etxloc=None, etxtext=None, etxconfig={} ):
        """`etxconfig` parameter will find its way into every object defined
        by wiki processor.
            TODO : somehow find a way to pass the arguments to `body` function
        """
        etxconfig_ = deepcopy( defaultconfig )
        etxconfig_.update( etxconfig )
        # Initialize plugins
        self.etxconfig = initplugins( etxconfig_, force=etxconfig_['devmod'] )
        self.etxloc, self.etxtext = etxloc, etxtext
        self.etparser = ETParser( etxconfig=self.etxconfig )

    def __call__( self, entryfn='body', context={} ):
        from   eazytext.compiler import Compiler
        self.compiler = Compiler( etxtext=self.etxtext,
                                  etxloc=self.etxloc,
                                  etxconfig=self.etxconfig,
                                  etparser=self.etparser
                                )
        context['_etxcontext'] = context
        module = self.compiler.execetx( context=context )
        entry = getattr( module, entryfn )
        html = entry() if callable( entry ) else ''
        return html

def etx_cmdline( etxloc, **kwargs ):
    from eazytext.compiler import Compiler

    etxconfig = deepcopy( defaultconfig )
    # directories, module_directory, devmod
    etxconfig.update( kwargs )
    etxconfig['module_directory'] = '.'
    etxconfig['include_skin'] = True
    etxconfig['ashtml'] = True

    # Parse command line arguments and configuration
    context = eval( etxconfig.pop( 'context', '{}' ))
    debuglevel = etxconfig.pop( 'debuglevel', 0 )
    show = etxconfig.pop( 'show', False )
    dump = etxconfig.pop( 'dump', False )
    encoding = etxconfig['input_encoding']

    # Initialize plugins
    etxconfig = initplugins( etxconfig, force=etxconfig['devmod'] )

    # Setup parser
    etparser = ETParser( etxconfig=etxconfig, debug=debuglevel )
    compiler = Compiler( etxloc=etxloc, etxconfig=etxconfig, etparser=etparser )
    pyfile = compiler.etxfile+'.py'
    htmlfile = compiler.etxfile.rsplit('.', 1)[0] + '.html'

    if debuglevel :
        print "AST tree ..."
        tu = compiler.toast()
    elif show :
        print "AST tree ..."
        tu = compiler.toast()
        tu.show()
    elif dump :
        tu = compiler.toast()
        rctext =  tu.dump()
        if rctext != codecs.open( compiler.etxfile, encoding=encoding ).read() :
            print "Mismatch ..."
        else : print "Success ..."
    else :
        print "Generating py / html file ... "
        pytext = compiler.topy( etxhash=compiler.etxlookup.etxhash )
        # Intermediate file should always be encoded in 'utf-8'
        codecs.open(pyfile, mode='w', encoding=DEFAULT_ENCODING).write(pytext)

        etxconfig.setdefault( 'memcache', True )
        t = Translate( etxloc=etxloc, etxconfig=etxconfig )
        html = t( context=context )
        codecs.open( htmlfile, mode='w', encoding=encoding).write( html )

        # This is for measuring performance
        st = dt.now()
        [ t( context=context ) for i in range(10) ]
        print (dt.now() - st) / 10

