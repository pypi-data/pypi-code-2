import sys
import os
import os.path as path
import imp
import fnmatch
import logging

VERSION = (0, 3, 0)

CO_VARARGS = 0x0004
CO_VARKEYWORDS = 0x0008

default_plugin_path = os.path.join(os.environ['HOME'], '.plugpy/plugins')

_instance = []
_cache = {}

DEBUG = False
#logger = None

def setup_log():
    global logger
    logger = logging.getLogger(__name__)
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                '%Y-%m-%d %H:%M:%S')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)
    global DEBUG
    DEBUG = True

def log(msg):
    if DEBUG:
        logger.debug(msg)

class Plugin(object):
    
    priority = 0    

    def __init__(self, *args, **kwargs):
        pass


def list_module(dir, pattern='*'):
    if path.isdir(dir):
        log("search plugin path:'%s'" % dir)
        dir = path.realpath(dir)
        return [path.join(dir, file) for file in os.listdir(dir) if not
                file.startswith('_') and file.endswith('.py') and
                fnmatch.fnmatchcase(file, pattern)]
    return []

def init_plugins(config, plugin_path=None, is_reload=False, pattern='*'):
    plugin_path = plugin_path or ['./plugins']
    plugins = []
    plugins.extend(list_module(default_plugin_path, pattern=pattern))
    
    plugin_pathes = plugin_path
    if not type(plugin_pathes) is list:
        plugin_pathes = [plugin_pathes]
    
    for plugin_path in plugin_pathes:
        if plugin_path:
            plugins.extend(list_module(plugin_path, pattern=pattern) or [])
    log("load module files %s" % plugins) 
    import_plugins(plugins, is_reload)

def import_plugins(plugins, is_reload=False):
    for plugin in plugins:
        if plugin:
            name = path.splitext(path.basename(plugin))[0]
            name = "plugpy.%s_plugin" % name
            if not is_reload:
                try:
                    return sys.modules[name]
                except KeyError:
                    pass
            fp = open(plugin)
            m = imp.load_module(name, fp, plugin, ('.py', 'U', 1))
            fp.close()
            log('import module %s' % m)
            
def find_plugin(clazz):
    sub = clazz.__subclasses__()
    log("find plugin class %s's plugin classes %s" % (clazz, sub))
    
    def _key(clazz):
        if hasattr(clazz, "priority"):
            return clazz.priority
        return clazz

    sub.sort(key=_key)
    log("'%s' target plugin classes %s" % (clazz, sub))
    return sub

def set_cache(clazz, ins):
    res = None
    try:
        res = _cache[clazz]
    except KeyError:
        _cache[clazz] = res = set()
    res.add(ins)

def is_cached(subclass):
    for ins in _instance:
        if isinstance(ins, subclass):
            return ins
    return None

def create_plugin(plugin_class, config, ignore):
    subclasses = find_plugin(plugin_class)
    for subclass in subclasses:
        if subclass in ignore:
            continue
        ins = is_cached(subclass)
        if ins:
            set_cache(plugin_class, ins)
            set_cache(subclass, ins)
            if hasattr(ins, "alias"):
                set_cache(ins.alias ,ins)
            continue
            
        ins = subclass(**config)
        set_cache(plugin_class, ins)
        set_cache(subclass, ins)
        if hasattr(ins, "alias"):
            set_cache(ins.alias ,ins)
        _instance.append(ins)


def load_plugins(config, plugin_path=None, plugin_class=None,
        pattern='*', ignore_class=None, debug=False, is_reload=False):
    if not config:
        config = dict()
    if debug:
        setup_log()
    
    plugin_path = plugin_path or ['./plugins']
    plugin_class = plugin_class or [Plugin]
    ignore_class = ignore_class or []

    log('plugin load config %s' % config)
    init_plugins(config, plugin_path=plugin_path, is_reload=is_reload,
            pattern=pattern)
    results = []
    pclasses = plugin_class
    if not type(pclasses) is list:
        pclasses = [pclasses]
    
    ignore = ignore_class
    if not type(ignore) is list:
        ignore = [ignore]
    
    for pclass in pclasses:
        create_plugin(pclass, config, ignore)

    log('loaded plugins %s' % _instance)
    return _instance

def dispatch(message, *args, **kwargs):
    res = []
    clazz = kwargs.pop('target', Plugin)
    prefix = kwargs.pop('prefix', 'on_')
    attr = prefix + message
    log("dispatch send message:'%s' call_method: '%s'" % (message, attr))
    targets = []
    if clazz in _cache:
        targets = _cache[clazz]
        log("dipatch targets %s" % targets)
        for ins in targets:
            if hasattr(ins, attr):
                func = getattr(ins, attr)
                log("find method %s '%s'" % (attr, ins))
                f_code = func.im_func.func_code
                if f_code.co_argcount > 1:
                    result = func(*args, **kwargs)
                else:
                    if f_code.co_flags & CO_VARARGS and f_code.co_flags & CO_VARKEYWORDS:
                        result = func(*args, **kwargs)
                    elif f_code.co_flags & CO_VARARGS:
                        result = func(*args)
                    elif f_code.co_flags & CO_VARKEYWORDS:
                        result = func(**kwargs)
                    else:
                        result = func()

                log("dispatch to %s call_method '%s' arg_info: %s %s : result %s" % 
                        (ins, attr, args, kwargs, result ))
                res.append((result, ins.__class__))
            else:
                log("missing plugin '%s' method '%s'" % (clazz, attr))
    else:
        log("missing plugin '%s'" % clazz)
        return
    
    log("dispatch finish message:'%s' call_method: '%s' : results %s" %
            (message, attr, res))
    return res

def reload_plugins(config, plugin_path=None, plugin_class=None,
        pattern='*', ignore_class=None, debug=False):
    log('reload plugin')

    plugin_path = plugin_path or ['./plugins']
    plugin_class = plugin_class or [Plugin]
    ignore_class = ignore_class or []
    
    del _instance[:]
    _cache.clear()
    return load_plugins(config, plugin_path=plugin_path,
            plugin_class=plugin_class, pattern=pattern, ignore_class=ignore_class,
            debug=debug, is_reload=True)

def get_plugins():
    return _instance

def get_plugin_list(key):
    plugins = _cache.get(key, None)
    if plugins:
        ret = []
        for plugin in plugins:
            ret.append(plugin.__class__.__name__)
        return str(ret)

def import_modules(plugin_path):
    import_path = plugin_path
    if not type(import_path) is list:
        import_path = [import_path]
    for p in import_path:
        import_module(p)

def import_module(plugin_path):
    d = len(plugin_path)
    if not plugin_path in sys.path:
        sys.path.insert(0, plugin_path)

    for root, dirs, files in os.walk(plugin_path):
        for file in files:
            if file.startswith('__'):
                continue
            name = path.join(root, file)[d:]
            if fnmatch.fnmatchcase(name, '*.py'):
                name = path.splitext(name)[0].replace('/', '.')
                m = __import__(name, {}, {}, [])
                print sys.modules[name]

__all__ = ['load_plugins', 'reload_plugins', 'get_plugins', 'get_plugin_list', 'dispatch', 'Plugin']

