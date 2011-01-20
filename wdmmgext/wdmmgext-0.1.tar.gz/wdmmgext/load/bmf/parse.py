import codecs
import re
import logging

from lxml import html

log = logging.getLogger(__name__)

BASE_URL = "http://www.bundesfinanzministerium.de/bundeshaushalt%s/"


def file_to_doc(fname):
	fh = codecs.open(fname, 'r', 'utf-8')
	doc = html.document_fromstring(fh.read())
	fh.close()
	return doc

def clean(elem):
    return elem.xpath("string()")

def anchors(doc, rfilter):
    f = re.compile(rfilter)
    for a in doc.findall('.//a'):
        href = a.get('href')
        if href is None:
            continue
        match = f.match(href)
        if match:
            yield (href, clean(a))
