from django.conf import settings

 # __init__.py
TO_DICT_ATTR    = getattr(settings, 'MEGAFEED_TO_DICT_ATTR',    'to_dict' )
FILTER_ATTR     = getattr(settings, 'MEGAFEED_FILTER_ATTR',     'filter'  )
MEGAFEED_ATTR   = getattr(settings, 'MEGAFEED_MEGAFEED_ATTR',   'megafeed')
PAGE_PREFIX     = getattr(settings, 'MEGAFEED_PAGE_PREFIX',     'page'    )
PER_PAGE_PREFIX = getattr(settings, 'MEGAFEED_PER_PAGE_PREFIX', 'per_page')
EXPAND_RELATED  = getattr(settings, 'MEGAFEED_EXPAND_RELATED',  'expand'  )
ORDERING        = getattr(settings, 'MEGAFEED_ORDERING',        'order'   )
TO_DICT_FN      = getattr(settings, 'MEGAFEED_TO_DICT_FN',       {}       )
START_PREFIX    = getattr(settings, 'MEGAFEED_START_PREFIX',    'start'   )
OR_QUERY        = getattr(settings, 'MEGAFEED_OR_QUERY',        'or'      )

DISTINCT_ATTR   = getattr(settings, 'MEGAFEED_DISTINCT_ATTR',   'distinct')

try:
    DEFAULT_SELECT_DISTINCT = settings.MEGAFEED_DEFAULT_SELECT_DISTINCT
except AttributeError:
    print 'Depreciation Warning: Auto SELECT DISTINCT may be removed in a future release.'
    print 'To disable now, set MEGAFEED_DEFAULT_SELECT_DISTINCT = False in your settings.'
    print 'To preserve current behavior, set MEGAFEED_DEFAULT_SELECT_DISTINCT = True.'
    print
    DEFAULT_SELECT_DISTINCT = True
    
try:
    DEFAULT_PAGINATE = settings.MEGAFEED_DEFAULT_PAGINATE
except AttributeError:
    print 'Depreciation Warning: Auto pagination may be removed in a future release.'
    print 'To disable now, set MEGAFEED_DEFAULT_PAGINATE = False in your settings.'
    print 'To preserve current behavior, set MEGAFEED_DEFAULT_PAGINATE = True.'
    print
    DEFAULT_PAGINATE = True
    

 # Extension
ALL_TAGS_ATTR   = getattr(settings, 'MEGAFEED_ALL_TAGS_ATTR',   'all_tags')
ANY_TAGS_ATTR   = getattr(settings, 'MEGAFEED_ANY_TAGS_ATTR',   'any_tags')

 # views.py
#DEFAULT_FEED_PREFIX = getattr(settings, 'MEGAFEED_DEFAULT_FEED_PREFIX', 'feed')
MODEL_SPECIFIER = getattr(settings, 'MEGAFEED_MODEL_SPECIFIER', 'model'   )
PAGINATE_ARG    = getattr(settings, 'MEGAFEED_PAGINATE_ARG   ', 'paginate')

 # middleware.py
JSONP_PREFIX    = getattr(settings, 'MEGAFEED_JSONP_PREFIX',    'jsonp'   )
JSON_DEFAULT    = getattr(settings, 'MEGAFEED_JSON_DEFAULT',    str       )
SHOW_QUERIES    = getattr(settings, 'MEGAFEED_SHOW_QUERIES',    False     )

 # Serialized Errors
BAD_FEED = {'error': '1000', 'message': 'Specified feed not found'}
