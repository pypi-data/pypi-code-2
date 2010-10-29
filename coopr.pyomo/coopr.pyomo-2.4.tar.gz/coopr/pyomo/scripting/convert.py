#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['pyomo2lp', 'pyomo2nl']


from optparse import OptionParser
from coopr.pyomo import pyomo
from coopr.opt import ProblemFormat
from coopr.opt.base import SolverFactory
from pyutilib.misc import Options, Container

import util

def create_parser(name):
    #
    #
    # Setup command-line options
    #
    #
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
    parser.add_option("--path",
        help="Give a path that is used to find the Pyomo python files",
        action="store",
        dest="path",
        type="string",
        default=".")
    parser.add_option("--help-components",
            help="Print information about modeling components supported by Pyomo",
            action="store_true",
            dest="help_components",
            default=False)
    parser.add_option("--debug",
            help=debug_help,
            action="append",
            dest="debug",
            choices=debug_choices)
    parser.add_option("-k","--keepfiles",
            help="Keep temporary files",
            action="store_true",
            dest="keepfiles",
            default=False)
    parser.add_option("--tempdir",
            help="Specify the directory where temporary files are generated",
            action="store",
            dest="tempdir",
            default=None)
    parser.add_option("-q","--quiet",
            help="Turn off solver output",
            action="store_true",
            dest="quiet",
            default=False)
    parser.add_option("--logfile",
            help="Redirect output to the specified logfile",
            action="store",
            dest="logfile",
            default=None)
    parser.add_option("--profile",
            help="Enable profiling of Python code.  The value of this option is the number of functions that are summarized.",
            action="store",
            dest="profile",
            default=0)
    parser.add_option("--preprocess",
            help="Specify a Python module that gets immediately executed (before the optimization model is setup).  If this option is specified multiple times, then the modules are executed in the specified order.",
            action="append",
            dest="preprocess",
            default=[])
    parser.add_option("--model-name",
            help="The name of the model object that is created in the specified Pyomo module",
            action="store",
            dest="model_name",
            type="string",
            default="model")
    parser.add_option("--model-options",
            help="Options passed into a create_model() function to construct the model",
            action="append",
            dest="model_options",
            type="string",
            default=[])
    parser.add_option("--disable-gc",
            help="Disable the garbage collecter",
            action="store_true",
            dest="disable_gc",
            default=False)
    parser.add_option("--save-model",
            help="Specify the filename to which the model is saved.  The suffix of this filename specifies the file format.  If debugging is on, then this defaults to writing the file 'unknown.lp'.",
            action="store",
            dest="save_model",
            default=True)

    parser.usage=name+" [options] <model.py> [<model.dat>]"
    return parser


format = None

def convert(options=Options(), args=(), parser=None):
    global format
    options.verbose = False
    options.format = format
    if options.help_components:
        util.print_components(options)
        return Container()
    if not util.setup_environment(options, args):
        return                                               #pragma:nocover
    if not util.apply_preprocessing(options, parser, args):
        return
    model = util.create_model(options, args)
    return model

def pyomo2lp(args=None):
    global format
    parser = create_parser('pyomo2lp')
    format = ProblemFormat.cpxlp
    return util.run_command(convert, parser, args=args, name='pyomo2lp')

def pyomo2nl(args=None):
    global format
    parser = create_parser('pyomo2nl')
    format = ProblemFormat.nl
    return util.run_command(convert, parser, args=args, name='pyomo2nl')

