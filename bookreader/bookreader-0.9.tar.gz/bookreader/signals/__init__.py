from django.db.models.signals import pre_save, post_save
from django.conf import settings

from bookreader.models import Repository, Collection, Book
from bookreader.signals import repository, collection, book

if 'bookreader' in settings.INSTALLED_APPS and settings.BOOKREADER_SIGNALS_ENABLED:
    pre_save.connect(repository.lookup_name, sender=Repository)
    
    pre_save.connect(collection.lookup_name, sender=Collection)
    post_save.connect(collection.load_books, sender=Collection)
    
    pre_save.connect(book.load_metadata, sender=Book)
    #post_save.connect(book.load_pages, sender=Book)
    #post_save.connect(book.load_links, sender=Book)