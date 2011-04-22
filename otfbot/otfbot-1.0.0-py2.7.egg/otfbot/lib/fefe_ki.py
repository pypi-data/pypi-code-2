import urllib2
from lxml import html
import pyniall_sqlite
import os.path


d=html.document_fromstring(unicode(urllib2.urlopen("http://blog.fefe.de/?mon=201003").read(), "UTF-8"))
entries=d.xpath("//li")

db_exists=os.path.exists("bla.db")
n=pyniall_sqlite.pyNiall("bla.db")

if not db_exists:
    for entry in entries:
        text=entry.text_content()[4:].encode("utf-8")
        #print text
        n.learn(text)
    n.cleanup()
else:
    print "[l] "+n.reply("")
