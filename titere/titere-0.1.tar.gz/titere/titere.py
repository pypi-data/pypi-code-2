import yaml
from tags import User


class Titere(object):

    def __init__(self, filename):

        # Read filename
        print filename
        fd = open(filename)
        document = fd.read()
        fd.close()

        # Parse document.
        self.start = yaml.load(document)

    def apply(self):

        # Apply
        self.start.apply()
