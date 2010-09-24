# svectors.py
# Copyright 2010 Hagen Fürstenau <hagenf@coli.uni-saarland.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from math import log
from operator import itemgetter
from itertools import chain
from collections import defaultdict
from os.path import join as path_join

import _svectors


### Functions for writing and loading image files ###

def write_dotimage(vectors, filename):
    """Take dictionary of vectors and write dot image to file "filename"

    "vectors" is a dict with words as keys and vector dicts as values.
    Each vector dict has (integer) dimension IDs as keys and floats as values.
    """
    def vector_iter():
        for lemma, vector in vectors.items():
            yield (lemma, sorted(vector.items(), key=itemgetter(0)))
    with open(filename, "wb") as f:
        _svectors.make_image(vector_iter(), f)


def write_bjcimage(wordnet_path, frequencies, filename):
    """Write image for bounded Jiang/Conrath similarity

    "wordnet_path" must be a directory containing the index and data files
    for nouns and verbs.

    "frequencies" is a dict with (word, POS) as keys and integer counts
    as values. POS is either "N" (for nouns) or "V" (for verbs).
    """
    # The word vectors for Jiang/Conrath similarity have
    # <hypernym ID> + 2^32*<corresponding synset ID>
    # as keys and information content of the hypernym synset as values.
    # Each hypernym is included only once. If it corresponds to more
    # than one synset, the one with the lowest information content
    # value is stored.

    def ic_order(t):
        # Order by (descending) information content.
        # For equal IC values order by (descending) keys as a convention.
        return (-t[1], -t[0]&0xffffffff)

    def data_iter(suffix, target_pos):
        count_tuples = ((lemma, count)
                        for (lemma, pos), count in frequencies.items()
                        if pos == target_pos)
        wn = Wordnet(path_join(wordnet_path, "index."+suffix),
                     path_join(wordnet_path, "data."+suffix),
                     count_tuples)
        for word, synsets in wn.index.items():
            d = dict()
            for synset in synsets:
                for hyper in wn.hypernyms(synset):
                    if ((hyper not in d) or
                            (wn.ic[d[hyper][0]>>32] > wn.ic[synset])):
                        d[hyper] = (hyper+(synset<<32), wn.ic[hyper])
            vector = sorted(d.values(), key=ic_order)
            yield (word+target_pos, vector)

    noun_verb_iter = chain(data_iter("noun", "N"), data_iter("verb", "V"))
    with open(filename, "wb") as f:
        _svectors.make_image(noun_verb_iter, f)


def load_image(filename):
    """Load image (either dot or bjc) from file 'filename'

    Returns a Dataset object with methods 'dot' and 'bjc'.
    You are responsible for calling the one matching your data!
    """
    with open(filename, "rb") as f:
        return _svectors.Dataset(f)


### Light-weight WordNet interface ###

class Wordnet:
    def __init__(self, index, data, counts=None, encoding="ascii"):
        """Initialize from WordNet data files

        'index' and 'data' are the appropriate files for either
        the noun hierarchy or the verb hierarchy of WordNet.

        If an iterable of (lemma, frequency) tuples is given as 'counts',
        then information content values will be computed from it
        and the method 'jiang_conrath' will be available.
        """
        # load index
        self.index = dict()
        with open(index, "r", encoding=encoding) as f:
            for line in f:
                if line[:1] == " ":
                    continue
                lemma, pos, n, *rest = line.strip().split()
                lemma = lemma.replace("_", " ")
                offsets = [int(s) for s in rest if len(s)>3]
                self.index[lemma] = offsets

        # load hypernyms from data file
        self.hyper = dict()
        self.hypo = defaultdict(set)
        with open(data, "r", encoding=encoding) as f:
            for line in f:
                if line[:1] == " ":
                    continue
                fields = line.strip().split()
                if len(fields) < 2:
                    continue
                offset = int(fields[0])
                wn = int(fields[3], 16)
                pn = int(fields[4+2*wn])
                hyper = {int(fields[4+2*wn+4*i+2]) for i in range(pn)
                         if fields[4+2*wn+4*i+1] == "@"}
                self.hyper[offset] = hyper
                for h in hyper:
                    self.hypo[h].add(offset)

        # compute information contents if counts are available
        if counts is None:
            self.ic = None
        else:
            ic = {synset:1.0 for synset in self.hyper}  # add-1 smoothing
            total = len(self.hyper)
            for lemma, n in counts:
                total += n
                synsets = self.index.get(lemma, [])
                for synset in synsets:
                    for hyper in [synset]+list(self.hypernyms(synset)):
                        ic[hyper] += n/len(synsets)
            for synset, n in ic.items():
                ic[synset] = -log(n/total)
            self.ic = ic

    def synsets(self, lemma):
        """Return list of synset ids for lemma."""

        return self.index.get(lemma, [])

    def direct_hypernyms(self, synset):
        """Return set of direct hypernyms of 'synset'."""

        return self.hyper[synset]

    def direct_hyponyms(self, synset):
        """Return set of direct hyponyms of 'synset'."""

        return self.hypo[synset]

    def _transitive_reflexive_closure(self, synset, relation):
        res = {synset}
        new = {synset}
        while new:
            new = {relative for synset in new for relative in relation(synset)}
            new -= res
                # This mainly prevents directed cycles from tripping us up.
                # However a non-empty new&res does not necessarily indicate
                # a directed cycle. We could also be at the upper end
                # of an undirected cycle.
            res |= new
        return res

    def hypernyms(self, synset):
        """Return set of all direct and indirect hypernyms of 'synset'.

        (This includes 'synset' itself.)
        """
        return self._transitive_reflexive_closure(synset,
                                                  self.direct_hypernyms)

    def hyponyms(self, synset):
        """Return set of all direct and indirect hyponyms of 'synset'.

        (This includes 'synset' itself.)
        """
        return self._transitive_reflexive_closure(synset, self.direct_hyponyms)

    def jiang_conrath(self, synset1, synset2):
        """Return Jiang/Conrath similarity value of 'synset1' and 'synset2'.

        This is slow and only here for reference!
        """
        if self.ic is None:
            raise RuntimeError("no information content values available")
        common = self.hypernyms(synset1)&self.hypernyms(synset2)
        if not common:
            return 0.0
        lcs_ic = max(self.ic[synset] for synset in common)
        denom = self.ic[synset1] + self.ic[synset2] - 2*lcs_ic
        if denom != 0:
            return 1/denom


