from databasepipe.helper.connection import PerRequestConnection, \
   PerRequestConnectionCursor, log, service_extensions
from bn import AttributeDict
from databasepipe.helper import plugin
from pipestack.pipe import Pipe

def get_config(bag, name, plugins=[]):
    from configconvert import handle_option_error, handle_section_error
    if not bag.app.option.has_key(name):
        raise handle_section_error(
            bag, 
            name, 
            (
                "'%s.database' or '%s.plugin'"%(name, name)
            )
        )
    from stringconvert import unicodeToUnicode, unicodeToInteger,\
       unicodeToBoolean
    from recordconvert import toRecord
    from configconvert import stringToObject
    from conversionkit import Conversion, chainConverters

    # Re-use the converters   
    unicode_to_integer = unicodeToInteger()
    null = unicodeToUnicode()

    connection_service_converter = toRecord(
        missing_defaults=dict(
            pool=False,
            mincached=0,
            maxcached=0,
            maxshared=0,
            maxconnections=0,
            blocking=0,
            maxusage=0,
        ),
        missing_or_empty_errors = dict(
            plugin="The required option '%s.plugin' is missing"%(name,),
        ),
        converters=dict(
            pool = unicodeToBoolean(),
            plugin = null,#stringToObject(),
            mincached = unicode_to_integer,
            maxcached = unicode_to_integer,
            maxshared = unicode_to_integer,
            maxconnections = unicode_to_integer,
            blocking = unicode_to_integer,
            maxusage = unicode_to_integer,
        ),
        # Keep the pool options as they are, the plugin will need them
        filter_extra_fields = False

    )
    conversion = Conversion(bag.app.option[name]).perform(connection_service_converter)
    if not conversion.successful:
        handle_option_error(conversion, name)
    else:
        connection_service_config = conversion.result

    plugin_name = connection_service_config.plugin
    if not plugin.plugins_loaded:
        plugin.load_available_plugins(plugins)
    if not plugin.available_plugins.has_key(plugin_name):
        raise Exception('Plugin %r not found'%plugin_name)
    if not plugin.update_config.has_key(plugin_name):
        plugin.update_config[plugin_name] = \
           plugin.available_plugins[plugin_name]['update_config'].load()
    if not plugin.engine_name.has_key(plugin_name):
        plugin.engine_name[plugin_name] = \
           plugin.available_plugins[plugin_name]['engine_name'].load()
    if not plugin.driver_name.has_key(plugin_name):
        plugin.driver_name[plugin_name] = \
           plugin.available_plugins[plugin_name]['driver_name'].load()
    if not plugin.param_style.has_key(plugin_name):
        plugin.param_style[plugin_name] = \
           plugin.available_plugins[plugin_name]['param_style'].load()

    bag.app.config[name] = plugin.update_config[plugin_name](
        bag,
        name,
        connection_service_config,
    )
    bag.app.config[name]['plugin'] = plugin_name
    bag.app.config[name]['engine'] = plugin.engine_name[plugin_name]
    bag.app.config[name]['driver'] = plugin.driver_name[plugin_name]
    bag.app.config[name]['param_style'] = plugin.param_style[plugin_name]
    return bag.app.config[name]

class DatabasePipe(Pipe):
    def __init__(self, bag, name, aliases=None, **pextras):
        Pipe.__init__(self, bag, name, aliases, **pextras)
        self.param_style='format'
        self.config = get_config(bag, name, pextras.get('plugins', []))

        # These are options which affect the pipe, the others are for the plugin
        # Might be better to keep plugins separate rather than deleting config?
        self.fetch_converter = None
        if self.config.has_key('fetch_converter'):
            self.fetch_converter = self.config['fetch_converter']
            del self.config['fetch_converter']
        self.execute_converter = None
        if self.config.has_key('execute_converter'):
            self.execute_converter = self.config['execute_converter']
            del self.config['execute_converter']
        self.on_connect_sql = None
        if self.config.has_key('on_connect_sql'):
            self.on_connect_sql = self.config['on_connect_sql']
            del self.config['on_connect_sql']

        self.connection_args = {}
        for k, v in self.config.items():
            if k in [
                'database', 
                'user', 
                'host', 
                'password', 
                'port', 
                'fetch_converter',
                'execute_converter',
                'on_connect_sql',
                'unicode_results', 
                'dsn',
            ]:
                self.connection_args[str(k)] = v
        if self.config.get('pool', False) is True:
            from DBUtils.PooledDB import PooledDB
            for k, v in self.config.items():
                if k in [
                    'creator',
                    'mincached',
                    'maxcached',
                    'maxshared',
                    'maxconnections',
                    'blocking',
                    'maxusage',
                    'setsession',
                ]:
                    self.connection_args[str(k)] = v
            self.pool = PooledDB(**self.connection_args)
            self._connect = pool.connection
        else:
            self.creator = self.config.creator
            def _connect():
                return self.creator(**self.connection_args)
            self._connect = _connect

    def enter(self, bag):
        bag[self.name] = AttributeDict()
        def connect():
            if not bag[self.name].has_key('_connection'):
                bag[self.name]['_connection'] = PerRequestConnection(
                    self._connect(),
                    self.fetch_converter,
                    self.execute_converter,
                )
                # Run connection-level SQL here
                if self.on_connect_sql:
                    cursor = bag[self.name]['_connection']._connection.cursor()
                    cursor.execute(str(self.on_connect_sql))
                    cursor.close()
            return bag[self.name]['_connection']
        bag[self.name]['connect'] = connect
        bag[self.name]['param_style'] = self.param_style
        service_extensions(bag, self.name)

    def leave(self, bag, error=False):
        if not error:
            if bag[self.name].has_key('_connection'):
                if bag[self.name]._connection._should_commit:
                    log.debug('Automatically commiting changes to the database')
                    bag[self.name]._connection._connection.commit()
                bag[self.name]._connection._connection.close()
        else:
            if bag[self.name].has_key('_connection'):
                log.warning('An error occurred, rolling back database changes')
                bag[self.name]._connection._should_commit = False
                bag[self.name]._connection._connection.rollback()

