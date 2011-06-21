from os.path import realpath


class RealpathRecipe(object):
    """
    Recipe that ingests options and normalizes the option values
    from relative paths to absolute paths if the option name begins
    with 'path.'
    """
    
    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        for key, value in self.options.items():
            if key.startswith('path.'):
                self.options[key] = realpath(value)
            else:
                self.options[key] = value
    
    def install(self):
        return tuple()
    
    update = install

