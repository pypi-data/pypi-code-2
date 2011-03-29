'''
Created on 31 oct. 2009

@author: coissac
'''
from random import shuffle, randrange

def lookfor(x,cumsum):
    lmax=len(cumsum)
    lmin=0
    while((lmax - lmin) > 1):

        i=(lmax+lmin)/2
        #print i,lmin,lmax
        if (x<cumsum[i] and (i==0 or x>cumsum[i-1])):
            #print "return 1 :",i,cumsum[i-1],"<",x,"<",cumsum[i]
            return i
        elif cumsum[i]==x:
            #print "return 2 :",i,cumsum[i],"<",x,"<",cumsum[i+1]
            return i+1
        elif x<cumsum[i]:
            lmax=i
        else:
            lmin=i
    #print "end return :",i,cumsum[i-1],"<",x,"<",cumsum[i]
    return i

def weigthedSample(events,size):
    entries = [k for k in events.iterkeys() if events[k]>0]
    shuffle(entries)
    cumul=[]
    s=0
    for e in entries:
        s+=events[e]
        cumul.append(s)
    
    #print cumul
    result={}
    
    for t in xrange(size):
        e=lookfor(randrange(s), cumul)
        k=entries[e]
        result[k]=result.get(k,0)+1

    return result