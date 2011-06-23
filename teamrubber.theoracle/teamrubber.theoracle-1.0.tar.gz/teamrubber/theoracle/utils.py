def _import(name,fromlist=[]):
    try:
        result = __import__(name,globals(),locals(),fromlist)
    except ImportError:
        result = None
    return result    

def safe_import(dotted_path):
    object_name = dotted_path
    if object_name is None:
        return None

    ob_import_explicit = _import(object_name,object_name.split('.')[-1:])
    ob_import = _import(object_name)
    ob = ob_import_explicit or ob_import
    if ob is None:
        return ''
    return ob
