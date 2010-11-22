from django.db.models import Q
from django.utils.text import smart_split,unescape_string_literal
import operator

def raw_search(query, fields, raw_search):
    """ Performs a search based on the raw search string. Returns a new
            query filtered with the search. """
    return search(query, fields, extract_terms(raw_search))

def search(query, fields, terms):
    """ Performs a search based on a list of search terms. Returns a new
            query filtered with the search. """

    if len(terms) > 0:

        search_list = []
        
        for term in terms:
            field_list = []
            for field in fields:
                field_list.append(Q(**{field + '__icontains':term}))
            search_list.append(reduce(operator.or_, field_list))
        
        return query.filter(reduce(operator.and_, search_list))

    else:
        return query
    
def extract_terms(raw):
    """ Extraction based on spaces, understands double and single quotes. Returns a list of strings """

    terms = list(smart_split(raw))

    print terms
    for i,term in enumerate(terms):
        try:
            terms[i] = unescape_string_literal(terms)
        except ValueError:
            pass
    return terms
