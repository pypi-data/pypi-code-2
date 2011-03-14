#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import gc
import logging
import os
import sys
import textwrap
import traceback
import types
import time

try:
    import cProfile as profile
except ImportError:
    import profile
try:
    import pstats
    pstats_available=True
except ImportError:
    pstats_available=False

try:
    import IPython
    IPython_available=True
    from IPython.Shell import IPShellEmbed
    ipshell = IPShellEmbed([''],
                banner = '\n# Dropping into Python interpreter',
                exit_msg = '\n# Leaving Interpreter, back to Pyomo\n')
except ImportError:
    IPython_available=False

from pyutilib.misc import Options
try:
   from pympler.muppy import muppy
   from pympler.muppy import summary
   from pympler.muppy import tracker
   from pympler.asizeof import *
   pympler_available = True
except ImportError:
   pympler_available = False
memory_tracker = None
memory_data = Options()

from coopr.pyomo import *
from coopr.opt import ProblemFormat
from coopr.opt.base import SolverFactory
from coopr.opt.parallel import SolverManagerFactory
import pyutilib.misc
from pyutilib.component.core import ExtensionPoint, Plugin, implements
from pyutilib.services import TempfileManager

from coopr.pyomo.expr.linear_repn import linearize_model_expressions

filter_excepthook=False
modelapi = {    'pyomo_create_model':IPyomoScriptCreateModel,
                'pyomo_create_modeldata':IPyomoScriptCreateModelData,
                'pyomo_print_model':IPyomoScriptPrintModel,
                'pyomo_modify_instance':IPyomoScriptModifyInstance,
                'pyomo_print_instance':IPyomoScriptPrintInstance,
                'pyomo_save_instance':IPyomoScriptSaveInstance,
                'pyomo_print_results':IPyomoScriptPrintResults,
                'pyomo_save_results':IPyomoScriptSaveResults,
                'pyomo_postprocess':IPyomoScriptPostprocess}


logger = logging.getLogger('coopr.pyomo')
start_time = 0.0

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
def setup_environment(options):
    #
    global start_time
    start_time = time.time()
    if not options.quiet:
        sys.stdout.write('- Setting up Pyomo environment                                       [%8.2f]\n' % 0.0)
        sys.stdout.flush()
    #
    # Setup memory tracker
    #
    if (pympler_available is True) and (options.profile_memory >= 1):
        global memory_tracker
        memory_tracker = tracker.SummaryTracker()
    #
    # Disable garbage collection
    #
    if options.disable_gc:
        gc.disable()
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
        if len(options.model_file) > 0:
            name = "model " + options.model_file
        else:
            name = "model"


        if filter_excepthook:
            action = "loading"
        else:
            action = "running"

        msg = "Unexpected exception while %s %s\n" % (action, name)

        #
        # This handles the case where the error is propagated by a KeyError.
        # KeyError likes to pass raw strings that don't handle newlines
        # (they translate "\n" to "\\n"), as well as tacking on single
        # quotes at either end of the error message. This undoes all that.
        #
        if etype == KeyError:
            valueStr = str(value).replace("\\n","\n")[1:-1]
        else:
            valueStr = str(value)

        logger.error(msg+valueStr)
        
        tb_list = traceback.extract_tb(tb,None)
        i = 0
        if not logger.isEnabledFor(logging.DEBUG) and filter_excepthook:
            while i < len(tb_list):
                #print "Y",model,tb_list[i][0]
                if options.model_file in tb_list[i][0]:
                    break
                i += 1
            if i == len(tb_list):
                i = 0
        print "\nTraceback (most recent call last):"
        for item in tb_list[i:]:
            print "  File \""+item[0]+"\", line "+str(item[1])+", in "+item[2]
            if item[3] is not None:
                print "    "+item[3]
        sys.exit(1)
    sys.excepthook = pyomo_excepthook
    # 
    return True


#
# Execute preprocessing files
#
def apply_preprocessing(options, parser):
    #
    if not options.quiet:
        sys.stdout.write('- Applying Pyomo preprocessing actions                               [%8.2f]\n' % (time.time()-start_time))
        sys.stdout.flush()
    #
    global filter_excepthook
    #
    #
    # Setup solver and model
    #
    #
    if len(options.model_file) == 0:
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
    options.usermodel = pyutilib.misc.import_file(options.model_file)
    filter_excepthook=False

    usermodel_dir = dir(options.usermodel)
    options._usermodel_plugins = []
    for key in modelapi:
        if key in usermodel_dir:
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
            raise SystemExit, msg % options.model_file
        getattr(options.usermodel, 'pyomo_preprocess')( options=options )

    return True

#
# Create instance of Pyomo model
#
def create_model(options):
    #
    if not options.quiet:
        sys.stdout.write('- Creating model                                                     [%8.2f]\n' % (time.time()-start_time))
        sys.stdout.flush()
    #
    if (pympler_available is True) and (options.profile_memory >= 1):
        global memory_data
        objects_before_instance_creation = muppy.get_objects()
        memory_data.summary_before_instance_creation = summary.summarize(objects_before_instance_creation)
        print "Initial set of objects:"
        summary.print_(memory_data.summary_before_instance_creation,limit=50)
    #
    # Verify that files exist
    #
    for file in [options.model_file]+options.data_files:
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
            raise SystemExit, msg % options.model_file
        model = getattr(options.usermodel, model_name)

        if model is None:
            msg = "'%s' object is 'None' in module %s"
            raise SystemExit, msg % (model_name, options.model_file)
            sys.exit(0)

    else:
       if len(ep) == 0:
           msg = "Neither '%s' nor 'pyomo_create_model' are available in "    \
                 'module %s'
           raise SystemExit, msg % ( model_name, options.model_file )
       elif len(ep) > 1:
           msg = 'Multiple model construction plugins have been registered!'
           raise SystemExit, msg
       else:
            model_options = options.model_options
            if model_options is None:
                model_options = []
            model = ep.service().apply( options=pyutilib.misc.Container(*model_options) )
    #
    for ep in ExtensionPoint(IPyomoScriptPrintModel):
        ep.apply( options=options, model=model )

    #
    # Disable canonical repn for ASL solvers, and if the user has specified as such (in which case, we assume they know what they are doing!).
    #
    # Likely we need to change the framework so that canonical repn
    # is not assumed to be required by all solvers?
    #
    if not options.solver is None and options.solver.startswith('asl'):
        model.skip_canonical_repn = True
    elif options.skip_canonical_repn is True:
        model.skip_canonical_repn = True

    #
    # Create Problem Instance
    #
    ep = ExtensionPoint(IPyomoScriptCreateModelData)
    if len(ep) > 1:
        msg = 'Multiple model data construction plugins have been registered!'
        raise SystemExit, msg

    if len(ep) == 1:
        modeldata = ep.service().apply( options=options, model=model )
    else:
        modeldata = ModelData()

    if len(options.data_files) > 1:
        #
        # Load a list of *.dat files
        #
        for file in options.data_files:
            suffix = (file).split(".")[-1]
            if suffix != "dat":
                msg = 'When specifiying multiple data files, they must all '  \
                      'be *.dat files.  File specified: %s'
                raise SystemExit, msg % str( file )

            modeldata.add(file)

        modeldata.read(model)

        if not options.profile_memory is None:
           instance = model.create(modeldata, profile_memory=options.profile_memory)
        else:
           instance = model.create(modeldata)

    elif len(options.data_files) == 1:
       #
       # Load a *.dat file or process a *.py data file
       #
       suffix = (options.data_files[0]).split(".")[-1]
       if suffix == "dat":
          if not options.profile_memory is None:
             instance = model.create(options.data_files[0], profile_memory=options.profile_memory)
          else:
             instance = model.create(options.data_files[0])
       elif suffix == "py":
          userdata = pyutilib.misc.import_file(options.data_files[0])
          if "modeldata" in dir(userdata):
                if len(ep) == 1:
                    msg = "Cannot apply 'pyomo_create_modeldata' and use the" \
                          " 'modeldata' object that is provided in the model"
                    raise SystemExit, msg

                if userdata.modeldata is None:
                    msg = "'modeldata' object is 'None' in module %s"
                    raise SystemExit, msg % str( options.data_files[0] )

                modeldata=userdata.modeldata

          else:
                if len(ep) == 0:
                    msg = "Neither 'modeldata' nor 'pyomo_create_model_data"  \
                          'is defined in module %s'
                    raise SystemExit, msg % str( options.data_files[0] )

          modeldata.read(model)
          if not options.profile_memory is None:
             instance = model.create(modeldata, profile_memory=options.profile_memory)
          else:
             instance = model.create(modeldata)
       else:
          raise ValueError, "Unknown data file type: "+options.data_files[0]
    else:
       if not options.profile_memory is None:
          instance = model.create(modeldata, profile_memory=options.profile_memory)
       else:
          instance = model.create(modeldata)

    if options.linearize_expressions is True:
       linearize_model_expressions(instance)

    #
    ep = ExtensionPoint(IPyomoScriptModifyInstance)
    for ep in ExtensionPoint(IPyomoScriptModifyInstance):
        ep.apply( options=options, model=model, instance=instance )
    #
    if logger.isEnabledFor(logging.DEBUG):
       print "MODEL INSTANCE"
       instance.pprint()
       print ""

    for ep in ExtensionPoint(IPyomoScriptPrintInstance):
        ep.apply( options=options, instance=instance )

    fname=None
    symbol_map=None
    if options.save_model is None and options.debug:
        options.save_model = 'unknown.lp'
    if not options.save_model is None:
        if options.save_model == True:
            if options.format in (ProblemFormat.cpxlp, ProblemFormat.lpxlp):
                fname = (options.data_files[0])[:-3]+'lp'
            else:
                fname = (options.data_files[0])[:-3]+str(options.format)
            format=options.format
        else:
            fname = options.save_model
            format=None
        (fname, symbol_map) = instance.write(filename=fname, format=format)
        if not options.quiet:
            if not os.path.exists(fname):
                print "ERROR: file "+fname+" has not been created!"
            else:
                print "Model written to file '"+str(fname)+"'"
    for ep in ExtensionPoint(IPyomoScriptSaveInstance):
        ep.apply( options=options, instance=instance )

    if (pympler_available is True) and (options.profile_memory >= 1):
        objects_after_instance_creation = muppy.get_objects()
        memory_data.summary_after_instance_creation = summary.summarize(objects_after_instance_creation)
        print "\nObjects created during Pyomo instance creation:"
        memory_tracker.print_diff(
                    summary1=memory_data.summary_before_instance_creation, 
                    summary2=memory_data.summary_after_instance_creation)

    return pyutilib.misc.Container( 
                    model=model, instance=instance, 
                    symbol_map=symbol_map, filename=fname )

#
# Perform optimization with concrete instance
#
def apply_optimizer(options, instance):
    #
    if not options.quiet:
        sys.stdout.write('- Applying solver                                                    [%8.2f]\n' % (time.time()-start_time))
        sys.stdout.flush()
    #
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

    if (pympler_available is True) and (options.profile_memory >= 1):
        global memory_data
        objects_after_optimization = muppy.get_objects()
        memory_data.summary_after_optimization = summary.summarize(objects_after_optimization)
        print "\nObjects created during optimization:"
        memory_tracker.print_diff(
                    summary1=memory_data.summary_after_instance_creation,
                    summary2=memory_data.summary_after_optimization)

    return results, opt

#
# Process results
#
def process_results(options, instance, results, opt):
    #
    if not options.quiet:
        sys.stdout.write('- Processing results                                                 [%8.2f]\n' % (time.time()-start_time))
        sys.stdout.flush()
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
    try:
        instance.update_results(results)
    except Exception, e:
        print "Problem loading solver results"
        raise
    #
    if not options.show_results:
        if options.save_results:
            results_file = options.save_results
        else:
            results_file = 'results.yml'
        results.write(filename=results_file)
        print "    Number of solutions:", len(results.solution)
        if len(results.solution) > 0:
            print "    Solution Information"
            print "      Gap:",results.solution[0].gap
            print "      Status:",results.solution[0].status
            if len(results.solution[0].objective) == 1:
                key = results.solution[0].objective.keys()[0]
                print "      Function Value:",results.solution[0].objective[key].value
        print "    Solver results file:",results_file
    else:
        ep = ExtensionPoint(IPyomoScriptPrintResults)
        if len(ep) == 0:
            try:
                instance.load(results)
            except Exception, e:
                print "Problem loading solver results"
                raise
            print ""
            results.write(num=1)
            print ""
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
    if (pympler_available is True) and (options.profile_memory >= 1):
        global memory_data
        objects_after_results_processing = muppy.get_objects()
        memory_data.summary_after_results_processing = summary.summarize(objects_after_results_processing)
        #diff_summary = summary.get_diff( memory_data.summary_after_optimization, memory_data.summary_after_results_processing)
        print "\nObjects created during results processing:"
        memory_tracker.print_diff(
                    summary1=memory_data.summary_after_optimization,
                    summary2=memory_data.summary_after_results_processing)

    return True


def apply_postprocessing(options, instance, results):
    #
    if not options.quiet:
        sys.stdout.write('- Applying Pyomo postprocessing actions                              [%8.2f]\n' % (time.time()-start_time))
        sys.stdout.flush()
    #
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
    if (pympler_available is True) and (options.profile_memory >= 1):
        final_objects = muppy.get_objects()
        summary_final = summary.summarize(final_objects)
        final_summary = summary.summarize(final_objects)
        print "\nFinal set of objects:"
        summary.print_(final_summary, limit=50)
    #
    return True


def finalize(options, model=None, instance=None, results=None):
    #
    if not options.quiet:
        sys.stdout.write('- Pyomo Finished                                                     [%8.2f]\n' % (time.time()-start_time))
        sys.stdout.flush()
    #
    model=model
    instance=instance
    results=results
    #
    if options.interactive:
        if IPython_available:
            ipshell()
        else:
            import code
            shell = code.InteractiveConsole(locals())
            print '\n# Dropping into Python interpreter'
            shell.interact()
            print '\n# Leaving Interpreter, back to Pyomo\n'


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
       _options = parser.parse_args(args=args)
       # Replace the parser options object with a pyutilib.misc.Options object
       options = pyutilib.misc.Options()
       for key in dir(_options):
            if key[0] != '_':
                val = getattr(_options, key)
                if not isinstance(val, types.MethodType):
                    options[key] = val
    except SystemExit:
       # the parser throws a system exit if "-h" is specified - catch
       # it to exit gracefully.
       return
    #
    # Configure the logger
    #
    logging.getLogger('coopr.pyomo').setLevel(logging.ERROR)
    logging.getLogger('coopr').setLevel(logging.ERROR)
    logging.getLogger('pyutilib').setLevel(logging.ERROR)
    #
    if options.warning:
        logging.getLogger('coopr.pyomo').setLevel(logging.WARNING)
        logging.getLogger('coopr').setLevel(logging.WARNING)
        logging.getLogger('pyutilib').setLevel(logging.WARNING)
    if options.info:
        logging.getLogger('coopr.pyomo').setLevel(logging.INFO)
        logging.getLogger('coopr').setLevel(logging.INFO)
        logging.getLogger('pyutilib').setLevel(logging.INFO)
    if options.verbose > 0:
        if options.verbose >= 1:
            logger.setLevel(logging.DEBUG)
        if options.verbose >= 2:
            logging.getLogger('coopr').setLevel(logging.DEBUG)
        if options.verbose >= 3:
            logging.getLogger('pyutilib').setLevel(logging.DEBUG)
    if options.debug:
        logging.getLogger('coopr.pyomo').setLevel(logging.DEBUG)
        logging.getLogger('coopr').setLevel(logging.DEBUG)
        logging.getLogger('pyutilib').setLevel(logging.DEBUG)
    if options.logfile:
        logging.getLogger('coopr.pyomo').handlers = []
        logging.getLogger('coopr').handlers = []
        logging.getLogger('pyutilib').handlers = []
        logging.getLogger('coopr.pyomo').addHandler( logging.FileHandler(options.logfile, 'w'))
        logging.getLogger('coopr').addHandler( logging.FileHandler(options.logfile, 'w'))
        logging.getLogger('pyutilib').addHandler( logging.FileHandler(options.logfile, 'w'))
    #
    # Setup I/O redirect to a file
    #
    logfile = getattr(options, 'output', None)
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
          command.__name__ + '(options=options,parser=parser)', command.__globals__, locals(), tfile
        )
        p = pstats.Stats(tfile).strip_dirs()
        p.sort_stats('time', 'cum')
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
            ans = command(options=options, parser=parser)
        except SystemExit, err:
            if __debug__:
                if options.debug or options.catch:
                    sys.exit(0)
            print 'Exiting %s: %s' % (name, str(err))
            ans = None
        except Exception, err:
            # If debugging is enabled, pass the exception up the chain
            # (to pyomo_excepthook)
            if __debug__:
                if options.debug or options.catch:
                    if not logfile is None:
                        pyutilib.misc.reset_redirect()
                    raise

            if len(options.model_file) > 0:
                name = "model " + options.model_file
            else:
                name = "model"
                
            global filter_excepthook
            if filter_excepthook:
                action = "loading"
            else:
                action = "running"

            msg = "Unexpected exception while %s %s\n" % (action, name)
            #
            # This handles the case where the error is propagated by a KeyError.
            # KeyError likes to pass raw strings that don't handle newlines
            # (they translate "\n" to "\\n"), as well as tacking on single
            # quotes at either end of the error message. This undoes all that.
            #
            errStr = str(err)
            if type(err) == KeyError:
                errStr = str(err).replace(r"\n","\n")[1:-1]

            logging.getLogger('coopr.pyomo').error(msg+errStr)
            ans = None

    if not logfile is None:
        pyutilib.misc.reset_redirect()

    if options.disable_gc:
        gc.enable()
    return ans
