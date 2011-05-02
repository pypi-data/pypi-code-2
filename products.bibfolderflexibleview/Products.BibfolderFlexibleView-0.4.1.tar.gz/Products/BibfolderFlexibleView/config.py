GLOBALS = globals()
PKG_NAME = "BibfolderFlexibleView"
PROJECTNAME = "BibfolderFlexibleView"

# unschoen: absolute_url ist ueber getRemoteUrl() in den brains
# schon verfuegbar, aber damits nich zu kompliziert wird brauchen
# wirs mit dem selben namen wie im objekt selbst
CATALOG_METADATA_ENTRIES = ('publication_url', 'absolute_url')

BIBFOLDERLIKE_TYPES = ('BibliographyFolder', 'ATBiblioTopic')

DISPLAY_VIEWS = {
     'BibliographyFolder' : ('bibfolder_flexible_view',),
     'ATBiblioTopic': ('bibfolder_flexible_view',),
          }

MASKS = {"<dt title='%abs'><a href='%l'>%T</a></dt> <dd><i>%A</i><br />%src<br />%o</dd>": (
    'ArticleReference', 
    'BookletReference', 
    'BookReference', 
    'ConferenceReference', 
    'InbookReference', 
    'IncollectionReference', 
    'InproceedingsReference', 
    'ManualReference', 
    'MastersthesisReference', 
    'MiscReference', 
    'PhdthesisReference', 
    'PreprintReference', 
    'ProceedingsReference', 
    'TechreportReference', 
    'UnpublishedReference', 
    'WebpublishedReference',
            ),    
        }


CATEGORIES  = {
             'all':                 ['ArticleReference', 'BookReference', 'InbookReference', 'ProceedingsReference', 'InproceedingsReference', 'MiscReference', 'PhdthesisReference', 'MasterthesisReference'],
             'journal articles':    ['ArticleReference'],
             'books':               ['BookReference'],
             'book chapters':       ['InbookReference'],
             'conference articles': ['InproceedingsReference'],
             'proceedings':         ['ProceedingsReference'],
             'poster':              ['MiscReference'],
             'theses':              ['PhdthesisReference', 'MasterthesisReference']
             }

DEBUG = 0  ## hide debug messages 
#DEBUG = 1  ## see debug messages

