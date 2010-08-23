from urllib import quote_plus

from django.db import models
from django.core.exceptions import ValidationError

import dspace

from bookreader.fields import MultiValueDictField



class Repository(models.Model):
    url = models.URLField()
    name = models.CharField(max_length=255, editable=False)
    
    class Meta:
        verbose_name_plural = u'repositories'
        ordering = ('name',)
    
    def __unicode__(self):
        if self.name and self.url:
            return '%s (%s)' % (self.name, self.url,)
        elif self.name:
            return self.name
        elif self.url:
            return self.url
        else:
            return self.pk
    
    def connection(self, **kwargs):
        return dspace.Repository(self.url, **kwargs)
    
    def validate_collection_handle(self, handle):
        return self.connection()._extractSet(handle) in self.collection_handles
    
    @property
    def collection_handles(self):
        return map(lambda c: c[0], self.connection().getCollections())
    
class Collection(models.Model):
    repository = models.ForeignKey(Repository, related_name='collections')
    handle = models.CharField(max_length=255)
    name = models.CharField(max_length=255, editable=False)
    
    class Meta:
        unique_together = ('repository','handle')
        ordering = ('name','handle',)
    
    def __unicode__(self):
        return self.name
    
    def clean_fields(self, exclude=None):
        errors = {}
        
        if exclude is None:
            exclude = []
        
        try:
            super(Collection, self).clean_fields(exclude=exclude)
        except ValidationError, e:
            errors = e.update_error_dict(errors)
        
        if not 'handle' in exclude:
            if not self.repository.validate_collection_handle(self.handle):
                message = '%s is not a valid collection handle for %s' % (self.handle,
                                                                          str(self.repository),)
                
                errors.setdefault('handle',[]).append(message)
        if errors:
            raise ValidationError(errors)
        

class Book(models.Model):
    identifier = models.CharField(max_length=255, primary_key=True, editable=False)
    collection = models.ForeignKey(Collection, related_name='books', editable=False)
    
    title = models.CharField(max_length=255,editable=False)
    creator = models.CharField(max_length=255, null=True, blank=True, editable=False)
    created = models.CharField(max_length=255, null=True, blank=True, editable=False)
    issued = models.DateTimeField(editable=False)
    
    thumbnail = models.URLField(null=True, blank=True)
    
    additional_metadata = MultiValueDictField(null=True, blank=True)
    
    class Meta:
        ordering = ('title',)
    
    def __unicode__(self):
        return self.title
    
    @property
    def handle(self):
        return self.identifier.rsplit(':',1)[-1]
    
    @property
    def repository_url(self):
        oai, host, handle = self.identifier.split(':',2)
        
        return 'http://%s/handle/%s' % (host, handle,)
    
    @property
    def first_page(self):
        try:
            return Page.objects.filter(book=self).order_by('sequence')[0]
        except:
            return None
    
    @property
    def offset_reading_view(self):
        offset = self.additional_metadata.get('offset',None)
        if offset is None:
            return True
        
        if offset.lower() in ('true','y','yes',):
            return True
        elif offset.lower() in ('false','n','no',):
            return False
        
        try:
            offset = int(offset)
            return bool(offset % 2)
        except Exception:
            pass
        
        return True

class Page(models.Model):
    book = models.ForeignKey(Book, related_name='pages')
    title = models.CharField(max_length=255)
    sequence = models.PositiveIntegerField(default=9999)
    jp2 = models.URLField()
    thumbnail = models.URLField(blank=True, null=True)
    
    def __unicode__(self):
        return "%s (%s)" % (self.title, self.book.title)
    
    @property
    def reading_page(self):
        sequence = self.sequence
        
        if not self.book.offset_reading_view:
            sequence -= 1
        return sequence / 2 + 1
    
    class Meta:
        ordering = ('book', 'sequence', 'title',)

class Link(models.Model):
    book = models.ForeignKey(Book, related_name='links')
    title = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=255)
    size = models.PositiveIntegerField(blank=True, null=True)
    bundle = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField()
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        ordering = ('book','title',)

