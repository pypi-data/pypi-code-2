# Copyright (C) 2009 by Eric Talevich (eric.talevich@gmail.com)
# Based on Bio.Nexus, copyright 2005-2008 by Frank Kauff & Cymon J. Cox.
# All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license. Please see the LICENSE file that should have been included
# as part of this package.

"""I/O function wrappers for the Newick file format.

See: U{ http://evolution.genetics.washington.edu/phylip/newick_doc.html }
"""
__docformat__ = "epytext en"

from cStringIO import StringIO

from Bio.Phylo import Newick

# Definitions retrieved from Bio.Nexus.Trees
NODECOMMENT_START = '[&'
NODECOMMENT_END = ']'


class NewickError(Exception):
    """Exception raised when Newick object construction cannot continue."""
    pass


# ---------------------------------------------------------
# Public API

def parse(handle):
    """Iterate over the trees in a Newick file handle.

    @return: a generator of Bio.Phylo.Newick.Tree objects.
    """
    return Parser(handle).parse()

def write(trees, handle, plain=False, **kwargs):
    """Write a trees in Newick format to the given file handle.

    @return: number of trees written.
    """
    return Writer(trees).write(handle, plain=plain, **kwargs)


# ---------------------------------------------------------
# Input

class Parser(object):
    """Parse a Newick tree given a file handle.

    Based on the parser in Bio.Nexus.Trees.
    """

    def __init__(self, handle):
        self.handle = handle

    @classmethod
    def from_string(cls, treetext):
        handle = StringIO(treetext)
        return cls(handle)

    def parse(self, values_are_support=False, rooted=False):
        """Parse the text stream this object was initialized with."""
        self.values_are_support = values_are_support
        self.rooted = rooted
        buf = ''
        for line in self.handle:
            buf += line.rstrip()
            if buf.endswith(';'):
                yield self._parse_tree(buf)
                buf = ''
        if buf:
            # Last tree is missing a terminal ';' character -- that's OK
            yield self._parse_tree(buf)

    def _parse_tree(self, text):
        """Parses the text representation into an Tree object."""
        # XXX what global info do we have here? Any? Use **kwargs?
        return Newick.Tree(root=self._parse_subtree(text))

    def _parse_subtree(self, text):
        """Parse (a,b,c...)[[[xx]:]yy] into subcomponents, recursively."""
        text = text.strip().rstrip(';')
        if text.count('(')!=text.count(')'):
            raise NewickError("Parentheses do not match in (sub)tree: " + text)
        # Text is now "(...)..." (balanced parens) or "..." (leaf node)
        if text.count('(') == 0:
            # Leaf/terminal node -- recursion stops here
            return self._parse_tag(text)
        # Handle one layer of the nested subtree
        # XXX what if there's a paren in a comment or other string?
        close_posn = text.rfind(')')
        subtrees = []
        # Locate subtrees by counting nesting levels of parens
        plevel = 0
        prev = 1
        for posn in range(1, close_posn):
            if text[posn] == '(':
                plevel += 1
            elif text[posn] == ')':
                plevel -= 1
            elif text[posn] == ',' and plevel == 0:
                subtrees.append(text[prev:posn])
                prev = posn + 1
        subtrees.append(text[prev:close_posn])
        # Construct a new clade from trailing text, then attach subclades
        clade = self._parse_tag(text[close_posn+1:])
        clade.clades = [self._parse_subtree(st) for st in subtrees]
        return clade

    def _parse_tag(self, text):
        """Extract the data for a node from text.

        @return: Clade instance containing any available data
        """
        # Extract the comment
        comment_start = text.find(NODECOMMENT_START)
        if comment_start != -1:
            comment_end = text.find(NODECOMMENT_END)
            if comment_end == -1:
                raise NewickError('Error in tree description: '
                                  'Found %s without matching %s'
                                  % (NODECOMMENT_START, NODECOMMENT_END))
            comment = text[comment_start+len(NODECOMMENT_START):comment_end]
            text = text[:comment_start] + text[comment_end+len(NODECOMMENT_END):]
        else:
            comment = None
        clade = Newick.Clade(comment=comment)
        # Extract name (taxon), and optionally support, branch length
        # Float values are support and branch length, the string is name/taxon
        values = []
        for part in (t.strip() for t in text.split(':')):
            if part:
                try:
                    values.append(float(part))
                except ValueError:
                    assert clade.name is None, "Two string taxonomies?"
                    clade.name = part
        if len(values) == 1:
            # Real branch length, or support as branch length
            if self.values_are_support:
                clade.confidence = values[0]
            else:
                clade.branch_length = values[0]
        elif len(values) == 2:
            # Two non-taxon values: support comes first. (Is that always so?)
            clade.confidence, clade.branch_length = values
        elif len(values) > 2:
            raise NewickError("Too many colons in tag: " + text)
        return clade


# ---------------------------------------------------------
# Output

class Writer(object):
    """Based on the writer in Bio.Nexus.Trees (str, to_string)."""

    def __init__(self, trees):
        self.trees = trees

    def write(self, handle, **kwargs):
        """Write this instance's trees to a file handle."""
        count = 0
        for treestr in self.to_strings(**kwargs):
            handle.write(treestr + '\n')
            count += 1
        return count

    def to_strings(self, support_as_branchlengths=False,
            branchlengths_only=False, plain=False,
            plain_newick=True, ladderize=None,
            max_support=1.0):
        """Return an iterable of PAUP-compatible tree lines."""
        # If there's a conflict in the arguments, we override plain=True
        if support_as_branchlengths or branchlengths_only:
            plain = False
        make_info_string = self._info_factory(plain, support_as_branchlengths,
                                              branchlengths_only, max_support)
        def newickize(clade):
            """Convert a node tree to a Newick tree string, recursively."""
            if clade.is_terminal():    #terminal
                return ((clade.name or '')
                        + make_info_string(clade, terminal=True))
            else:
                subtrees = (newickize(sub) for sub in clade)
                return '(%s)%s' % (','.join(subtrees),
                                   make_info_string(clade))

        # Convert each tree to a string
        for tree in self.trees:
            if ladderize in ('left', 'LEFT', 'right', 'RIGHT'):
                # Nexus compatibility shim, kind of
                tree.ladderize(reverse=(ladderize in ('right', 'RIGHT')))
            rawtree = newickize(tree.root) + ';'
            if plain_newick:
                yield rawtree
                continue
            # Nexus-style (?) notation before the raw Newick tree
            treeline = ['tree', (tree.name or 'a_tree'), '=']
            if tree.weight != 1:
                treeline.append('[&W%s]' % round(float(tree.weight), 3))
            if tree.rooted:
                treeline.append('[&R]')
            treeline.append(rawtree)
            yield ' '.join(treeline)

    def _info_factory(self, plain, support_as_branchlengths,
            branchlengths_only, max_support):
        """Return a function that creates a nicely formatted node tag."""
        if plain:
            # Plain tree only. That's easy.
            def make_info_string(clade, terminal=False):
                return ''

        elif support_as_branchlengths:
            # Support as branchlengths (eg. PAUP), ignore actual branchlengths
            def make_info_string(clade, terminal=False):
                if terminal:
                    # terminal branches have 100% support
                    return ':%1.2f' % max_support
                else:
                    return ':%1.2f' % (clade.confidence)

        elif branchlengths_only:
            # write only branchlengths, ignore support
            def make_info_string(clade, terminal=False):
                return ':%1.5f' % (clade.branch_length)

        else:
            # write support and branchlengths (e.g. .con tree of mrbayes)
            def make_info_string(clade, terminal=False):
                if terminal:
                    return ':%1.5f' % (clade.branch_length or 1.0)
                else:
                    if (clade.branch_length is not None and
                        hasattr(clade, 'confidence') and
                        clade.confidence is not None):
                        # we have blen and suppport
                        return '%1.2f:%1.5f' % (clade.confidence,
                                                clade.branch_length)
                    elif clade.branch_length is not None:
                        # we have only blen
                        return '0.00000:%1.5f' % clade.branch_length
                    elif (hasattr(clade, 'confidence') and
                          clade.confidence is not None):
                        # we have only support
                        return '%1.2f:0.00000' % clade.confidence
                    else:
                        return '0.00:0.00000'

        return make_info_string

