from xml.etree import ElementTree
from os import listdir
from os.path import join
from urllib2 import urlopen

from lxml.etree import fromstring, parse, XMLSyntaxError

cache = 'tests/cache'

def multiple():
    for fn in listdir(cache):
        if not fn.startswith('.'):
            with open(join(cache, fn)) as f:
                try:
                    fromstring(f.read())
                    print 'SUCCESS: %s' % fn
                except XMLSyntaxError, e:
                    print 'ERROR:   %s' % fn
                    print e
                    exit()

def single(fn):
    #print fn
    #print join(cache, fn)
    url = 'http://www.thetvdb.com/api/C4C424B4E9137AFD/series/80348/default/1/8/en.xml'
    data = urlopen(url).read()
    print ElementTree.fromstring(data)
    print fromstring(data)
    with open(join(cache, fn), 'w') as f:
        f.write(data)

    with open(join(cache, fn), 'r') as f:
        print fromstring(f.read())
        #try:
            #fromstring(f.read())
            #print 'SUCCESS: %s' % fn
        #except XMLSyntaxError, e:
            #print 'ERROR:   %s' % fn
            #print e
        #exit()

#multiple()
single('test.xml')

