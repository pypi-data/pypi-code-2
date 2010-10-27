from django.shortcuts import get_object_or_404
from django.views.generic import list_detail

from bookreader.models import Repository, Book

def browse(request, **kwargs):
    kwargs.setdefault('template_object_name','repository')
    kwargs.setdefault('queryset', Repository.objects.all())
    return list_detail.object_list(request, **kwargs)

def view(request, object_id, **kwargs):
    repository = get_object_or_404(Repository, pk=object_id)
    
    kwargs.setdefault('template_object_name','collection')
    kwargs.setdefault('template_name', 'bookreader/repository_detail.html')
    kwargs.setdefault('queryset', repository.collections.all())
    kwargs.setdefault('extra_context', {})
    kwargs['extra_context']['repository'] = repository
    
    return list_detail.object_list(request, **kwargs)
    
def books(request, object_id, **kwargs):
    repository = get_object_or_404(Repository, pk=object_id)
    
    kwargs.setdefault('template_object_name','book')
    kwargs.setdefault('template_name', 'bookreader/repository_books.html')
    kwargs.setdefault('queryset', Book.objects.filter(collection__repository=repository))
    kwargs.setdefault('extra_context', {})
    kwargs['extra_context']['repository'] = repository
    
    return list_detail.object_list(request, **kwargs)
    