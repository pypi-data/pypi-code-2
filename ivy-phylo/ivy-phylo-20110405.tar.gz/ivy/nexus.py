from Bio.Nexus import Nexus
import newick

class Newick(object):
    """
    convenience class for storing the results of a newick tree
    record from a nexus file, as parsed by newick.nexus_iter
    """
    def __init__(self, parse_results=None, ttable={}):
        self.name = ""
        self.comment = ""
        self.root_comment = ""
        self.newick = ""
        self.ttable = ttable
        if parse_results: self.populate(parse_results)

    def populate(self, parse_results, ttable={}):
        self.name = parse_results.tree_name
        self.comment = parse_results.tree_comment
        self.root_comment = parse_results.root_comment
        self.newick = parse_results.newick
        if ttable: self.ttable = ttable

    def parse(self, newick=newick):
        assert self.newick
        self.root = newick.parse(
            self.newick, ttable=self.ttable, treename=self.name
            )
        return self.root

def fetchaln(fname):
    n = Nexus.Nexus(fname)
    return n

