from django.conf import settings

from bookreader.models import Book



def comparison_books(request):
    if settings.BOOKREADER_COMPARISON_GET_ARGUMENT in request.GET:
        compare = request.GET.getlist(settings.BOOKREADER_COMPARISON_GET_ARGUMENT)
    elif settings.BOOKREADER_COMPARISON_SESSION_KEY in request.session:
        compare = request.session.get(settings.BOOKREADER_COMPARISON_SESSION_KEY)
    else:
        return {}
    
    books = []
    for book in compare:
        try:
            books.append(Book.objects.get(identifier=book))
        except Book.DoesNotExist:
            pass
    
    return {settings.BOOKREADER_COMPARISON_TEMPLATE_VARIABLE: books}
