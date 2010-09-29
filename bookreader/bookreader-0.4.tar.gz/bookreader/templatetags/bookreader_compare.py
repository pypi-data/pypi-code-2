from urllib import urlencode, unquote
from logging import getLogger

from django import template
from django.conf import settings
from django.utils.datastructures import MultiValueDict

from bookreader.models import Book



register = template.Library()
log = getLogger('bookreader.templatetags.bookreader_compare')

def resolve_book(book):
    if book[0] == book[-1] and book[0] in ("'",'"'):
        return book[1:-1]
    else:
        return template.Variable(book)

@register.tag
def add_book_args(parser, token):
    token = token.split_contents()
    
    if len(token) != 2:
        raise template.TemplateSyntaxError, '%s tag requires a book identifier or object as an argument' % token[0]
    
    return CompareArgumentsResolverNode(add=[token[1]])

@register.tag
def remove_book_args(parser, token):
    token = token.split_contents()
    
    if len(token) != 2:
        raise template.TemplateSyntaxError, '%s tag requires a book identifier or object as an argument' % token[0]
    
    return CompareArgumentsResolverNode(remove=[token[1]])

@register.tag
def current_book_args(parser, token):
    return CompareArgumentsResolverNode(ignore_request=True)

class CompareArgumentsResolverNode(template.Node):
    def __init__(self, remove=[], add=[], ignore_request=False):
        self.remove = map(resolve_book, remove)
        self.add = map(resolve_book, add)
        self.ignore = ignore_request
    
    def render(self, context):
        if 'request' in context and not self.ignore:
            args = MultiValueDict(context['request'].GET.iterlists())
        else:
            args = MultiValueDict()
        
        books = []
        if settings.BOOKREADER_COMPARISON_TEMPLATE_VARIABLE in context:
            try:
                for book in context[settings.BOOKREADER_COMPARISON_TEMPLATE_VARIABLE]:
                    try:
                        books.append(book.identifier)
                    except:
                        log.exception('Error getting a book identifier')
            except:
                log.exception('Error iterating over already compared books')
        elif settings.BOOKREADER_COMPARISON_GET_ARGUMENT in args:
            try:
                for book in args.getlist(settings.BOOKREADER_COMPARISON_GET_ARGUMENT):
                    try:
                        books.append(unquote(book))
                    except:
                        log.exception('Error unquoting a book id from GET')
            except:
                log.exception('Error accessing GET variables')
        
        def resolve(book):
            if isinstance(book, basestring):
                return book
            book = book.resolve(context)
            
            if isinstance(book, basestring):
                return book
            
            if isinstance(book, Book):
                return book.identifier
            
            return None
        
        for book in filter(lambda b: b is not None, map(resolve, self.remove)):
            try:
                books.remove(book)
            except ValueError:
                pass
        
        for book in filter(lambda b: b is not None, map(resolve, self.add)):
            if book not in books:
                books.append(book)
        
        args.setlist(settings.BOOKREADER_COMPARISON_GET_ARGUMENT, books)
        return urlencode(dict(args.iterlists()),doseq=True)
