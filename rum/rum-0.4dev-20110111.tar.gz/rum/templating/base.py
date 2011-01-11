from pkg_resources import resource_filename

class BaseRenderer(object):
    def __init__(self, search_path=None, auto_reload=True, cache_dir=None):
        if search_path is None:
            search_path = []
        search_path.append(resource_filename('rum', 'templates'))
        self.search_path = search_path
        self.cache_dir = cache_dir
        self.auto_reload = auto_reload
        self.loader = None

    def render(self, data, possible_templates=[]):
        raise NotImplementedError("I'm an abstract method")
