'''
Created on Feb 22, 2011

@author: raul
'''

import itertools
import pickle
import os

import nltk.chunk
import nltk.corpus, nltk.tag
 
class TagChunker(nltk.chunk.ChunkParserI):
    def __init__(self, chunk_tagger):
        self._chunk_tagger = chunk_tagger
 
    def parse(self, tokens):
        # split words and part of speech tags
        (words, tags) = zip(*tokens)
        # get IOB chunk tags
        chunks = self._chunk_tagger.tag(tags)
        # join words with chunk tags
        wtc = itertools.izip(words, chunks)
        # w = word, t = part-of-speech tag, c = chunk tag
        lines = [' '.join([w, t, c]) for (w, (t, c)) in wtc if c]
        # create tree from conll formatted chunk lines
        return nltk.chunk.conllstr2tree('\n'.join(lines))
 
def conll_tag_chunks(chunk_sents):
    tag_sents = [nltk.chunk.tree2conlltags(tree) for tree in chunk_sents]
    return [[(t, c) for (w, t, c) in chunk_tags] for chunk_tags in tag_sents]
 
def ubt_conll_chunk_accuracy(train_sents, test_sents):
    train_chunks = conll_tag_chunks(train_sents)
    test_chunks = conll_tag_chunks(test_sents)
 
    u_chunker = nltk.tag.UnigramTagger(train_chunks)
    print 'u:', nltk.tag.accuracy(u_chunker, test_chunks)
 
    ub_chunker = nltk.tag.BigramTagger(train_chunks, backoff=u_chunker)
    print 'ub:', nltk.tag.accuracy(ub_chunker, test_chunks)
 
    ubt_chunker = nltk.tag.TrigramTagger(train_chunks, backoff=ub_chunker)
    print 'ubt:', nltk.tag.accuracy(ubt_chunker, test_chunks)
 
    ut_chunker = nltk.tag.TrigramTagger(train_chunks, backoff=u_chunker)
    print 'ut:', nltk.tag.accuracy(ut_chunker, test_chunks)
 
    utb_chunker = nltk.tag.BigramTagger(train_chunks, backoff=ut_chunker)
    print 'utb:', nltk.tag.accuracy(utb_chunker, test_chunks)
 
def train_chunker(train_sents):
    train_chunks = conll_tag_chunks(train_sents)
    u_chunker = nltk.tag.UnigramTagger(train_chunks)
    ub_chunker = nltk.tag.BigramTagger(train_chunks, backoff=u_chunker)
    return ub_chunker

def test1():
    # conll chunking accuracy test
    conll_train = nltk.corpus.conll2000.chunked_sents('train.txt')
    conll_test = nltk.corpus.conll2000.chunked_sents('test.txt')
    ubt_conll_chunk_accuracy(conll_train, conll_test)
     
    # treebank chunking accuracy test
    treebank_sents = nltk.corpus.treebank_chunk.chunked_sents()
    ubt_conll_chunk_accuracy(treebank_sents[:2000], treebank_sents[2000:])    
    
def get_chunks(sentence,chunker):
    words = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(words)
    tree = chunker.parse(tagged)
    #tree.draw()
    print nltk.chunk.util.tree2conlltags(tree)
    result = []
    # for each noun phrase sub tree in the parse tree
    for subtree in tree.subtrees(filter=lambda t: t.node == 'NP'):
        # print the noun phrase as a list of part-of-speech tagged words
        result.append(subtree.leaves())
    return result

def get_chunks_IOB(text,chunker):
    sents = nltk.sent_tokenize(text)
    words = [x for sent in sents for x in nltk.word_tokenize(sent)]
    tagged = nltk.pos_tag(words)
    tree = chunker.parse(tagged)
    return nltk.chunk.util.tree2conlltags(tree)
    
#    words = nltk.word_tokenize(text)
#    tagged = nltk.pos_tag(words)
#    tree = chunker.parse(tagged)
#    return nltk.chunk.util.tree2conlltags(tree)

def create_chunker(file_name):
    treebank_sents = nltk.corpus.treebank_chunk.chunked_sents()
    chunk_tagger = train_chunker(treebank_sents)
    chunker = TagChunker(chunk_tagger)
    f = open(file_name,'w')
    pickle.dump(chunker,f)
    f.close()
    return chunker
    
def load_chunker(file_name):
    f = open(file_name,'r')
    chunker = pickle.load(f)
    return chunker

def get_chunker():
    data_path = os.path.join(os.path.dirname(__file__),'data')
    chunker = load_chunker(os.path.join(data_path,'chunker_en.pickle'))
    return chunker
 
def test2():
    data_path = os.path.join(os.path.dirname(__file__),'data')
    #chunker = create_chunker(os.path.join(data_path,'chunker_en.pickle'))
    chunker = load_chunker(os.path.join(data_path,'chunker_en.pickle'))
    
    
    s = "United States is a beautiful country located in North America."
    l = get_chunks(s,chunker)
    for chunk in l:
        print chunk
        
    s = "Tryolabs is the best place to work!"
    l = get_chunks(s,chunker)
    for chunk in l:
        print chunk
        
    s = "The German consul of Boston, John Smith, resides in Indiana."
    l = get_chunks(s,chunker)
    for chunk in l:
        print chunk    
    

if __name__ == '__main__':
    test2()