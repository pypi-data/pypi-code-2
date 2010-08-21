#!/bin/python

# for python 2.6
# dependencies - wxpython, beautiful soup, pypdf

import sys, os, os.path, getopt, re, time
import urllib
import urllib2
import string
import traceback
from BeautifulSoup import *
import urlparse
import wx
import re
import locale

from pyPdf import PdfFileWriter, PdfFileReader
from pieberry_config import *
from pieberry_events import *
from utility.decoding import *

prefenc = locale.getpreferredencoding()

user_agent = 'Mozilla/Linux'
headers = { 'User-Agent' : user_agent }
re_submission = re.compile(r'^(.+?)(\'s)?( -)? [sS]ubmission')
head_re = re.compile('[hH][1-7]')
sub_re = re.compile('[Ss]ubmission')

def fetch_page(notify_window, url):
    '''fetch a page. that is all'''
    try:    
        thepage = urllib2.urlopen(url)
    except ValueError:
        traceback.print_exc()
        wx.PostEvent(notify_window, pieUpdateEvent('warn', "Not a valid or recognised url"))
        raise ValueError
    except urllib2.HTTPError: 
        traceback.print_exc()
        wx.PostEvent(notify_window, pieUpdateEvent('warn', "Could not access website"))
        raise Exception
    thehtml = thepage.read()
    return thehtml

pdf_rex = ("^.*\.(PDF|pdf)", r'.*DownloadPublication.aspx.*')

def pdf_test():
     '''generator function to serve up various regexs to find pdfs on
     a page (different CMSs make this necessary)'''
     for rex in pdf_rex:
          yield rex

def text_t(node):
     '''return last substantial (> 5 chars) bit of text before the
     current BS node'''
     rettext = ''
     counter = 0
     while not len(rettext) > 5 and counter < 10000:
          node = node.findPrevious(text=True)
          rettext = unicode(node)
          counter += 1
     return rettext

doc_contexts = {
    'submissions': ['submission'],
    'appendices': ['appendix', 'attachment', 'annexure'],
    'media': ['media release', 'media statement', 'bulletin'],
    'etc': ['agenda'],
    'notices': ['notice']
    }

def snarf_pdfs(notify_window, html, url):
    '''get all pdfs on a given page. return list of dicts:
    { pdflink, pdflink_text, pdflink_context } 
    pdflink_context can be one of "submissions" ... '''
    try:
        readup = BeautifulSoup(html)
    except Exception, err:
        traceback.print_exc()
        wx.PostEvent(notify_window, pieUpdateEvent('warn', "Invalid or unparseable HTML"))
        raise Exception
    pdflinks = []
    for pdfre in pdf_test():
         pdflinks.extend(readup.findAll('a', href=re.compile(pdfre)))
    if not pdflinks:
        wx.PostEvent(notify_window, pieUpdateEvent('warn', 'No pdf links found'))
        raise Exception
    wx.PostEvent(notify_window, pieUpdateEvent('blank', 'Starting (Found %d files)' % len(pdflinks)))
    retlist = []
    all_are_submissions = ('ubmissions' in readup.title.string)
    if readup.base: # if base url explicitly specified (e.g. dme.qld.gov.au)
        baseurl = readup.base['href']
    else:
        baseurl = url
    for link in pdflinks:
        ret = {
            'pdflink': '',
            'pdflink_text': '',
            'pdflink_context': ''}
        doctext = link.findChildren(text=True)
        nameofdoc = string.join(doctext, " ").decode('utf-8')
        if len(nameofdoc) < 5: #that can't be right ... let's have a guess
             print 'warning - bad filename context'
             nameofdoc = string.join((
                  text_t(link), 
                  '-', 
                  link['href'].split('/')[-1])
                  # urlparse.urlparse(
                  #      urllib.unquote(
                  #           link['href'])).path.split('/')[-1]
                  )
        nameofdoc = decode_htmlentities(nameofdoc)

        # Get rid of filename extension
        if nameofdoc[-4:] in ('.pdf', '.PDF', '.Pdf'):
            nameofdoc = nameofdoc[:-4]
        ret['pdflink_text'] = nameofdoc
        head_h = link.findPrevious(head_re) # the last heading
        for contx, keyterms in doc_contexts.items():
            for kt in keyterms:
                if kt in ret['pdflink_text'].lower():
                    ret['pdflink_context'] = contx
                if head_h and kt in unicode(head_h.text).lower():
                    ret['pdflink_context'] = contx
        # # Determine whether this is a submission and flag accordingly
        # if sub_re.search(nameofdoc):
        #     ret['pdflink_context'] = 'submissions'
        # # If 'submission' in the last headings do same

        # if head_h:
        #     if sub_re.search(head_h.text):
        #         ret['pdflink_context'] = 'submissions'
        # if all_are_submissions:
        #      ret['pdflink_context'] = 'submissions'
        # Finally assign relevant link
        # try to work out if the link is already quoted text or not
        if "%" in  link['href'].encode('utf-8'):
            pathstub = link['href'].encode('utf-8')
        else:
            pathstub = urllib.quote(link['href'].encode('utf-8'))
        ret['pdflink'] = urlparse.urljoin(baseurl, pathstub)
        retlist.append(ret)
    return retlist

import cookielib
cj = cookielib.CookieJar()

def download_pdf(notify_window, pdfinfo, author, tag):
    '''download a pdf and return its location.'''
    try:
        tr_fn = translate_non_alphanumerics(pdfinfo['pdflink_text'])[:100] + ".pdf"
        assert type(tr_fn) == unicode
        output_directory = os.path.join(config.get('PBoptions', 'workingdir'), author, tag, pdfinfo['pdflink_context'])
        assert type(output_directory) == unicode
        if not os.path.isdir(output_directory): 
            os.makedirs(output_directory)
        existfiles = [fl[9:] for fl in os.listdir(output_directory)] #files with their date prefixes stripped out
        if tr_fn in existfiles: 
            wx.PostEvent(notify_window, pieUpdateEvent('pass', 'Already downloaded', cite=pdfinfo['pdflink_text'], href=pdfinfo['pdflink'], updatelast=True))
            return
        outfilename = os.path.join(output_directory, tr_fn)     
        assert type(outfilename) == unicode
        urllib.urlretrieve(pdfinfo['pdflink'], outfilename)
        # try:
        # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        # opener.addheaders = [('User-agent', 'Firefox/3.6.1')]

        # # print 'Opening', pdfinfo['pdflink']
        # doc = opener.open(pdfinfo['pdflink'])
        # # except:
        # #     try: #fall back to the simpler urllib
        # #         doc = urllib.urlopen(pdfinfo['pdflink'])
        # #     except:
        # #         raise Exception, 'Dodgy URL'
        # # doc = urllib2.urlopen(pdfinfo['pdflink'])
        # docdata = doc.read()
        # outfile = open(outfilename, 'wb')
        # outfile.write(docdata)
        # outfile.close()
        return outfilename
    except Exception, err:
        traceback.print_exc()
        wx.PostEvent(notify_window, pieUpdateEvent('fail', "FAILED to download", cite=pdfinfo['pdflink_text'], href=pdfinfo['pdflink'], updatelast=True))
        raise Exception

def get_internal_pdf_metadata(notify_window, pdfinfo):
    retinfo = {}
    retinfo['creation_date'] = time.localtime()
    retinfo['internal_author'] = ''
    retinfo['internal_title'] = ''
    try:
        pdf_file = file(pdfinfo['outfilename'], 'rb')
        pdfread = PdfFileReader(pdf_file)
        docmetadata = pdfread.getDocumentInfo()
    except:
        traceback.print_exc()
        if pdfinfo.has_key('pdflink_text'): lt = pdfinfo['pdflink_text'] 
        else: lt = ''
        wx.PostEvent(notify_window, pieUpdateEvent('fail', "Unreadable", cite=lt, href=pdfinfo['outfilename'], updatelast=True))
        pdf_file.close()
        return retinfo
    if docmetadata == None:
        docmetadata = {} #pyPdf appears to send Nonetypes instead of
                         #empty dicts, annoyingly
    # creation date is found here. if not present, fall back to current date
    try:
        if docmetadata.has_key('/CreationDate'):
            rd = docmetadata['/CreationDate'][2:]
            retinfo['creation_date'] = time.strptime("%s %s %s %s %s" % (rd[0:4], rd[4:6], rd[6:8], rd[8:10], rd[10:12]), "%Y %m %d %H %M")
            retinfo['creation_date_guessed'] = False
        else:
            retinfo['creation_date_guessed'] = True
    except: #hack ... but sometimes /creationdate is bunged
        traceback.print_exc()
        retinfo['creation_date_guessed'] = True

    retinfo['download_time'] = time.localtime()
    # some reformatting necessary when author names are computer-inserted
    splre = re.compile("[./_ ]")
    authst = ''
    if not pdfread.documentInfo:
        return retinfo
    if pdfread.documentInfo.author:
        authst = string.join(splre.split(pdfread.documentInfo.author))
        authst = string.capwords(authst)
    retinfo['internal_author'] = authst
    retinfo['internal_title'] = unicode(pdfread.documentInfo.title)
    pdf_file.close()
    return retinfo
        
def gen_title_and_docname(pdfinfo, behaviour):
    '''format the appropriate title and document name'''
    retdata = {}
    if behaviour == 'prepend':
        retdata['title'] = u"%s: %s" % (pdfinfo['tag'], pdfinfo['pdflink_text'])
    elif behaviour == 'append_hyphen':
        retdata['title'] = u"%s - %s" % (pdfinfo['pdflink_text'], pdfinfo['tag'])
    elif behaviour == 'append_brackets':
        retdata['title'] = u"%s (%s)" % (pdfinfo['pdflink_text'], pdfinfo['tag'])
    else:
        retdata['title'] = pdfinfo['pdflink_text']
    assert type(retdata['title']) == unicode
    final_fn = os.path.join(config.get('PBoptions', 'workingdir'), pdfinfo['author'], pdfinfo['tag'], pdfinfo['pdflink_context'], "%s %s" % (time.strftime("%Y%m%d", pdfinfo['creation_date']), os.path.basename(pdfinfo['outfilename'])))
    retdata['final_fn'] = final_fn
    assert type(retdata['final_fn']) == unicode
    return retdata

def prefetch_page_info(notify_window, url):
    '''pre-fetch a page header to assist determing pre/postfix'''
    try:    
        wx.PostEvent(notify_window, pieUpdateEvent('pass', "Reading..."))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        # print 'Opening', pdfinfo['pdflink']
        thepage = opener.open(url)
        # if sys.version_info >= (2,6):
        #     thepage = urllib2.urlopen(url, data=None, timeout=1) 
        # else:
        #     thepage = urllib2.urlopen(url, data=None) 
        # timeout is 1s, we don't want to hang the UI waiting 
    except ValueError:
        traceback.print_exc()
        wx.PostEvent(notify_window, pieUpdateEvent('warn', "Not a valid or recognised url", updatelast=True))
        return 
    except: 
        wx.PostEvent(notify_window, pieUpdateEvent('warn', "Not a valid or recognised url", updatelast=True))
        traceback.print_exc()
        return 
    thehtml = thepage.read()
    try:
        readup = BeautifulSoup(thehtml)
    except Exception, err:
        traceback.print_exc()
        wx.PostEvent(notify_window, pieUpdateEvent('warn', "Invalid or unparseable HTML", updatelast=True))
        return 
    tag = translate_non_alphanumerics(readup.title.string.split(' - ')[0][:100].strip())
    wx.PostEvent(notify_window, pieUpdateEvent('pass', "Read.", updatelast=True))
    assert type(tag) == unicode
    return tag

    

