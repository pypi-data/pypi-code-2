from bn import AttributeDict
from pkg_resources import iter_entry_points

available_plugins = {}
insert_record = {}
update_config = {}
engine_name = {}
driver_name = {}
param_style = {}
plugins_loaded = False

def load_available_plugins(plugins=[]):
    dist_plugins = {}
    if not plugins:
        for ep in iter_entry_points(
            group='database.engine',
            # Use None to get all entry point names
            name=None,
        ):
            if not dist_plugins.has_key(ep.dist):
                dist_plugins[ep.dist] = {}
            dist_plugins[ep.dist][ep.name] = ep
        for k, v in dist_plugins.items():
            available_plugins[v['plugin_name'].load()] = {
                'insert_record': v['insert_record'],
                'engine_name': v['engine_name'],
                'driver_name': v['driver_name'],
                'update_config': v['update_config'],
                'param_style': v['param_style'],
            }
    else:
        for plugin in plugins:
            available_plugins[plugin['plugin_name']] = plugin
            if plugin.has_key('insert_record'):
                insert_record[plugin['plugin_name']] = plugin['insert_record']
            if plugin.has_key('update_config'):
                update_config[plugin['plugin_name']] = plugin['update_config']
            if plugin.has_key('engine_name'):
                engine_name[plugin['plugin_name']] = plugin['engine_name']
            if plugin.has_key('driver_name'):
                driver_name[plugin['plugin_name']] = plugin['driver_name']
            if plugin.has_key('param_style'):
                param_style[plugin['plugin_name']] = plugin['param_style']
    plugins_loaded = True
 
