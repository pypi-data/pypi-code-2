"""\
Base classes for the different types of Pipe
"""

import getopt
import logging
from bn import AttributeDict

log = logging.getLogger(__name__)

class Pipe(object):
    """\
    Pipes can be implemented using classes as well as nested functions. 

    This ``Pipe`` class is designed to be used as a base class for other 
    classes. The derived classes should implement the ``enter()`` and 
    ``leave()`` methods.

    Pipes are used in a ``Site`` object combined with the ``pipe()``  
    function. They each have a name which is passed to ``pipe()`` and 
    can specify some aliases for other pipes they use. The aliases
    spcified in the derived pipe's ``default_aliases`` member are used
    unless an ``aliases`` argument is given to ``pipe()``.

    Any extra arguments to ``pipe()`` should be keyword arguments and
    can be handled by overriding the ``on_init_extras()`` method in the
    derived pipe. By default they are ignored.
    """
    default_aliases = {}
    def __init__(self, bag, name, aliases=None, **pextras):
        # Don't keep a reference to the bag, just the name this pipe from the ``.name`` attribute given
        self.name = name
        self.aliases = AttributeDict(self.default_aliases)
        if aliases:
            self.aliases.update(aliases)
        self.on_init_extras(**pextras)

    def on_init_extras(self):
        pass

    def enter(self, bag):
        log.debug('The enter() method hasn\'t been overidden in the %r derived class', self.__class__.__name__)

    def leave(self, bag, error=False):
        log.debug('The leave() method hasn\'t been overidden in the %r derived class', self.__class__.__name__)

class ConfigPipe(Pipe):
    """\
    Like a config pipe but with support for basic configuration options in the form of Fields.

    Used like this::

        from pipestack.pipe import ConfigPipe
        from conversionkit import Field
        from stringconvert import unicodeToUnicode, unicodeToBoolean

        class MyPipe(ConfigPipe):
            options = {
                'index_template': Field(
                    unicodeToUnicode(), 
                    missing_default="post.dwt",
                    empty_error="Please enter a value for '%(name)s.index_template' or remove it to use the default",
                ),
                'enable_archive': Field(
                    unicodeToBoolean(), 
                    empty_error="Please enter a value for '%(name)s.enable_archive'",
                    missing_default=False,
                ),
                'directory': Field(
                    existingDirectory(), 
                    empty_error="Please enter a value for '%(name)s.enable_archive'",
                )
            }
            post_converters = [
               guessDirectoryIfMissing(),
            ]

            def enter(self, bag):
                ...

            def leave(self, bag, error=False):
                ...

    In the example above the directory option doesn't have a simple default
    value if it isn't specified. Instead we need to guess which directory is used
    and to do so we might need to access other pipes. In this case we use a
    *post-converter* to choose a directory if there isn't one in the config file.
    The post converter will have access to the ``bag`` so will be able to access
    pipes, enabling it to choose an appropriate value.  The bag object it accesses
    will temporarily have a ``bag.pipe`` attribute that refers to the pipe so that you
    know which pipe it is being used with and can access its raw options as
    ``bag.app.option[bag.pipe.name]`` or its filtered options as ``conversion.value``.
    You can access its aliases as ``bag.pipe.aliases``.  For MarblePipes, the marble
    isn't set up until each request so you don't have access to it in the
    converters.

    For really complex cases you can override the ``on_parse_options()`` 
    method to define your own configuration implementation:

        from pipestack.pipe import ConfigPipe
        from conversionkit import Field
        from stringconvert import unicodeToUnicode, unicodeToBoolean
        from configconvert import handle_option_error
        from conversionkit import Conversion
        from recordconvert import toRecord
        from configconvert import handle_option_error, handle_section_error

        class MyPipe(ConfigPipe):

            def on_parse_options(self, bag, name):
                if self.required_section_error_message:
                    if not bag.app.option.has_key(name):
                        raise handle_section_error(
                            bag, 
                            name, 
                            self.required_section_error_message%dict(name=name)
                        )
                options = {
                    'item_template': Field(
                        unicodeToUnicode(), 
                        missing_default="tweet.dwt",
                        empty_error="Please enter a value for '%(name)s.item_template' or remove it to use the default",
                    ),
                    'enable_archive': Field(
                        unicodeToBoolean(), 
                        empty_error="Please enter a value for '%(name)s.enable_archive'",
                        missing_default=False,
                    ),
                }
                converter = toRecord(
                    converters=options
                )
                conversion = Conversion(bag.app.option.get(name, {})).perform(
                    converter,
                    AttributeDict(bag=bag, pipe=self)
                )
                if not conversion.successful:
                    handle_option_error(conversion, name)
                else:
                    bag.app.config[name] = conversion.result

            def enter(self, bag):
                ...

            def leave(self, bag, error=False):
                ...

    If an error should be raised if no config options are present you should
    specify ``required_section_error_message``. This option takes a string value
    which will have any ``%(name)s`` characters replaced with the name of the
    pipe to provide examples of the options which are required. For example::

        class MyRequiredConfigPipe(MyConfigPipe):

            required_section_error_message = '%(name)s.item_template and %(name)s.enable_archive'

    The error produced for the user if the pipe is called 'templating' would be::

        Expected the config file to contain options templating.item_template and templating.enable_archive.

    """
    required_section_error_message = None
    options = {}

    def __init__(self, bag, name, aliases=None, **pextras):
        Pipe.__init__(self, bag, name, aliases, **pextras)
        self.on_parse_options(bag)

    def on_parse_options(self, bag):
        if bag.app.option is None:
            raise getopt.GetoptError('No config file specified')
        if self.required_section_error_message:
            from configconvert import handle_option_error, handle_section_error
            if not bag.app.option.has_key(self.name):
                raise handle_section_error(
                    bag, 
                    self.name, 
                    self.required_section_error_message%dict(name=self.name)
                )
        from configconvert import handle_option_error
        from conversionkit import Conversion
        from recordconvert import toRecord
        options = self.options
        converter = toRecord(
            converters=options,
            #allow_extra_fields=False,
            #raise_on_extra_fields=False,
        )
        if hasattr(self, 'post_converters'):
            from conversionkit import chainPostConverters
            converter = chainPostConverters(converter, *self.post_converters)
        conversion = Conversion(bag.app.option.get(self.name, {})).perform(
            converter,
            AttributeDict(bag=bag, pipe=self),
        )
        if not conversion.successful:
            handle_option_error(conversion, self.name)
        else:
            self.config = bag.app.config[self.name] = conversion.result

class Marble(object):
    def __init__(self, bag, name, config, persistent_state, flow_state=None, aliases=None):
        self.__dict__['bag'] = bag
        self.__dict__['name'] = name
        self.__dict__['aliases'] = aliases
        self.on_initial_config(config)
        self.on_set_persistent_state(persistent_state)
        self.on_set_flow_state(flow_state)

    def on_initial_config(self, config):
        self.__dict__['config'] = config

    def on_set_persistent_state(self, persistent_state):
        self.__dict__['persistent_state'] = persistent_state

    def on_set_flow_state(self, flow_state):
        self.__dict__['flow_state'] = flow_state

class MarblePipe(ConfigPipe):
    """\
    This is an instance of a ``ConfigPipe`` but designed with the specific
    purpose of adding a marble to the bag. The class from which the marble should
    be created is specified as the ``marble_class`` instance variable.

    Often, ``MarblePipe`` classes and ``Marble`` classes need to co-operate 
    to work effectively together.
    """
    marble_class = Marble
    persistent_state = None
    def __init__(self, bag, name, aliases=None, **p):
        ConfigPipe.__init__(self, bag, name, aliases, **p)

    def enter(self, bag):
        if self.marble_class is not None:
            bag[self.name] = self.marble_class(
                bag, 
                self.name,
                bag.app.config[self.name],
                persistent_state = self.persistent_state,
                flow_state=None,
                aliases = self.aliases,
            )

    def leave(self, bag, error=False):
        if self.marble_class is not None and self.name in bag:
            del bag[self.name]

