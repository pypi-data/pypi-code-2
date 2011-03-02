'''
Created on Feb 23, 2011

@author: raul
'''

import nltk

if __name__ == '__main__':
    #text = "United States is a beautiful country located in North America."
    text = "Machine learning, a branch of Artificial Intelligence, is a scientific discipline concerned with the design and development of algorithms that allow computers to evolve behaviors based on empirical data, such as from sensor data or databases. A learner can take advantage of examples (data) to capture characteristics of interest of their unknown underlying probability distribution. Data can be seen as examples that illustrate relations between observed variables. A major focus of machine learning research is to automatically learn to recognize complex patterns and make intelligent decisions based on data; the difficulty lies in the fact that the set of all possible behaviors given all possible inputs is too large to be covered by the set of observed examples (training data). Hence the learner must generalize from the given examples, so as to be able to produce a useful output in new cases. Machine learning, like all subjects in artificial intelligence, requires cross-disciplinary proficiency in several areas, such as probability theory, statistics, pattern recognition, cognitive science, data mining, adaptive control, computational neuroscience and theoretical computer science."
    
    sents = nltk.sent_tokenize(text)
    words = [x for sent in sents for x in nltk.word_tokenize(sent)]
    tags = nltk.pos_tag(words)
    tree = nltk.ne_chunk(tags,binary=True)
    result = []
    
    #tree.draw()
    print nltk.chunk.util.tree2conlltags(tree)
    
    # for each noun phrase sub tree in the parse tree
    for subtree in tree.subtrees(filter=lambda t: t.node == 'NE'):
        # print the noun phrase as a list of part-of-speech tagged words
        result.append(subtree.leaves())
    print result