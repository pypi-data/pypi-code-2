from ConfigParser import ConfigParser
from optparse import OptionParser
import logging
import os, sys

def config(filename):
    cfgpath = os.path.abspath(filename)
    cfgfile = ConfigParser({ "here": os.path.dirname(cfgpath) })
    cfgfile.read(cfgpath)

    cfg = {}
    if cfgfile.has_section("app:main"):
        cfg.update(cfgfile.items("app:main"))
    return cfg

class Command(object):
    """
    (this class is copied from :module:`ordf.command`)

    This class is very similar to :class:`paste.script.command.Command` but
    rather than implementing a :program:`paster` plugin it is for stand-alone
    command line programs. To implement a command line program, sub-class this
    class, and make a minimal method to instantiate and run it. As with the
    paster counterpart you have to add an option parser and a method called
    :meth:`command`. A minimal example:

    .. code-block:: python

        class Hello(Command):
            parser = Command.StandardParser(usage="%prog [options]")
            def command(self):
                print "hello world"

        def hello():
            Hello().command()

    To create the actual script, in your package's *setup.py* needs an entry
    point like::

        [console_scripts]
        hello=mypackage.command:hello

    and then run one of::

        % python setup.py develop
        % python setup.py install
    """
    def __init__(self):
        self.parse_args()
        self.parse_config()
        self.setup_logging()

    @classmethod
    def StandardParser(cls, *av, **kw):
        parser = OptionParser(*av, **kw)
        parser.add_option("-c", "--config",
                          dest="config", default="development.ini",
                          help="configuration file (default: development.ini)")
        parser.add_option("-l", "--logfile",
                          dest="logfile", default=None,
                          help="log to file")
        parser.add_option("-v", "--verbosity",
                          dest="verbosity", default="info",
                          help="log verbosity. one of debug, info, warning, error, critical")
        return parser

    def parse_args(self):
        self.options, self.args = self.parser.parse_args()

    def parse_config(self):
        self.config = {}

        if self.options.config:
            cfg = config(self.options.config)
            self.config.update(cfg)

    def setup_logging(self):
        ## set up logging
        logcfg = {
            "level": logging.INFO,
            "format": "%(asctime)s %(levelname)s  [%(name)s] %(message)s",
            }
        if self.options.logfile:
            logcfg["filename"] = self.options.logfile
        if self.options.verbosity:
            levels = {
                "debug": logging.DEBUG,
                "info": logging.INFO,
                "warning": logging.WARNING,
                "error": logging.ERROR,
                "critical": logging.CRITICAL
                }
            logcfg["level"] = levels.get(self.options.verbosity, logging.NOTSET)
        logging.basicConfig(**logcfg)
