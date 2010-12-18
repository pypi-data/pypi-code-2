# coding: 

import sys
import urllib
import HTMLParser

class DescriptionFetcher(HTMLParser.HTMLParser):
    def __init__(self, parent):
        HTMLParser.HTMLParser.__init__(self)
        self.parent = parent
        self.text = ''
        self.rec = False
    def handle_starttag(self, tag, attrs):
        if tag == 'pre':
            self.rec = True
    def handle_endtag(self, tag):
        if tag == 'pre':
            self.parent.data.append(self.text.strip())
            self.rec = False
            self.text = ''
    def handle_data(self, data):
        if self.rec:
            self.text += data
            
        
class ProblemDescription(object):
    def __init__(self, pid):
        self.data = []
        self.descfetcher = DescriptionFetcher(self)
        url = 'http://rose.u-aizu.ac.jp/onlinejudge/ProblemSet/description.jsp?id='
        cont = urllib.urlopen(url + str(pid).zfill(4)).read()
        self.descfetcher.feed(cont)
        
        self.samplein = self.data[-2]
        self.sampleout = self.data[-1]

pid = sys.argv[1]
pd = ProblemDescription(pid)

fs = open('in', 'w')
print pd.samplein
fs.write(pd.samplein)
fs.close()
print ''
fs = open('sout', 'w')
print pd.sampleout
fs.write(pd.sampleout)
fs.close()
