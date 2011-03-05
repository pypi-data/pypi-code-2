'''
Created on Feb 23, 2011

@author: raul
'''

#Penn Treebank word level tags
#http://bulba.sdsu.edu/jeanette/thesis/PennTags.html
#
#CC - Coordinating conjunction
#CD - Cardinal number
#DT - Determiner
#EX - Existential there
#FW - Foreign word
#IN - Preposition or subordinating conjunction
#JJ - Adjective
#JJR - Adjective, comparative
#JJS - Adjective, superlative
#LS - List item marker
#MD - Modal
#NN - Noun, singular or mass
#NNS - Noun, plural
#NNP - Proper noun, singular
#NNPS - Proper noun, plural
#PDT - Predeterminer
#POS - Possessive ending
#PRP - Personal pronoun
#PRP$ - Possessive pronoun (prolog version PRP-S)
#RB - Adverb
#RBR - Adverb, comparative
#RBS - Adverb, superlative
#RP - Particle
#SYM - Symbol
#TO - to
#UH - Interjection
#VB - Verb, base form
#VBD - Verb, past tense
#VBG - Verb, gerund or present participle
#VBN - Verb, past participle
#VBP - Verb, non-3rd person singular present
#VBZ - Verb, 3rd person singular present
#WDT - Wh-determiner
#WP - Wh-pronoun
#WP$ - Possessive wh-pronoun (prolog version WP-S)
#WRB - Wh-adverb

import string

import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer

from chunker import get_chunker, get_chunks_IOB


KEYWORD_TAGS = set(['NN', 'NNS', 'NNP', 'NNPS'])
STOP_WORDS = set([])


def get_keywords(text):
    print text
    words = nltk.word_tokenize(text)
    tags = nltk.pos_tag(words)
    histo = {}
    for w, t in tags:
        if t in KEYWORD_TAGS and not (w in STOP_WORDS):
            if w in histo:
                histo[w] += 1
            else:
                histo[w] = 1
    l = sorted(histo, key=histo.get, reverse=True)
    for w in l:
        print w, histo[w]        
        
def transform(word):
    s = word.lower()
#    stemmer = PorterStemmer()
#    s = stemmer.stem(s)
    lemmatizer = WordNetLemmatizer()
    s = lemmatizer.lemmatize(s)
    return s
      
def get_keyphrases(text):
    ch = get_chunker()
    chunks = get_chunks_IOB(text,ch)
    in_np = False
    #histogram of individual words
    histo_w = {}
    #histogram of noun phrases
    histo_wp = {}
    #histogram of representative label for noun phrases
    histo_wpr = {}
    wpt = ''
    wpr = ''
    for w, t, p in chunks:    
        if p == 'B-NP':
            if in_np:
                if wpt in histo_wp:
                    histo_wp[wpt] += 1
                else:
                    histo_wp[wpt] = 1
                
                if wpt in histo_wpr:
                    histo_rep = histo_wpr[wpt]
                else:
                    histo_rep = {}
                if wpr in histo_rep:
                    histo_rep[wpr] += 1
                else:
                    histo_rep[wpr] = 1
                histo_wpr[wpt] = histo_rep
                     
            in_np = True
            if t in KEYWORD_TAGS:
                wpt = transform(w)
                wpr = w
            else:
                wpt = ''
                wpr = ''
        elif p == 'I-NP':
            if wpt != '':
                wpt += ' '
                wpr += ' '
            wpt += transform(w)
            wpr += w
        else:
            if in_np:
                if wpt in histo_wp:
                    histo_wp[wpt] += 1
                else:
                    histo_wp[wpt] = 1
                    
                if wpt in histo_wpr:
                    histo_rep = histo_wpr[wpt]
                else:
                    histo_rep = {}
                if wpr in histo_rep:
                    histo_rep[wpr] += 1
                else:
                    histo_rep[wpr] = 1
                histo_wpr[wpt] = histo_rep
            in_np = False
            wpt = ''
            wpr = ''            
        if t in KEYWORD_TAGS:
            wt = transform(w)
            if wt in histo_w:
                histo_w[wt] += 1
            else:
                histo_w[wt] = 1
    #remove bad cases          
    if '' in histo_wp:
        del histo_wp['']
    if '"' in histo_wp:
        del histo_wp['"']
    #remove terms that have invalid characters    
    VALID_LETTERS = string.lowercase + string.digits + ' '
    rem = []
    for w in histo_wp:
        for l in w:
            if not (l in VALID_LETTERS):
                rem.append(w)
                break
    for w in rem:
        del histo_wp[w]
    #add to compound phrases the weights of each component
    for wp in histo_wp:
        for w in histo_w:
            if w in wp:
                histo_wp[wp] += histo_w[w]
    l = sorted(histo_wp, key=histo_wp.get, reverse=True)
    res = []
    for w in l:
        histo = histo_wpr[w]
        l2 = sorted(histo, key=histo.get, reverse=True)
        wr = l2[0]
        print wr, histo_wp[w]
        res.append((wr,histo_wp[w]))
    return res
                
if __name__ == '__main__':
    text = '''
        Police shut Palestinian theatre in Jerusalem.
        
        Israeli police have shut down a Palestinian theatre in East Jerusalem.
        
        The action, on Thursday, prevented the closing event of an international
        literature festival from taking place.
        
        Police said they were acting on a court order, issued after intelligence
        indicated that the Palestinian Authority was involved in the event.
        
        Israel has occupied East Jerusalem since 1967 and has annexed the
        area.
        
        This is not recognised by the international community.
        
        The British consul-general in Jerusalem , Richard Makepeace, was
        attending the event.
        
        "I think all lovers of literature would regard this as a very
        regrettable moment and regrettable decision," he added.
        
        Mr Makepeace said the festival's closing event would be reorganised to
        take place at the British Council in Jerusalem.
        
        The Israeli authorities often take action against events in East
        Jerusalem they see as connected to the Palestinian Authority.
        
        Saturday's opening event at the same theatre was also shut down.
        
        A police notice said the closure was on the orders of Israel's internal
        security minister on the grounds of a breach of interim peace accords
        from the 1990s.
        
        These laid the framework for talks on establishing a Palestinian state
        alongside Israel, but left the status of Jerusalem to be determined by
        further negotiation.
        
        Israel has annexed East Jerusalem and declares it part of its eternal
        capital.
        
        Palestinians hope to establish their capital in the area.
        '''
    text = "Machine learning, a branch of Artificial Intelligence, is a scientific discipline concerned with the design and development of algorithms that allow computers to evolve behaviors based on empirical data, such as from sensor data or databases. A learner can take advantage of examples (data) to capture characteristics of interest of their unknown underlying probability distribution. Data can be seen as examples that illustrate relations between observed variables. A major focus of machine learning research is to automatically learn to recognize complex patterns and make intelligent decisions based on data; the difficulty lies in the fact that the set of all possible behaviors given all possible inputs is too large to be covered by the set of observed examples (training data). Hence the learner must generalize from the given examples, so as to be able to produce a useful output in new cases. Machine learning, like all subjects in artificial intelligence, requires cross-disciplinary proficiency in several areas, such as probability theory, statistics, pattern recognition, cognitive science, data mining, adaptive control, computational neuroscience and theoretical computer science."
    text = "Biology is a natural science concerned with the study of life and living organisms, including their structure, function, growth, origin, evolution, distribution, and taxonomy.[1] Biology is a vast subject containing many subdivisions, topics, and disciplines. Among the most important topics are five unifying principles that can be said to be the fundamental axioms of modern biology:[2]Cells are the basic unit of life. New species and inherited traits are the product of evolution. Genes are the basic unit of heredity. An organism regulates its internal environment to maintain a stable and constant condition. Living organisms consume and transform energy. Subdisciplines of biology are recognized on the basis of the scale at which organisms are studied and the methods used to study them: biochemistry examines the rudimentary chemistry of life; molecular biology studies the complex interactions of systems of biological molecules; cellular biology examines the basic building block of all life, the cell; physiology examines the physical and chemical functions of the tissues, organs, and organ systems of an organism; and ecology examines how various organisms interact and associate with their environment."
    get_keyphrases(text)
    