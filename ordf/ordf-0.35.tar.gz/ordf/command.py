"""
.. program:: ordf

:program:`ordf`
===============

A command line program, :program:`ordf`, for running handlers and processing 
messages. This is somewhat of a swiss-army knife but some of the more
common use cases are described below.

.. cmdoption:: -c config.ini, --config config.ini

    Some command line options can be specified in the configuration file
    with a similar syntax. Other than for testing it is almost always going
    to be desirable to run with a configuration file.
    
    Any options given on the command line will override the corresponding
    configuration file parameters.

    The configuration file should have a section *[app:main]* for 
    compatibility with pylons configuration files. This configuration 
    section is passed to :func:`ordf.handler.init_handler`

.. cmdoption:: -r reader[,reader[...]], --readers reader[,reader[...]]

    A comma-separated list of reader plugins. Equivalent to *ordf.readers*
    in the configuration file.

.. cmdoption:: -w writer[,writer[...]], --writers writer[,writer[...]]

    A comma-separated list of writer plugins. Equivalent to *ordf.writers*
    in the configuration file.

.. cmdoption:: -l logfile, --logfile logfile

    A file to write log messages to.

.. cmdoption:: -v verbosity, --verbosity verbosity

    The minimum level of log messages to write to the file. Must be one of
    *debug, info, warning, error* or *critical*.

.. cmdoption:: -s, --save

    Save the arguments to the store.

.. cmdoption:: -x, --remove

    Remove the arguments from the store by replacing them with an empty graph.

.. cmdoption:: -f format, --format format

    For operations that involve reading RDF data, the format that it is in.
    This must be one of the formats supported by rdflib. The default is XML.

.. cmdoption:: -i uri, --identifier uri

    For operations that involve writing data to the store, the graph identifier 
    that should be the destination of the data. Default is the filename.

.. cmdoption:: -e sub, --edit sub

    For importing as opposed to copying a graph from a remote store, pass
    this sed(1) style substitution command. For example for development
    one might do:

    .. code-block:: sh

        ordf -c development.ini -s --nocs \
            -e 's@^http://.*bibliographica.org/@http://localhost:5000/@' \
            http://bnb.bibliographica.org/entry/GB6214539

    It is possible to set these options in the configuration file as well like
    so::

        ordf.edit = ['s@^http://.*bibliographica.org/@http://localhost:5000/@']

    Unless the `--noprov` flag is given, these edit operations are recorded
    in the provenance block of the imported graph.
    
.. cmdoption:: -u username, --user username

    Username for logging changes

.. cmdoption:: -m message, --message message

    Log message or change reason for logging changes

.. cmdoption:: -d, --daemon

    Run as a daemon, listening to a source and writing data to local storage.

.. cmdoption:: --reload

    Run in a reloading file monitor, reloading if changes to python code or
    configuration file are made.

.. cmdoption:: --reindex

    Rebuild indices iterating over a single reader

.. program:: ordf_load

:program:`ordf_load`
=======================

Utility program for loading any RDF fixtures that are packaged with some
python modules. Normal usage is as in::

    % ordf_load -p ordf.vocab
    INFO  [ordf.handler] Handler(0/0) initialised ver 0.7.246.1a3933607282
    INFO  [ordf.handler] Handler(1/0) reading from <ordf.handler.pt.PairTree object ...>
    INFO  [ordf.handler] Handler(1/1) writing to <ordf.handler.pt.PairTree object ...>
    INFO  [ordf.handler.rdf.RDFLib] Initialising Sleepycat storage
    INFO  [ordf.handler] Handler(1/2) writing to <ordf.handler.rdf.RDFLib object ...>
    INFO  [ordf.load/3149] Loading http://ordf.org/schema/ordf
    INFO  [ordf.changeset] 20 changes urn:uuid:44764ed0-8d12-11df-acde-001f5bef60ee

    % ordf_load -p ordf.onto
    INFO  [ordf.handler] Handler(0/0) initialised ver 0.7.246.1a3933607282
    INFO  [ordf.handler] Handler(1/0) reading from <ordf.handler.pt.PairTree ...>
    INFO  [ordf.handler] Handler(1/1) writing to <ordf.handler.pt.PairTree ...>
    INFO  [ordf.handler.rdf.RDFLib] Initialising Sleepycat storage
    INFO  [ordf.handler] Handler(1/2) writing to <ordf.handler.rdf.RDFLib ...>
    INFO  [ordf.load/3148] Loading http://ordf.org/lens/changeset
    INFO  [ordf.load/3148] Loading http://ordf.org/lens/fresnel
    INFO  [ordf.load/3148] Loading http://ordf.org/lens/ontology
    INFO  [ordf.load/3148] Loading http://ordf.org/lens/rdfs
    INFO  [ordf.changeset] 612 changes urn:uuid:171ffd8c-8d12-11df-850a-001f5bef60ee

In addition to the *-c* for specifying the config file, *-l* and *-v*
for log file and debugging, and *-r* and *-w* for specifying readers and
writers as with :program:`ordf`, :program:`ordf_load` supports these
arguments:

.. cmdoption:: -p, --package

    Name of the package (python module) to look for N3 fixtures in. This
    doesn't work with namespace packages (e.g. ordf itself which is why
    the schema fixtures are in the ordf.vocab sub-module).

Command Implementation -- :class:`Command`
==========================================

.. autoclass:: Command
"""
from ordf.graph import Graph
from ordf.handler import init_handler
from ordf.namespace import RDF, RDFS
from ordf.term import Literal, URIRef
from ordf.vocab.opmv import Agent, Process
from optparse import OptionParser
from ConfigParser import ConfigParser
from getpass import getuser
from paste import reloader
from glob import glob
import subprocess, signal
import pkg_resources
import os, sys
import urllib
import logging
import sys
import re

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
        self.setup_handler()

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
            "format": "%(levelname)s  [%(name)s] %(message)s"
            }
        if self.options.logfile:
            logcfg["filename"] = self.options.logfile
            logcfg["format"] = "%(asctime)s %(levelname)s  [%(name)s] %(message)s"
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

    def setup_handler(self):
        self.handler = init_handler(self.config)

class ORDF(Command):
    usage = "Usage: %prog [options] [files...]"
    _reloader_environ_key = 'PYTHON_RELOADER_SHOULD_RUN'
    parser = Command.StandardParser(usage=usage)
    parser.add_option("-r", "--readers",
                       dest="readers", default=None,
                       help="comma separated list of reader plugins")
    parser.add_option("-w", "--writers",
                       dest="writers", default=None,
                       help="comma separated list of writer plugins")
    parser.add_option("-s", "--save", action="store_true",
                       dest="save", default=False,
                       help="save the arguments to the store")
    parser.add_option("-f", "--format",
                       dest="format", default="xml",
                       help="format of rdf files for read operations. default XML")
    parser.add_option("-i", "--identifier",
                       dest="identifier", default=None,
                       help="the graph uri to store the data")
    parser.add_option("-u", "--user",
                       dest="user", default=None,
                       help="username for logging. defaults to environment")
    parser.add_option("-m", "--message",
                       dest="message", default=None,
                       help="change message for logging")
    parser.add_option("-x", "--remove", action="store_true",
                        dest="remove", default=False,
                        help="remove graph from store")
    parser.add_option("-d", "--daemon", action="store_true",
                       dest="daemon", default=False,
                       help="Do not exit, loop and process messages")
    parser.add_option("--reload", action="store_true",
                       dest="reload", default=False,
                       help="Check files for changes and reload")
    parser.add_option("--reindex", action="store_true",
                       dest="reindex", default=False,
                       help="Reindex indices reading from a single reader")
    parser.add_option("--nocs", action="store_true",
                      dest="nocs", default=False,
                      help="Do not process changesets")
    parser.add_option("--noprov", action="store_true",
                      dest="noprov", default=False,
                      help="Do not store provenance information")
    parser.add_option("-e", "--edit", action="append", dest="edit",
                      default=[], help="Transform URIs according to the given sed-like regexp")
    def parse_config(self):
        super(ORDF, self).parse_config()

        ## override config with the command line
        if self.options.readers:
            self.config["ordf.readers"] = self.options.readers
        if self.options.writers:
            self.config["ordf.writers"] = self.options.writers

        if not self.options.nocs:
            if self.options.save or self.options.remove:
                if not self.options.message:
                    self.parser.print_help()
                    print "ERROR: missing log message"
                    exit(1)

        regexps = self.config.get("ordf.edit")
        if regexps is not None:
            self.config["ordf.edit"] = eval(regexps)
        else:
            self.config["ordf.edit"] = []
        if self.options.edit != []:
            self.config["ordf.edit"] = self.options.edit
            
        if self.options.reindex:
            reader = self.config.get("ordf.readers")
            if reader.find(",") >= 0:
                print "--reindex requires exactly one reader (-r/--readers)"
                exit(1)
            self.reindex_reader = reader

    def setup_logging(self):
        super(ORDF, self).setup_logging()
        self.log = logging.getLogger("ordf.command/%s" % os.getpid())

    def command(self):
        self.compile_edit()

        if self.options.reload:
            if os.environ.get(self._reloader_environ_key):
                self.log.debug("using reloading file monitor")
                reloader.install(1)
                if self.options.config:
                    reloader.watch_file(self.options.config)
            else:
                return self.restart_with_reloader()

        if self.options.save or self.options.remove:
            if self.options.user:
                user = self.options.user
            else:
                user = getuser()

            if not self.options.nocs:
                ctx = self.handler.context(user, self.options.message)

            agent = Agent()
            agent.nick(Literal(user))

            for filename in self.args:

                if self.options.identifier:
                    ident = URIRef(self.options.identifier)
                else:
                    proto, rest = urllib.splittype(filename)
                    if proto:
                        ident = URIRef(filename)
                    else:
                        ident = URIRef("file://" + os.path.abspath(filename))
                    ident = self.edit(ident)
                
                g = Graph(identifier=ident)
                
                if self.options.save:
                    ingraph = Graph()
                    ingraph.parse(filename, format=self.options.format)
                    for s, p, o in ingraph.triples((None, None, None)):
                        if isinstance(s, URIRef):
                            s = self.edit(s)
                        if isinstance(o, URIRef):
                            o = self.edit(o)
                        g.add((s, p, o))
                    
                    if not self.options.noprov:
                        proc = Process()
                        proc.agent(agent)
                        proto, rest = urllib.splittype(filename)
        
                        if proto:
                            src = URIRef(filename)
                        else:
                            src = URIRef("file://" + os.path.abspath(filename))
                        proc.use(src)
                        if self.config["ordf.edit"] != []:
                            proc.add((proc.identifier, RDFS["comment"],
                                      Literal("\n".join(self.config["ordf.edit"]))))
                        proc.result(g)

                    self.log.info("add %s" % (g.identifier,))
                    if self.options.nocs:
                        self.handler.put(g)

                elif self.options.remove:
                    self.log.info("del %s" % (g.identifier,))
                    if self.options.nocs:
                        self.handler.remove(g)

                if not self.options.nocs:
                    ctx.add(g)

            if not self.options.nocs:
                self.log.info("commit changes")
                cs = ctx.commit()

        elif self.options.reindex:
            reader = getattr(self.handler, self.reindex_reader)
            for graph in reader:
                self.log.info("indexing %s" % graph.identifier)
                self.handler.put(graph)
        else:
            for uri in self.args:
                g = self.handler.get(uri)
                print g.serialize(format=self.options.format)
        
        def _daemon():
            from time import sleep
            try:
                while True:
                    sleep(1)
            except KeyboardInterrupt:
                pass

        if self.options.daemon:
            _daemon()
        self.handler.close()

    def compile_edit(self):
        self._edit = []
        def err(reason):
                self.log.error("invalid substitution: %s (%s)", subst, reason)
                self.log.error("must be of the form s@pattern@replacement@")
                sys.exit(255)

        for subst in self.config["ordf.edit"]:
            if not subst.startswith("s"): err("does not start with s")
            if len(subst) < 4: err("too short")
            sep = subst[1]
            if sep == '\\': err("escape character is not a valid separator")
            if subst[-1] != sep: err("wrong end character")
            pat_start = 2
            pat_end = -1
            for i in range(2, len(subst)-1):
                if subst[i] == sep and subst[i-1] != '\\':
                    pat_end = i
                    break
            if pat_end < 0: err("could not find end of pattern")
            pattern = subst[pat_start:pat_end]
            repl_start = pat_end+1
            replace = subst[pat_end+1:-1]
            if len(replace) > 0 and replace[-1] == '\\': err("last character is escaped")
            if len(pattern) == 0: err("no pattern")

            try:
                compiled = re.compile(pattern)
                self._edit.append((compiled, replace))
            except Exception, e:
                err("invalid regular expression: %s" % e)

    def edit(self, uri):
        for pattern, replace in self._edit:
            uri = pattern.sub(replace, uri)
        return URIRef(uri)
    
    def restart_with_reloader(self):
        while 1:
            args = [sys.executable] + sys.argv
            new_environ = os.environ.copy()
            new_environ[self._reloader_environ_key] = 'true'
            proc = None
            try:
                try:
                    def handle_term(signo, frame):
                        raise SystemExit
                    signal.signal(signal.SIGTERM, handle_term)
                    proc = subprocess.Popen(args, env=new_environ)
                    self.log.debug("started child process %s" % proc.pid)
                    exit_code = proc.wait()
                    proc = None
                except KeyboardInterrupt:
                    self.log.info('^C caught in monitor process')
                    return 1
            finally:
                if (proc is not None
                    and hasattr(os, 'kill')):
                    try:
                        os.kill(proc.pid, signal.SIGTERM)
                    except (OSError, IOError):
                        pass
            if exit_code != 3:
                return exit_code
            self.log.info('-'*20 + ' Restarting ' + '-'*20)

class ORDF_LOAD(Command):
    usage = "%prog [options]"
    parser = Command.StandardParser(usage=usage)
    parser.add_option("-p", "--package",
                      dest="package_name",
                      default="ordf.vocab",
                      help="Package name to read N3 fixtures from (default: ordf.vocab) " +
                           "-- does not work for namespace packages")
    parser.add_option("--nocs",
                      dest="nocs",
                      action="store_true",
                      default=False,
                      help="Put data directly into store without changeset")
    parser.add_option("-r", "--readers",
                       dest="readers", default=None,
                       help="comma separated list of reader plugins")
    parser.add_option("-w", "--writers",
                       dest="writers", default=None,
                       help="comma separated list of writer plugins")

    def parse_config(self):
        super(ORDF_LOAD, self).parse_config()

        ## override config with the command line
        if self.options.readers:
            self.config["ordf.readers"] = self.options.readers
        if self.options.writers:
            self.config["ordf.writers"] = self.options.writers

    def setup_logging(self):
        super(ORDF_LOAD, self).setup_logging()
        self.log = logging.getLogger("ordf.load/%s" % os.getpid())

    def command(self):
        pkg = __import__(self.options.package_name, globals(), locals(), ["version"])

        ctx = self.handler.context(getuser(), "ORDF N3 Import")

        if hasattr(pkg, "rdf_data"):
            for graph in pkg.rdf_data():
                label = graph.one((graph.identifier, RDFS["label"], None))
                if label is not None:
                    self.log.info("Loading %s (%s)" % (graph.identifier, label[2]))
                else:
                    self.log.info("Loading %s" % (graph.identifier,))
                if self.options.nocs:
                    self.handler.put(graph)
                else:
                    ctx.add(graph)

        if not self.options.nocs:
            ctx.commit()

def ordf():
    ORDF().command()

def load_rdf():
    ORDF_LOAD().command()
