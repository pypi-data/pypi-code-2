"""\
Base classes for the different types of Pipe
"""

import getopt
import logging
import warnings
from bn import AttributeDict, MarbleLike

log = logging.getLogger(__name__)

class Pipe(object):
    """\
    Like a config pipe but with support for basic configuration options in the form of Fields.

    Used like this::

        from pipestack.pipe import Pipe
        from conversionkit import Field
        from stringconvert import unicodeToUnicode, unicodeToBoolean

        class MyPipe(Pipe):
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

    For really complex cases you can override the ``parse_options()`` 
    method to define your own configuration implementation:

        from pipestack.pipe import Pipe
        from conversionkit import Field
        from stringconvert import unicodeToUnicode, unicodeToBoolean
        from configconvert import handle_option_error
        from conversionkit import Conversion
        from recordconvert import toRecord
        from configconvert import handle_option_error, handle_section_error

        class MyPipe(Pipe):

            def parse_options(self, bag, name):
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

        class MyRequiredPipe(MyPipe):

            required_section_error_message = '%(name)s.item_template and %(name)s.enable_archive'

    The error produced for the user if the pipe is called 'templating' would be::

        Expected the config file to contain options templating.item_template and templating.enable_archive.

    """
    marble_class = None
    required_section_error_message = None
    options = {}
    post_converters = None

    default_aliases = {}
    version = (0,1,0)

    # The app would need to keep an install log.
    # Suggest app.install_log = /path/to/install/log
    # Then default_pipeline would be changed to flow_pipeline

    def __init__(self, bag, name, aliases=None, **pextras):
        # Don't keep a reference to the bag, just the name this pipe from the ``.name`` attribute given
        self.name = name
        self.aliases = AttributeDict()
        # Update the default aliases with the default aliases of the immediate parent (which should itself have been updated with the default aliases of its parents when it was initialised.
        if hasattr(super(self.__class__, self), 'default_aliases'):
            default_aliases = AttributeDict()
            default_aliases.update(super(self.__class__, self).default_aliases)
            default_aliases.update(self.default_aliases)
            self.default_aliases = default_aliases
        self.aliases.update(self.default_aliases)
        if aliases:
            self.aliases.update(aliases)
        if hasattr(self, 'persistent_state'):
            warnings.warn('The use of persistent_state as a class property is deprecated, please just overide create() in %s and set self.persistent_state there'%self.__class__.__name__)
        else:
            self.persistent_state = None
        self.config = bag.app.config[self.name] = self.parse_options(bag)
        self.create(bag)
        # Deprecated
        if hasattr(self, 'on_parse_options'):
            warnings.warn('The use of on_parse_options() is deprecated, please just overide __init__() in %s'%self.__class__.__name__)
            self.on_parse_options(bag)

    def create(self, bag):
        pass

    def parse_options(self, bag):
        
        # If the pipe doesn't have an options, don't parse them
        if not self.options and not self.post_converters and not self.required_section_error_message:
            self.config = bag.app.config[self.name] = AttributeDict()
            return self.config
        if not bag.app.option and not bag.app.config_file:
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
        from nestedrecord import decode
        options = self.options
        converter = toRecord(
            converters=options,
            filter_extra_fields=False,
            #allow_extra_fields=False,
            #raise_on_extra_fields=False,
        )
        if hasattr(self, 'post_converters') and \
           self.post_converters is not None:
            from conversionkit import chainPostConverters
            converter = chainPostConverters(converter, *self.post_converters)
        conversion = Conversion(decode(bag.app.option.get(self.name, {}))).perform(
            converter,
            AttributeDict(bag=bag, pipe=self),
        )
        if not conversion.successful:
            handle_option_error(conversion, self.name)
        #print conversion.result
        return conversion.result

    def enter(self, bag):
        if self.marble_class is not None:
            bag[self.name] = self.marble_class(
                bag, 
                self.name,
                bag.app.config[self.name],
                persistent_state = self.persistent_state,
                flow_state=None,
                aliases = self.aliases,
                default_aliases = self.default_aliases,
            )
        else:
            bag[self.name] = None
           
    def leave(self, bag, error=False):
        if self.name in bag:
            del bag[self.name]
        else:
            warnings.warn(
                'The %r pipe did not add a marble to the bag'%(self.name,)
            )

    @classmethod
    def upgrade(cls, bag):
        pass

    @classmethod
    def downgrade(self, bag):
        pass

    @classmethod
    def install(self, bag):
        pass

    def uninstall(self, bag):
        pass

class Marble(MarbleLike):
    def __init__(
        marble, 
        bag, 
        name, 
        config, 
        aliases=None, 
        default_aliases=None, 
        persistent_state=None, 
        flow_state=None
    ):
        MarbleLike.__init__(marble, bag, name, aliases)
        marble.__dict__['default_aliases'] = default_aliases
        marble.__dict__['config'] = config
        marble.__dict__['persistent_state'] = persistent_state
        marble.__dict__['flow_state'] = flow_state
        if marble.__dict__['default_aliases']:
            for name in marble.__dict__['default_aliases']:
                if name in marble.__dict__:
                    raise Exception(
                        'Invalid default alias %r (the class %s has an '
                        'instance variable of the same name)'%(
                            name,
                            marble.__class__.__name__,
                        )
                    )
        # Deprecated
        if hasattr(marble, 'on_set_persistent_state'):
            warnings.warn('The use of on_set_persistent_state() is deprecated, please just overide __init__() in %s'%marble.__class__.__name__)
            marble.on_set_persistent_state(persistent_state)
        if hasattr(marble, 'on_set_flow_state'):
            warnings.warn('The use of on_set_flow_state() is deprecated, please just overide __init__() in %s'%marble.__class__.__name__)
            marble.on_set_flow_state(flow_state)

class DispatchMarble(Marble):
          
    def dispatch(marble):
        pass

# Deprecated 
ConfigPipe = Pipe
class MarblePipe(Pipe):
    def on_parse_options(self, bag):
        warnings.warn('The use of on_parse_options() is deprecated, please just overide __init__() in %s'%self.__class__.__name__)
    
