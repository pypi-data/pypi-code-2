#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import sys
import os
import textwrap
import traceback
try:
    import cProfile as profile
except ImportError:
    import profile
try:
    import pstats
    pstats_available=True
except ImportError:
    pstats_available=False
import textwrap
import gc
from coopr.pyomo import *
from coopr.opt.base import SolverFactory
from coopr.opt.parallel import SolverManagerFactory
import pyutilib.misc
from pyutilib.component.core import ExtensionPoint, Plugin, implements
from pyutilib.services import TempfileManager

from coopr.pyomo.expr.linear_repn import linearize_model_expressions

filter_excepthook=False
modelapi = {    'pyomo_create_model':IPyomoScriptCreateModel, 
                'pyomo_creat_modeldata':IPyomoScriptCreateModelData, 
                'pyomo_print_model':IPyomoScriptPrintModel, 
                'pyomo_print_instance':IPyomoScriptPrintInstance, 
                'pyomo_modify_instance':IPyomoScriptModifyInstance, 
                'pyomo_save_instance':IPyomoScriptSaveInstance, 
                'pyomo_print_results':IPyomoScriptPrintResults, 
                'pyomo_save_results':IPyomoScriptSaveResults, 
                'pyomo_postprocess':IPyomoScriptPostprocess}

#
# Print information about modeling components supported by Pyomo
#
def print_components(options):
    print ""
    print "----------------------------------------------------------------"
    print "Pyomo Model Components:"
    print "----------------------------------------------------------------"
    components = pyomo.model_components()
    index = pyutilib.misc.sort_index(components)
    for i in index:
        print ""
        print " "+components[i][0]
        for line in textwrap.wrap(components[i][1], 59):
            print "    "+line
    print ""
    print "----------------------------------------------------------------"
    print "Pyomo Virtual Sets:"
    print "----------------------------------------------------------------"
    pyomo_sets = pyomo.predefined_sets()
    index = pyutilib.misc.sort_index(pyomo_sets)
    for i in index:
        print ""
        print " "+pyomo_sets[i][0]
        print "    "+pyomo_sets[i][1]

#
# Print information about the solvers that are available
#
def print_solver_help(options):
    print "The following solvers are are currently supported:"
    solver_list = SolverFactory.services()
    solver_list = sorted( filter(lambda x: '_' != x[0], solver_list) )
    n = max(map(len, solver_list))
    wrapper = textwrap.TextWrapper(subsequent_indent=' '*(n+9))
    for s in solver_list:
        format = '    %-'+str(n)+'s  %s'
        print wrapper.fill(format % (s , SolverFactory.doc(s)))
    print 'The default solver is glpk.'
    print ""
    wrapper = textwrap.TextWrapper(replace_whitespace=False)
    print wrapper.fill('Subsolver options can be specified by with the solver name followed by colon and then the subsolver.  For example, the following specifies that the asl solver will be used:')
    print '   --asl:PICO'
    print wrapper.fill('This indicates that the asl solver will launch the PICO executable to perform optimization. Currently, no other solver supports this syntax.')


#
# Setup Pyomo execution environment
#
def setup_environment(options, args):
    #
    # Disable garbage collection
    #
    if options.disable_gc:
        gc.disable()
    #
    # Setup verbose debugging mode
    #
    pyomo.reset_debugging()
    #
    # Setup debugging for specific Pyomo components
    #
    if options.debug is not None:
       for val in options.debug:
         pyomo.set_debugging( val )
    if options.verbose:
       pyomo.set_debugging("verbose")
    #
    # Setup management for temporary files
    #
    if not options.tempdir is None:
        if not os.path.exists(options.tempdir):
            msg =  'Directory for temporary files does not exist: %s'
            raise ValueError, msg % options.tempdir
        TempfileManager.tempdir = options.tempdir

    #
    # Configure exception management
    #
    def pyomo_excepthook(etype,value,tb):
        """
        This exception hook gets called when debugging is on. Otherwise,
        run_command in this module is called.
        """
        global filter_excepthook
        model=""
        if len(args) > 0:
            model=args[0]

        action = "loading"
        if not filter_excepthook:
            action = "running"
        name = "model "
        if model != "":
            name += model

        msg = "\nERROR: Unexpected exception while %s %s" % (action, name)

        #
        # This handles the case where the error is propagated by a KeyError.
        # KeyError likes to pass raw strings that don't handle newlines
        # (they translate "\n" to "\\n"), as well as tacking on single
        # quotes at either end of the error message. This undoes all that.
        #
        valueStr = "\n" + str(value)
        if etype == KeyError:
            valueStr = "\n" + str(value).replace("\\n","\n")[1:-1]

        print msg,
        print "  ",valueStr
        print ""
        tb_list = traceback.extract_tb(tb,None)
        i=0
        if not pyomo.debug("all") and filter_excepthook:
            while i < len(tb_list):
                #print "Y",model,tb_list[i][0]
                if model in tb_list[i][0]:
                    break
                i += 1
        print "Traceback (most recent call last):"
        for item in tb_list[i:]:
            print "  File \""+item[0]+"\", line "+str(item[1])+", in "+item[2]
            if item[3] is not None:
                print "    "+item[3]
        sys.exit(1)
    sys.excepthook = pyomo_excepthook
    return True


#
# Execute preprocessing files
#
def apply_preprocessing(options, parser, args):
    global filter_excepthook
    #
    #
    # Setup solver and model
    #
    #
    if len(args) == 0:
        parser.print_help()
        return False
    #
    if not options.preprocess is None:
        for file in options.preprocess:
            preprocess = pyutilib.misc.import_file(file)
    #
    for ep in ExtensionPoint(IPyomoScriptPreprocess):
        ep.apply( options=options )
    #
    filter_excepthook=True
    options.usermodel = pyutilib.misc.import_file(args[0])
    filter_excepthook=False

    usermodel_dir = dir(options.usermodel)
    options._usermodel_plugins = []
    for key in modelapi:
        if key in usermodel_dir:
            #print "ZZZ",key
            class TMP(Plugin):
                implements(modelapi[key])
                def __init__(self):
                    Plugin.__init__(self)
                    self.fn = getattr(options.usermodel, key)
                def apply(self,**kwds):
                    return self.fn(**kwds)
            options._usermodel_plugins.append( TMP() )

    if 'pyomo_preprocess' in usermodel_dir:
        if options.model_name in usermodel_dir:
            msg = "Preprocessing function 'pyomo_preprocess' defined in file" \
                  " '%s', but model is already constructed!"
            raise SystemExit, msg % args[0]
        getattr(options.usermodel, 'pyomo_preprocess')( options=options )

    return True

#
# Create instance of Pyomo model
#
# TODO: extend this API to make it more generic:
#       create_model(options, model_file=None, data_files=None, modeldata=None)
#
def create_model(options, args):
    #
    # Verify that files exist
    #
    for file in args:
        if not os.path.exists(file):
            raise IOError, "File "+file+" does not exist!"
    #
    # Create Model
    #
    ep = ExtensionPoint(IPyomoScriptCreateModel)
    model_name = 'model'
    if options.model_name is not None: model_name = options.model_name

    if model_name in dir(options.usermodel):
        if len(ep) > 0:
            msg = "Model construction function 'create_model' defined in "    \
                  "file '%s', but model is already constructed!"
            raise SystemExit, msg % args[0]
        model = getattr(options.usermodel, model_name)

        if model is None:
            msg = "'%s' object is 'None' in module %s"
            raise SystemExit, msg % (model_name, args[0])
            sys.exit(0)

    else:
       if len(ep) == 0:
           msg = "Neither '%s' nor 'pyomo_create_model' are available in "    \
                 'module %s'
           raise SystemExit, msg % ( model_name, args[0] )
       elif len(ep) > 1:
           msg = 'Multiple model construction plugins have been registered!'
           raise SystemExit, msg
       else:
            model_options = options.model_options
            if model_options is None:
                model_options = []
            model = ep.service().apply(
                options=pyutilib.misc.Container(*model_options) )
    #
    for ep in ExtensionPoint(IPyomoScriptPrintModel):
        ep.apply( options=options, model=model )
        
    #
    # Disable canonical repn for ASL solvers
    #
    # Likely we need to change the framework so that canonical repn
    # is not assumed to be required by all solvers?
    #
    if hasattr(options, 'solver') and options.solver.startswith('asl'):
        model.skip_canonical_repn = True
    
    #
    # Create Problem Instance
    #
    ep = ExtensionPoint(IPyomoScriptCreateModelData)
    if len(ep) > 1:
        msg = 'Multiple model data construction plugins have been registered!'
        raise SystemExit, msg

    if len(ep) == 1:
        modeldata = ep.apply( options=options, model=model )
    else:
        modeldata = ModelData()

    if len(args) > 2:
        #
        # Load a list of *.dat files
        #
        for file in args[1:]:
            suffix = (file).split(".")[-1]
            if suffix != "dat":
                msg = 'When specifiying multiple data files, they must all '  \
                      'be *.dat files.  File specified: %s'
                raise SystemExit, msg % str( file )

            modeldata.add(file)

        modeldata.read(model)
        instance = model.create(modeldata)

    elif len(args) == 2:
       #
       # Load a *.dat file or process a *.py data file
       #
       suffix = (args[1]).split(".")[-1]
       if suffix == "dat":
          instance = model.create(args[1])
       elif suffix == "py":
          userdata = pyutilib.misc.import_file(args[1])
          if "modeldata" in dir(userdata):
                if len(ep) == 1:
                    msg = "Cannot apply 'pyomo_create_modeldata' and use the" \
                          " 'modeldata' object that is provided in the model"
                    raise SystemExit, msg

                if userdata.modeldata is None:
                    msg = "'modeldata' object is 'None' in module %s"
                    raise SystemExit, msg % str( args[1] )

                modeldata=userdata.modeldata

          else:
                if len(ep) == 0:
                    msg = "Neither 'modeldata' nor 'pyomo_create_model_data"  \
                          'is defined in module %s'
                    raise SystemExit, msg % str( args[1] )

          modeldata.read(model)
          instance = model.create(modeldata)
       else:
          raise ValueError, "Unknown data file type: "+args[1]
    else:
       instance = model.create()

    if hasattr(options, "linearize_expressions") and (options.linearize_expressions is True):
       linearize_model_expressions(instance)

    #
    ep = ExtensionPoint(IPyomoScriptModifyInstance)
    for ep in ExtensionPoint(IPyomoScriptModifyInstance):
        ep.apply( options=options, model=model, instance=instance )
    #
    if pyomo.debug("instance"):
       print "MODEL INSTANCE"
       instance.pprint()
       print ""

    for ep in ExtensionPoint(IPyomoScriptPrintInstance):
        ep.apply( options=options, instance=instance )

    fname=None
    symbol_map=None
    if not options.save_model is None:
        if options.save_model == True:
            if options.format in (ProblemFormat.cpxlp, ProblemFormat.lpxlp):
                fname = (args[1])[:-3]+'lp'
            else:
                fname = (args[1])[:-3]+str(options.format)
            format=options.format
        else:
            fname = options.save_model
            format=None
        (fname, symbol_map) = instance.write(filename=fname, format=format)
        if not os.path.exists(fname):
            print "ERROR: file "+fname+" has not been created!"
        else:
            print "Model written to file '"+str(fname)+"'"
    for ep in ExtensionPoint(IPyomoScriptSaveInstance):
        ep.apply( options=options, instance=instance )

    return pyutilib.misc.Container(
        model=model, instance=instance, symbol_map=symbol_map, filename=fname )

#
# Perform optimization with concrete instance
#
def apply_optimizer(options, instance):
    #
    # Create Solver and Perform Optimization
    #
    solver = options.solver
    if solver is None:
       raise ValueError, "Problem constructing solver:  no solver specified"

    subsolver=None
    if not solver is None and ':' in solver:
        solver, subsolver = solver.split(':')
    opt = SolverFactory( solver )
    if opt is None:
        solver_list = SolverFactory.services()
        solver_list = sorted( filter(lambda x: '_' != x[0], solver_list) )
        raise ValueError, "Problem constructing solver `"+str(solver)+"' (choose from: %s)" % ", ".join(solver_list)

    # let the model know of our chosen solver's capabilities
    instance.has_capability = opt.has_capability

    opt.keepFiles=options.keepfiles or options.log
    if options.timelimit == 0:
       options.timelimit=None

    if options.solver_mipgap is not None:
       opt.mipgap = options.solver_mipgap

    if not options.solver_suffixes is None:
        opt.suffixes = options.solver_suffixes

    if not subsolver is None:
        subsolver=' solver='+subsolver
    else:
        subsolver=''

    if not options.solver_options is None:
        opt.set_options(" ".join(options.solver_options)+subsolver)

    if options.smanager_type is None:
        solver_mngr = SolverManagerFactory( 'serial' )
    else:
        solver_mngr = SolverManagerFactory( options.smanager_type )

    if solver_mngr is None:
        msg = "Problem constructing solver manager '%s'"
        raise ValueError, msg % str( options.smanager_type )

    results = solver_mngr.solve( instance, opt=opt, tee=options.tee, timelimit=options.timelimit )

    if results == None:
       raise ValueError, "opt.solve returned None"

    return results, opt

#
# Process results
#
def process_results(options, instance, results, opt):
    #
    if options.log:
       print ""
       print "=========================================================="
       print "Solver Logfile:",opt.log_file
       print "=========================================================="
       print ""
       INPUT = open(opt.log_file, "r")
       for line in INPUT:
         print line,
       INPUT.close()
    #
    ep = ExtensionPoint(IPyomoScriptPrintResults)
    if len(ep) == 0:
        try:
            instance.load(results)
        except Exception, e:
            print "Problem loading solver results"
            raise
        print ""
        results.write(num=1)
    #
    if options.summary:
       print ""
       print "=========================================================="
       print "Solution Summary"
       print "=========================================================="
       if len(results.solution(0).variable) > 0:
          print ""
          display(instance)
       else:
          print "No solutions reported by solver."
    #
    for ep in ExtensionPoint(IPyomoScriptPrintResults):
        ep.apply( options=options, instance=instance, results=results )
    #
    for ep in ExtensionPoint(IPyomoScriptSaveResults):
        ep.apply( options=options, instance=instance, results=results )
    #
    return True


def apply_postprocessing(options, instance, results):
    for file in options.postprocess:
        postprocess = pyutilib.misc.import_file(file)
        if "postprocess" in dir(postprocess):
            postprocess.postprocess(instance,results)
    for ep in ExtensionPoint(IPyomoScriptPostprocess):
        ep.apply( options=options, instance=instance, results=results )
    #
    # Deactivate and delete plugins
    #
    for plugin in options._usermodel_plugins:
        plugin.deactivate()
    options._usermodel_plugins = []


#
# Execute a function that processes command-line arguments and then
# calls a command-line driver.  This
# is segregated from the driver to enable profiling.
#
def run_command(command, parser, args=None, name='unknown'):
    #
    #
    # Parse command-line options
    #
    #
    try:
       (options, nargs) = parser.parse_args(args=args)
    except SystemExit:
       # the parser throws a system exit if "-h" is specified - catch
       # it to exit gracefully.
       return
    #
    # Setup I/O redirect to a logfile
    #
    logfile = getattr(options, 'logfile', None)
    if not logfile is None:
        pyutilib.misc.setup_redirect(logfile)
    #
    # Call the main Pyomo runner with profiling
    #
    if options.profile > 0:
        if not pstats_available:
            if not logfile is None:
                pyutilib.misc.reset_redirect()
            msg = "Cannot use the 'profile' option.  The Python 'pstats' "    \
                  'package cannot be imported!'
            raise ValueError, msg
        tfile = TempfileManager.create_tempfile(suffix=".profile")
        tmp = profile.runctx(
          command.__name__ + '(options=options,args=nargs,parser=parser)',
          globals(), locals(), tfile
        )
        p = pstats.Stats(tfile).strip_dirs()
        p.sort_stats('time', 'cum')
        options.profile = eval(options.profile)
        p = p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        p = p.sort_stats('cum','calls')
        p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        p = p.sort_stats('calls')
        p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        TempfileManager.clear_tempfiles()
        ans = [tmp, None]
    else:
        #
        # Call the main Pyomo runner without profiling
        #
        try:
            ans = command(options=options, args=nargs, parser=parser)
        except SystemExit, err:
            if pyomo.debug('errors'):
                sys.exit(0)
            print 'Exiting %s: %s' % (name, str(err))
            ans = None
        except Exception, err:
            if pyomo.debug('errors'):
                if not logfile is None:
                    pyutilib.misc.reset_redirect()
                raise
            #
            # This handles the case where the error is propagated by a KeyError.
            # KeyError likes to pass raw strings that don't handle newlines
            # (they translate "\n" to "\\n"), as well as tacking on single
            # quotes at either end of the error message. This undoes all that.
            #
            errStr = str(err)
            if type(err) == KeyError:
                errStr = str(err).replace(r"\n","\n")[1:-1]
            print "\nERROR:",errStr
            ans = None

    if not logfile is None:
        pyutilib.misc.reset_redirect()

    if options.disable_gc:
        gc.enable()
    return ans
