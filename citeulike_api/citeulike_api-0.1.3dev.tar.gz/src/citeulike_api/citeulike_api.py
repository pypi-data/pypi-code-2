# encoding: utf-8
"""
fetch a supplied user's bookmarks somewhere, optionally writing them out into a file
"""
from string import Template
import re
import codecs
from string import capwords
from copy import deepcopy
import importlib
try:
    import simplejson as json
except ImportError:
    import json
from calendar import month_name
from util import get_code_revision
import time
import mechanize
import os.path
import hashlib
import openmeta
import glob

def sha1_digest(userfiles):
    """return a hex digest of some bytes"""
    return hashlib.sha1(userfiles).hexdigest()
    
#from the CUL webform
# <option value="BOOK" >Book</option> 
# <option value="CHAP" >Book chapter/section</option> 
# <option value="PAMP" >Booklet</option> 
# <option value="INCOL" >Book part (with own title)</option> 
# <option value="INCONF" >Conference proceedings (article)</option> 
# <option value="CONF" >Conference proceedings (whole)</option> 
# <option value="DATA" >Data file</option> 
# <option value="ELEC" >Electronic citation</option> 
# <option value="INPR" >In the press</option> 
# <option value="JOUR" selected="selected">Journal article</option> 
# <option value="MANUAL" >Manual (technical documentation)</option> 
# <option value="GEN" >Miscellaneous</option> 
# <option value="REP" >Technical report</option> 
# <option value="STD" >Technical Standard</option> 
# <option value="MTHES" >Thesis (Master's)</option> 
# <option value="THES" >Thesis (PhD)</option> 
# <option value="UNPB" >Unpublished work</option> 

CUL_FIELDS = {
  'JOUR': 'article', 
  'BOOK': 'book', 
  'PAMP': 'booklet', 
  'CHAP': 'inbook', 
  'INCOL': 'incollection', 
  'INCONF': 'inproceedings', 
  'MANUAL': 'manual', 
  'MTHES': 'mastersthesis', 
  'THES': 'phdthesis', 
  'CONF': 'proceedings', 
  'REP': 'techreport', 
  'STD': 'techreport', 
  'UNPB': 'unpublished', 
  # '?patent': 'patent',
  # '?collection': 'collection',
  'ELEC': 'electronic',
  'GEN': 'misc',
  'DATA': 'misc',
  'INPR': 'misc',
}

FIELDS_THAT_GET_SPURIOUS_BRACES = {
  "journal": "journal",
  "authors": "authors",
  "abstract": "abstract",
  "title": "title",
  "location": "location",
  "address": "address",
  "booktitle": "title_secondary"
}

#anglocentric stopwords
STOP_WORDS = set([
  'In', 'To', 'For', 'At', 'With', 'A', 'An', 'And', 'The', 'On', 'By', 'Of'
])

_edit_priority_url = Template(
  "http://www.citeulike.org/editpriority.json?"
  "user_article_id=579067&article_id=1137810&"
  "to_read=4&callback=jsonp1282733494417"
)
_all_bibtex_t = Template(
  "http://www.citeulike.org/bibtex/user/${username}"
  "?key_type=4&clean_urls=0"
)
_all_json_t = Template(
  "http://www.citeulike.org/json/user/${username}"
)
_article_edit_t = Template(
  "http://www.citeulike.org/edit_article_details?"
  "username=${username}&article_id=${article_id}"
)
_article_view_t = Template(
  "http://www.citeulike.org/user/${username}/article/${article_id}"
)
_attachment_t= Template(
  "http://www.citeulike.org${path}"
)

_base_url = 'http://www.citeulike.org/'

_cul = None

class CulError(Exception):
    pass

# handy filters
def BRACE_IN_TITLE(rec):
    return rec['title'].find('{')>=0

def BRACE_IN_QUESTIONABLE_LOCATION(rec):
    field_vals = []
    for field in FIELDS_THAT_GET_SPURIOUS_BRACES:
        field_val = rec.get(field)
        if field_val is None: continue
        if isinstance(field_val, basestring):
            field_vals.append(field_val)
        else:
            for sub_val in field_val:
                field_vals.append(sub_val)
    return any([
      field_val.find('{')>=0
      for field_val in field_vals
    ])

def HAS_SHOUT_CAPS(rec):
    return rec['title']==rec['title'].upper()

def get_browser(debug=False):
    """create a browser, optionally with debugging enabled"""
    import socket
    socket.setdefaulttimeout(20.0)
    import mechanize
    
    browser = mechanize.Browser()
    
    if debug:
        import logging
        import sys
        # Log information about HTTP redirects and Refreshes.
        browser.set_debug_redirects(True)
        # Log HTTP response bodies (ie. the HTML, most of the time).
        browser.set_debug_responses(True)
        # Print HTTP headers.
        browser.set_debug_http(True)

        # To make sure you're seeing all debug output:
        logger = logging.getLogger("mechanize")
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(logging.INFO)
    return browser

def fetch_all_bibtex(username="livingthingdan", password=None, filepath=None):
    """fetch a whole library in bibtex format.
    
    we should probably do this authenticated using the below CUL client class"""
    
    cul = get_cul(username, password)
    return cul.download_bibtex(dumpfile=filepath)

def fetch_all_json(username="livingthingdan", password=None, filepath=None):
    """fetch a whole library in JSON format."""
    cul = get_cul(username, password)
    return cul.download_json_index(json_cache=filepath)

def tokenise(f):
    return [t for t in re.split(r'[-\s]+', f) if t]
    
def topwords_iter(f):
    """yield non-stopword tokens """
    for t in tokenise(f):
        t = stripped_word(t)
        if t not in STOP_WORDS:
            yield t

def topwords(f):
    """return non-stopword tokens"""
    return list(topwords_iter(f))

def get_sirname(creators):
    return stripped_word(tokenise(creators[0])[-1])
    
def stripped_word(w):
    """remove punctuation and return a word initial-capped"""
    return capwords(re.sub(r'[^\w]*', '', w))

def strip_html_tags(value):
    """Returns the given HTML with all tags stripped."""
    return re.sub(r'<[^>]*?>', '', unicode(value))

def create_key(obj):
    """create a citeulike-like AuthorYearTitle key from a record.
    probably not the same as theirs, which handles name prefixes better."""
    key = []
    creators = obj.get('authors', obj.get('editors', ['Anonymous']))
    key.append(get_sirname(creators))
    if obj.get('published', False):
        key.append(obj['published'][0])
    key.append(topwords_iter(obj['title']).next())
    return ''.join(key)
    
def strip_wrapping_braces(field):
    #delete leading space and braces
    field = re.sub(r'^[{\s]*', '', field)
    #delete trailing space and braces
    return re.sub(r'[}\s]*$', '', field)

def strip_braces(field):
    return field.replace('{', '').replace('}', '')

def strip_tex_nonsense(ustring):
    ustring = ustring.replace('\\', '')
    ustring = ustring.replace(r'{', '')
    ustring = ustring.replace(r'}', '')
    ustring = ustring.replace(r'"', '')
    return ustring
    
def open_article_for_edit(article_id, username, password):
    # from subprocess import popen
    import webbrowser
    import urlparse
    cul = get_cul(username, password)
    edit_path = cul.get_edit_url(article_id)
    edit_url = urlparse.urljoin(_base_url, edit_path)
    webbrowser.open_new_tab(edit_url)

def get_cul(username, *args, **kwargs):
    """return the last browser used, or create a new one with the supplied
    pasword"""
    global _cul
    if not _cul: 
        _cul = CiteULike(username, *args, **kwargs)
    return _cul
    
def auto_edit_article(article_id, username, password):
    cul = get_cul(username, password)
    cul.kill_cite_key(article_id)

def clean_article(obj):
    """returns a record dict with certain CUL fuckups corrected."""
    obj = deepcopy(obj)
    for creator_field in ('authors', 'editors'):
        creator_list = obj.get(creator_field, None)
        if not creator_list: continue
        obj[creator_field] = [strip_braces(n) for n in creator_list]
    return obj

class CiteULike(object):
    
    MIN_API_WAIT = 5
    
    def __init__(self, username,
          password=None,
          json_cache=None,
          attachment_path=None,
          debug=False,):
        """set up an object to access CUL
        If you omit username but suply the path to a acached copy of the JSON output, then you can still do useful things in an "offline mode"
        """
        # first set up the socket handling to a value reflective of CiteULike's
        # somewhat frequent, er, network difficulties
        
        #set up state for anonymous use
        self.username = username
        self.logged_in = False
        self.debug = debug
        
        browser = get_browser(debug=debug)
        browser.set_handle_robots(False)
        user_agent_string = "CiteULikeApi %s" % get_code_revision()
        browser.addheaders = [
          ("User-agent", user_agent_string),
        ]
        self.browser = browser
        
        self.last_api_access = time.time() - self.MIN_API_WAIT
        
        #now, if password is provided, log in
        if password is not None:
            self.login(username, password)
        
        # set up record cache
        self.records = []
        self.json_cache = json_cache
        
        # if we ARE set up to use a cache file, try to load its contents now
        if json_cache:
            self.load_json_from_cache(json_cache)
        
        self.attachment_path = attachment_path
        if attachment_path is not None:
            self.attachment_path = os.path.realpath(attachment_path)
        
        if openmeta.is_openmeta_working():
            self.tagger = openmeta.set_tags
        else:
            def _dummy_tagger(*args, **kwargs):
                pass
            self.tagger = _dummy_tagger
    
    def wait_for_api_limit(self, min_wait=0):
        min_wait = max(min_wait, self.MIN_API_WAIT)
        now = time.time()
        elapsed_time = now - self.last_api_access
        if elapsed_time<min_wait:
            time.sleep(min_wait-elapsed_time)
        self.last_api_access = time.time()
    
    def login(self, username, password):
        browser = self.browser
        
        browser.open('http://www.citeulike.org/login?from=/')
        self.wait_for_api_limit()
        
        browser.select_form(name='frm')
        browser['password'] = password
        browser['username'] = username
        
        self.wait_for_api_limit()
        
        try:
            #handle redirects manually to avoid connection flakiness
            browser.set_handle_redirect(False)
            resp = browser.submit()
        except mechanize.HTTPError, e:
            if e.getcode()!=302 : raise e
            next_page = e.info().getheader('Location')
            if next_page == 'http://www.citeulike.org/' :
                #success
                self.logged_in = True
            elif next_page.find('status=login-failed')>=0:
                raise CulError('Login Failed')
            else:
                err = CulError('Unknown login response')
                err.data = e
                raise err
        finally:
            browser.set_handle_redirect(True)
        
    def get_edit_url(self, article_id):
        return _article_edit_t.substitute(
          username = self.username,
          article_id=article_id)
        
    def cache_records(self, force_update=False):
        """update myself with all relevant records for rapid searching"""
        if not self.records or force_update:
            self.records = self.download_json_index()
        self.article_id_index()
        return self.records
    
    def render(self, renderer_module='bibtex', ids=None,
            attachment_path=None, *args, **kwargs):
        self._check_index()
        if attachment_path is None: attachment_path=self.attachment_path
        renderer_module = importlib.import_module(
          'citeulike.output.' + renderer_module)
        renderer = renderer_module.Renderer(
            attachment_path=attachment_path,
            *args, **kwargs)
        if ids is None:
            records = self.records
        else:
            records = tuple(self.with_ids(ids))
        return renderer.render(records)
        
    def with_ids(self, ids):
        ids = set([unicode(i) for i in ids])
        for id_ in ids:
            yield self.article_lookup[id_]
                
    def download_json_index(self, json_cache=None):
        """load the index JSON, optionally caching it locally"""
        browser = self.browser
        self.wait_for_api_limit()
        content = browser.open(
          _all_json_t.substitute(username = self.username)
          ).read()
        # Apparently we get utf-8 bytes back and have to decode to avoid ascii
        # roundtripping
        # it would be nice to use a stream decoder for this, but codecs doesn't
        # like mechanize
        content = codecs.decode(content, 'utf-8')
        
        json_cache = json_cache or self.json_cache
        if json_cache:
            with codecs.open(json_cache, 'w', encoding='utf-8') as f:
                f.write(content)
        return json.loads(content)
        
    def load_json_from_cache(self, json_cache):
        self.json_cache = json_cache
        with codecs.open(json_cache, 'r', encoding='utf-8') as f:
            self.records = json.load(f)
        self.article_id_index()
    
    def article_id_index(self):
        article_lookup = {}
        for i in xrange(len(self.records)):
            article_lookup[self.records[i]['article_id']] = self.records[i]
        self.article_lookup = article_lookup
        
    def download_bibtex(self, username = None, dumpfile=None):
        """Download the CUL bibtex.
        This is highly likely to be malformed. You'd be better off using the
        bibtex_output methods"""
        browser = self.browser
        username = username or self.username
        content = browser.open(
          _all_bibtex_t.substitute(username = username)
        )
        if dumpfile:
            with codecs.open(dumpfile, 'w', encoding='utf-8') as f:
                f.write(content)
        return content
        
    def _check_index(self):
        """do we have records laoded?"""
        if not self.records:
            raise CulError("Empty record index. Have you run "
              "load_json_from_cache or cache_records?")
         
    def bulk_apply(self, filt=None, method_names=None, method_args=None):
        self._check_index()
        
        #what to do
        if not method_names:
            method_names=['kill_cite_key']
        methods = [getattr(self, mn) for mn in method_names]
        
        if not method_args:
            method_args = {}
        
        #what to do it to
        if filt is None:
            filt = lambda x: True
        
        for rec in self.records:
            if not filt(rec): continue
            print "Batching record %s, '%s'" % (
              rec['article_id'], rec['title'])
                  
            for fn, fn_name in zip(methods, method_names):
                print "applying %s" % fn_name
                for attempt in range(4):
                    try:
                        fn(int(rec['article_id']), **method_args)
                        break
                    except IOError, e:
                        print "network problem", unicode(e)
                        if hasattr(e, 'getcode'):
                            print "HTTP code", e.getcode()
                        wait = 5*(2**attempt-1)
                        print "retrying in %d seconds" % wait
                        self.wait_for_api_limit(wait)
                        
        
    def go_to_article_form(self, article_id, fields=None):
        """point our invisible browser at the artcle change form"""
        browser = self.browser
        self.wait_for_api_limit()
        browser.open(self.get_edit_url(article_id))

        browser.select_form(
          predicate=lambda form: form.attrs.get('id')=='article'
        )
        return browser
    
    def submit_article_form(self):
        self.wait_for_api_limit()
        resp = self.browser.submit()
        if not resp.geturl().startswith('http://www.citeulike.org/user/'):
            raise CulError("some kind of form failure")
    
    #### Particular handy things i need to do often
    def kill_cite_key(self, article_id):
        """blank out the bibtex key in case you imported or copied the article
        from someone else who uses a convention you don't like.
        Less important now that CUL export multiple cite keys."""
        browser = self.go_to_article_form(article_id)
        browser.form['bibtex_import_cite'] = ""
        self.wait_for_api_limit()
        self.submit_article_form()
    
    def kill_braces(self, article_id, fields=None):
        """purge the braces that CUL wraps fields with sometimes"""
        if fields is None:
            fields = FIELDS_THAT_GET_SPURIOUS_BRACES
        print 'checking %s for braces' % article_id
        browser = self.go_to_article_form(article_id)
        for json_name, form_name in fields.iteritems():
            questionable_content = browser.form[form_name]
            better_content = '\r\n'.join([
               strip_wrapping_braces(line) for line in questionable_content.splitlines()
            ])
            browser.form[form_name] = better_content
            print '  updating %s' % json_name 
        self.wait_for_api_limit()
        self.submit_article_form()
    
    def fix_title_case(self, article_id):
        from titlecase import titlecase
        """PURGE SHOUT CASE TITLE!!!1!"""
        print 'updating %s for silly title caps' % article_id
        browser = self.go_to_article_form(article_id)
        questionable_content = browser.form['title']
        browser.form['title'] = titlecase(questionable_content)
        print '  updating "%s"' % questionable_content 
        self.wait_for_api_limit()
        self.submit_article_form()

    def download_attachments(self, article_id,
            attachment_path=None,
            force=False,
            sync_tags=True):
        """sync my pdfs etc to disk from a given article"""
        browser = self.browser
        article_id = unicode(article_id)
        if attachment_path:
            attachment_path = os.path.realpath(attachment_path)
        else:
            attachment_path = self.attachment_path
        article_meta = self.article_lookup[article_id]
        attachments = article_meta.get('userfiles', [])
        for attachment in attachments:
            local_path = os.path.join(attachment_path, attachment["name"])
            print "inspecting local path %s" % os.path.abspath(local_path)
            remote_url = _attachment_t.substitute(path=attachment["path"])
            #if the force flag is on, let's DO it
            do_download = force
            # elsewise, check if we need to
            if not force:
                if not os.path.exists(local_path):
                    print "local path %s does not exist. downloading" % \
                      os.path.abspath(local_path)
                    do_download = True
                else: #Is this sane? overwrites local annotations
                    local_sha1 = sha1_digest(open(local_path, 'rb').read())
                    if attachment['sha1'] != local_sha1:
                        do_download = True
                        print "local path SHA %s does not equal remote SHA %s" \
                          " Downloading." % \
                          (local_sha1, attachment['sha1'])
                          
            if do_download:
                remote_path = _attachment_t.substitute(path=attachment['path'])
                self.wait_for_api_limit()
                content = browser.open(remote_path).read()
                with open(local_path, 'wb') as f:
                    f.write(content)
            else:
                print "...but no need to download this one"
            
            if sync_tags:
                self.tagger(local_path, article_meta.get('tags', []))
                
    def delete_unknown_attachments(self, attachment_path=None):
        """for now, this only handles orphan PDFs"""
        if attachment_path:
            attachment_path = os.path.realpath(attachment_path)
        else:
            attachment_path = self.attachment_path
        known_attachments = set()
        for record in self.records:
            for att in record.get('userfiles', []):
                known_attachments.add(
                  os.path.abspath(
                    os.path.join(
                      attachment_path, 
                      att['name']
                    )
                  )
                )
        all_attachments = set(glob.glob(
          os.path.join(attachment_path, '*.pdf')
        ))
        
        for unknown_attachment in (all_attachments-known_attachments):
            print "unknown attachment '%s'" % unknown_attachment
            os.remove(os.path.abspath(unknown_attachment))
            
                