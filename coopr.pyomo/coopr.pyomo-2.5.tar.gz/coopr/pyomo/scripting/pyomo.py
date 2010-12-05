#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


from optparse import OptionParser, OptionGroup
from coopr.pyomo import pyomo
from coopr.opt.base import SolverFactory
from coopr.opt.parallel import SolverManagerFactory
from pyutilib.misc import Options, Container
try:
    import IPython
    IPython_available=True
    from IPython.Shell import IPShellEmbed
    ipshell = IPShellEmbed([''],
                banner = '\n# Dropping into Python interpreter',
                exit_msg = '\n# Leaving Interpreter, back to Pyomo\n')
except ImportError:
    IPython_available=False

import util

def create_parser():
    #
    #
    # Setup command-line options
    #
    #
    solver_help=\
    "This option specifies the type of solver that is used "\
    "to solve the Pyomo model instance.  The following solver "\
    "types are are currently supported:"
    solver_list = SolverFactory.services()
    solver_list = sorted( filter(lambda x: '_' != x[0], solver_list) )
    solver_help += " %s.  Default: glpk." % ', '.join(solver_list)
    debug_help=\
    "This option is used to turn on debugging output. This option "\
    "can be specified multiple times to turn on different debugging"\
    "output. The following debugging options can be specified:"
    debug_choices=[]
    for item in pyomo.Debug:
      if str(item) != "none":
         debug_choices.append( str(item) )
         debug_help += "\n.."+str(item)

    parser = OptionParser()
    parser.usage = 'pyomo [options] <model.py> [<model.dat>]'

    solverOpts = OptionGroup( parser, 'Solver Options')
    outputOpts = OptionGroup( parser, 'Output Options')
    otherOpts  = OptionGroup( parser, 'Other Options')
    parser.add_option_group( solverOpts )
    parser.add_option_group( outputOpts )
    parser.add_option_group( otherOpts )


    solverOpts.add_option('--instance-only',
        help='Generate a model instance, and then return',
        action='store_true',
        dest='only_instance',
        default=False)
    solverOpts.add_option('--model-name',
        help='The name of the model object that is created in the specified ' \
             'Pyomo module',
        action='store',
        dest='model_name',
        type='string',
        default='model')
    solverOpts.add_option('--model-options',
        help='Options passed into a create_model() function to construct the '\
             'model',
        action='append',
        dest='model_options',
        type='string',
        default=[])
    solverOpts.add_option('--postprocess',
        help='Specify a Python module that gets executed after optimization.' \
             'If this option is specified multiple times, then the modules '  \
             'are executed in the specified order.',
        action='append',
        dest='postprocess',
        default=[])
    solverOpts.add_option('--preprocess',
        help='Specify a Python module that gets immediately executed (before '\
             'the optimization model is setup).  If this option is specified '\
             'multiple times, then the modules are executed in the specified '\
             'order.',
        action='append',
        dest='preprocess',
        default=[])
    solverOpts.add_option('--solver',
        help=solver_help,
        action='store',
        dest='solver',
        type='string',
        #choices=solver_list,
        default='glpk')
    solverOpts.add_option('--solver-manager',
        help='Specify the technique that is used to manage solver executions.',
        action='store',
        dest='smanager_type',
        type='choice',
        choices=SolverManagerFactory.services(),
        default='serial')
    solverOpts.add_option('--solver-mipgap',
        help='The solver termination mipgap',
        action='store',
        dest='solver_mipgap',
        type='float',
        default=None)
    solverOpts.add_option('--solver-options',
        help='Options passed into the solver',
        action='append',
        dest='solver_options',
        type='string',
        default=[])
    solverOpts.add_option('--solver-suffixes',
        help='One or more solution suffixes to be extracted by the solver',
        action='append',
        dest='solver_suffixes',
        type='string',
        default=[])
    solverOpts.add_option('--timelimit',
        help='Limit to the number of seconds that the solver is run',
        action='store',
        dest='timelimit',
        type='int',
        default=0)
    solverOpts.add_option("--linearize-expressions",
        help="EXPERIMENTAL: An option intended for use on linear or mixed-integer models " \
             "in which expression trees in a model (constraints or objectives) are compacted " \
             "into a more memory-efficient and concise form. The trees themselves are eliminated. ",
        action="store_true",
        dest="linearize_expressions",
        default=False)

    outputOpts.add_option('--debug',
        help='This option is meant only for Pyomo developers.  Most users '   \
             'will want the --warning option.',
        action='append',
        dest='debug',
        type='choice',
        choices=debug_choices,
        default=[])
    outputOpts.add_option('-l','--log',
        help='Print the solver logfile after performing optimization',
        action='store_true',
        dest='log',
        default=False)
    outputOpts.add_option('--logfile',
        help='Redirect output to the specified logfile',
        action='store',
        dest='logfile',
        type='string',
        default=None)
    outputOpts.add_option('-q','--quiet',
        help='Turn off solver output',
        action='store_true',
        dest='quiet',
        default=False)
    outputOpts.add_option('--save-model',
        help='Specify the filename to which the model is saved.  The suffix ' \
             'of this filename specifies the file format.  If debugging is '  \
             "on, then this defaults to writing the file 'unknown.lp'.",
        action='store',
        dest='save_model',
        type='string',
        default=None)
    outputOpts.add_option('--stream-output',
        help='Stream the solver output to provide information about the '     \
             "solver's progress.",
        action='store_true',
        dest='tee',
        default=False)
    outputOpts.add_option('-s','--summary',
        help='Summarize the final solution after performing optimization',
        action='store_true',
        dest='summary',
        default=False)
    outputOpts.add_option('-v','--verbose',
        help='Make solver output verbose',
        action='store_true',
        dest='verbose',
        default=False)
    outputOpts.add_option('-w', '--warning',
        help='Warning level.  Use this option to set the level of '           \
             'informational output from Pyomo.  Levels include quiet, '       \
             'warning, and info.  Default: warning.',
        action='store',
        dest='warning',
        default='warning')

    otherOpts.add_option('--disable-gc',
        help='Disable the garbage collecter',
        action='store_true',
        dest='disable_gc',
        default=False)
    otherOpts.add_option('--help-components',
        help='Print information about modeling components supported by Pyomo',
        action='store_true',
        dest='help_components',
        default=False)
    otherOpts.add_option('--help-solvers',
        help='Print information about the solvers that are available',
        action='store_true',
        dest='help_solvers',
        default=False)
    otherOpts.add_option('-i', '--interactive',
        help='After executing Pyomo, launch an interactive Python shell.  If IPython is installed, this shell is an IPython shell.',
        action='store_true',
        dest='interactive',
        default=False)
    otherOpts.add_option('-k','--keepfiles',
        help='Keep temporary files',
        action='store_true',
        dest='keepfiles',
        default=False)
    otherOpts.add_option('--path',
        help='Give a path that is used to find the Pyomo python files',
        action='store',
        dest='path',
        type='string',
        default='.')
    otherOpts.add_option('--profile',
        help='Enable profiling of Python code.  The value of this option is ' \
             'the number of functions that are summarized.',
        action='store',
        dest='profile',
        type='int',
        default=0)
    otherOpts.add_option('--tempdir',
        help='Specify the directory where temporary files are generated',
        action='store',
        dest='tempdir',
        type='string',
        default=None)
    parser.add_option("--skip-canonical-repn",
            help="Do not create the canonical representation. This is not necessary for solvers that do not require it.",
            action="store_true",
            dest="skip_canonical_repn",
            default=False)
    #
    # These options are depricated until we have a specific use-case for them
    #
    ##if False:
    ##  parser.add_option("--seed",
    ##        help="Specify a seed to derandomize the solver",
    ##        action="store",
    ##        dest="seed",
    ##        type="int",
    ##        default=0)
    ##  parser.add_option("--first-feasible",
    ##        help="Terminate after the first feasible incumbent",
    ##        action="store_true",
    ##        dest="ff",
    ##        default=False)

    return parser


def run_pyomo(options=Options(), args=(), parser=None):
    if options.help_components:
        util.print_components(options)
        return Container()
    if options.help_solvers:
        util.print_solver_help(options)
        return Container()
    if not util.setup_environment(options, args):
        return Container()                                   #pragma:nocover
    if not util.apply_preprocessing(options, parser, args):
        return Container()                                   #pragma:nocover
    model_data = util.create_model(options, args)
    if options.save_model or options.only_instance:
        return Container(instance=model_data.instance)
    results, opt = util.apply_optimizer(options, model_data.instance)
    if not util.process_results(options, model_data.instance, results, opt):
        return Container(instance=model_data.instance, results=results) #pragma:nocover
    util.apply_postprocessing(options, model_data.instance, results)
    model=model_data.model
    instance=model_data.instance
    if options.interactive:
        if IPython_available:
            ipshell()
        else:
            import code
            shell = code.InteractiveConsole(locals())
            print '\n# Dropping into Python interpreter'
            shell.interact()
            print '\n# Leaving Interpreter, back to Pyomo\n'
    return Container(instance=model_data.instance, results=results)


def run(args=None):
    return util.run_command(run_pyomo, create_parser(), args=args, name='pyomo')

