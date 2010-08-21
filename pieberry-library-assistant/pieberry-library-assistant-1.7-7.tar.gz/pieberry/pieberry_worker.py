import wx
import sys, os, os.path, time, string, re
import traceback
from threading import Thread
from pieberry_config import *
from pieberry_exec import *
from pieberry_events import *


if sys.version_info >= (2,6):
    from os.path import relpath as relpath
else:
    from utility.relpath import truncpath as relpath

# pieberry bibdata dicts may contain: 
# author    = *bibtex author string
# title     = *bibtex title string
# year      = *bibtex year
# month     = *bibtex month
# note      = *bibtex note
# annote    = *bibtex annote
# url       = bibtex url
# internal_author = author from file metadata
# internal_title  = title from file metadata
# bibtex_key      = bibtex key (only once saved or specifically set by user)
# bibtex_type     = *bibtex entry type (set to default value for downloads)
# howpublished    = *bibtex howpublished, perhaps with embedded \url or \href
# pdflink         = original link of pdf
# pdflink_context = context string for pdf (e.g. 'submission')
# pdflink_text    = original text string of pdf link
# final_fn        = final resting place of the downloaded file on filesystem
# outfilename     = temporary first location of downloaded file
# exclude         = (bool) should this entry be excluded from the bibliography
# creation_date   = (time_t) creation date of document
# download_time   = (time_t) download time of document
# creation_date_guessed  = (bool) whether the creation date was guessed (t) or gleaned from metadata (f)
# corporate_author       = (bool) is the author in 'author' "corporate" (t) or a person(s) (f)
# ancillary_creationtime = (time_t) deprecated - creation time of document - same as creation_date
# ancillary_outfilename  = deprecated - same as final_fn
# ancillary_locofdoc     = deprecated - same as pdflink
# ancillary_downloadtime = deprecated - same as download_time

class piePrefetchThread(Thread):
    '''thread to prefetch page info'''
    def __init__(self, notify_window, url):
        Thread.__init__(self)
        self._notify_window = notify_window
        self._url = url
        self.start()
    def run(self):
        tag = prefetch_page_info(self._notify_window, self._url)
        if tag:
            wx.PostEvent(self._notify_window, piePrefetchEvent(tag))

class pieWorkerThread(Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window, scrapedata, scrapecommands):
        """Init Worker Thread Class.
        scrapecommands should contain the following:
          - tag_behaviour o(prepend, append_hyphen, append_brackets, dironly)
          - [support recursion some time in future?]
        scrapedata should contain the following:
          - author
          - tag
          - url 
          """
        Thread.__init__(self)
        self._notify_window = notify_window
        self._scrapedata = scrapedata # data from user as necessary
        self._scrapecommands = scrapecommands # directions from user/ui
        self._bibdata = {}
        self._want_abort = 0
        self.start()
 
    def run(self):
        """Run Worker Thread."""
        #TODO - need property to denote if corporate author
        try:
            html = fetch_page(self._notify_window, self._scrapedata['url'])
            pdfs = snarf_pdfs(self._notify_window, html, self._scrapedata['url'])
        except:
            traceback.print_exc()
            # wx.PostEvent(self._notify_window, pieUpdateEvent('fail', 'Failed'))
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return
        curr_pdf_link = 0
        num_pdf_links = len(pdfs)
        re_submission = re.compile(r'^(.+?)(\'s)?( -)? [sS]ubmission')
        return_data = {}
        for pdf in pdfs:
            curr_pdf_link += 1
            if self._want_abort == 1:
                break
            pdf['author'] = self._scrapedata['author']
            pdf['tag'] = self._scrapedata['tag']
            wx.PostEvent(self._notify_window, pieUpdateEvent('spin', '[%d/%d] Downloading' % (curr_pdf_link, num_pdf_links), cite=pdf['pdflink_text'], href=pdf['pdflink']))
            try:
                pdf['outfilename'] = download_pdf(self._notify_window, pdf, author=self._scrapedata['author'], tag=self._scrapedata['tag'])
            except:
                continue
            if not pdf['outfilename']:
                continue # there was a problem, couldn't download?
            int_metadata = get_internal_pdf_metadata(self._notify_window, pdf)
            if int_metadata == None:
                continue # there was a problem, already downloaded?
            pdf.update(int_metadata)
            # by this point, 'pdf' should have the following keys:
            # author, tag, outfilename, pdflink, pdflink_text,
            # pdflink_context, creation_date, download_time,
            # [internal_author, internal_title]
            titles = gen_title_and_docname(pdf, self._scrapecommands['tag_behaviour'])
            # and now - title, final_fn
            pdf['title'] = titles['title']
            try:
                os.renames(pdf['outfilename'], titles['final_fn'])
                pdf['final_fn'] = titles['final_fn']
            except:
                print 'Could not rename file'
                pdf['final_fn'] = pdf['outfilename']
            #reauthor for submission - this begs for a more considered approach;
            #rather dodgy assumption that submissions are always titled 'person's submission...'
            if pdf['pdflink_context'] == 'submissions':
                submatch = re_submission.match(pdf['pdflink_text'])
                if submatch:
                    pdf['author'] = submatch.group(1)
            # user may choose what to in/exclude later
            pdf['bibtex_type'] = config.get('PBoptions', 'default_bibtex_entry_type')
            hpstyle = config.getint('PBoptions', 'default_bibtex_entry_style')
            if hpstyle in (0, 3):
                pdf['howpublished'] = u'On the web'
            elif hpstyle == 1:
                pdf['howpublished'] = u'\\url{%s}' % pdf['pdflink']
            elif hpstyle == 2:
                pdf['howpublished'] = u'\\href{%s}{%s}' % (pdf['pdflink'], 'On the web')
            pdf['url'] = pdf['pdflink']
            pdf['year'] = unicode(time.strftime("%Y", pdf['creation_date']))
            pdf['month'] = unicode(time.strftime("%B", pdf['creation_date']))
            pdf['annote'] = 'Downloaded_on: %s\nPublication_date: %s\nSaved_to: %s\nAuthor_from_metadata: %s\nTitle_from_metadata: %s' % (
                time.ctime(), 
                time.ctime(time.mktime(pdf['creation_date'])), 
                relpath(pdf['final_fn'], config.get('PBoptions', 'workingdir')),
                pdf['internal_author'], 
                pdf['internal_title']
                )
            pdf['note'] = ''
            data_id = wx.NewId()
            if pdf['pdflink_context'] in exclude_by_default:
                pdf['exclude'] = True
                wx.PostEvent(self._notify_window, pieUpdateEvent('exclude', 'Success', cite="%s (%s). %s" % (pdf['author'], pdf['year'], pdf['title']), href=pdf['pdflink'], data_id=data_id, updatelast=True))
            else:
                pdf['exclude'] = False
                wx.PostEvent(self._notify_window, pieUpdateEvent('success', 'Success', cite="%s (%s). %s" % (pdf['author'], pdf['year'], pdf['title']), href=pdf['pdflink'], data_id=data_id, updatelast=True))
            return_data[data_id] = pdf
        wx.PostEvent(self._notify_window, ResultEvent(return_data))
 
    def abort(self):
        """abort worker thread."""
        self._want_abort = 1
                         


if __name__ == '__main__':
    print 'ok'
                             
