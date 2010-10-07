

class Memo(object):
    """ A lightweight, picklable container for document data.  Contain
    all the data elements necessary to construct a xapaian document."""

    def __init__(self):
        self.lang = None
        self.terms = []    # (term, type) | (term, type, wdfinc)
        self.posts = []    # (term, position) | (term, position, wdfinc)
        self.texts = []    # {text=u"", lang=None, stem=True, stop=True}
        self.values = []   # (name, value, type)
        self.data = None   # bytestring or None

    @classmethod
    def from_dict(cls, data):
        """ Construct a Memo from a data dictionary. """
        m = cls()
        m.lang = data.get('lang')
        m.terms = data.get('terms', [])
        m.posts = data.get('posts', [])
        m.texts = data.get('texts', [])
        m.values = data.get('values', [])
        m.data = data.get('data')
        return m

    @property
    def dict(self):
        """ Returns a dictionary representation of the document. """
        return dict(
            lang=self.lang,
            terms=self.terms,
            posts=self.posts,
            texts=self.texts,
            values=self.values,
            data=self.data)

    def add_term(self, term, boolean=False, wdfinc=None):
        typ = 'b' if boolean else 'r'
        term = (term, typ, wdfinc) if wdfinc else (term, typ)
        self.terms.append(term)

    def add_post(self, term, position, wdfinc=None):
        term = (term, position, wdfinc) if wdfinc else (term, position)
        self.posts.append(term)

    def add_text(self, text, prefix=None, lang=None,
                 post=True, stem=True, stop=True, spell=True):
        self.texts.append(dict(text=text,
                               prefix=prefix,
                               lang=lang,
                               post=post,
                               stem=stem,
                               stop=stop,
                               spell=True,
                               ))

    def add_value(self, name, value, type):
        self.values.append((name, value, type))

    def set_data(self, data):
        self.data = data

    def set_lang(self, lang):
        self.lang = lang
