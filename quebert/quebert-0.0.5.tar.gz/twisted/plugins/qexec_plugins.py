"""
Quebert Executor plugin for Quebert.
"""
from zope.interface import classProvides
from twisted.plugin import IPlugin
from twisted.python.usage import Options, UsageError
from twisted.python import reflect
from twisted.application.service import IServiceMaker

class QuExecutorPlugin(object):
    """
    This plugin eases the process of creating an executor
    using a Twisted Web server.
    """
    classProvides(IPlugin, IServiceMaker)

    tapname = "quexecutor"
    description = "Create an AMQP tasks executor"

    class options(Options):
        optParameters = [
            ["with_syslog_prefix", "p", None, "Activate syslog and give it the specified prefix (default will not use syslog)"],
            ["function", "f", None, "The function that will setup the listeners and executors"],
            ["port", "p", 8000, "The port on which the qexecutor should listen", int],
            ["subconfig", "s", "", "Optional configuration option for the subprocess", str]
        ]

        def postOptions(self):
            """
            Check and finalize the value of the arguments.
            """
            if self['function'] is None:
                raise UsageError("Must specify a setup function")
            try:
                self['function'] = reflect.namedAny(self['function'])
            except:
                raise UsageError("%s doesn't exist." % (self['function'],))

    @classmethod
    def makeService(cls, options):
        """
        Create an L{IService} for the parameters and return it
        """
        from quebert import service
        return service.makeExecutorService(options)
