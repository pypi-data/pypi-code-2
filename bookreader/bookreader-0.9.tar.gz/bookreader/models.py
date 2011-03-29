from django.db import models
from django.core.exceptions import ValidationError

import dspace

from bookreader.fields import MultiValueDictField



class Repository(models.Model):
    url = models.URLField()
    name = models.CharField(max_length=255, editable=False)
    oai_path = models.CharField(max_length=255, default='dspace-oai/request')
    sword_enabled = models.BooleanField(default=False)
    sword_service_path = models.CharField(max_length=255,
                                          default='sword/servicedocument')
    sword_deposit_path = models.CharField(max_length=255,
                                          default='sword/deposit')
    sword_user = models.CharField(max_length=255, blank=True, null=True)
    sword_password = models.CharField(max_length=255, blank=True, null=True)
    
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
        kwargs.setdefault('oai_enabled', True)
        kwargs.setdefault('base_url', self.url)
        kwargs.setdefault('oai_path', self.oai_path)
        
        if self.sword_enabled:
            kwargs.setdefault('sword_enabled', True)
            kwargs.setdefault('sword_service_path', self.sword_service_path)
            kwargs.setdefault('sword_deposit_path', self.sword_deposit_path)
            if self.sword_user:
                kwargs.setdefault('sword_user', self.sword_user)
                
                if self.sword_password:
                    kwargs.setdefault('sword_password', self.sword_password)
        
        return dspace.Repository(**kwargs)
    
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
    identifier = models.CharField(max_length=255, primary_key=True,
                                  editable=False)
    collection = models.ForeignKey(Collection, related_name='books',
                                   blank=False)
    canonical = models.ForeignKey('self', related_name='copies', blank=True, 
                                  null=True,
                                  limit_choices_to={'type': 'canonical'})
    work = models.ForeignKey('self', related_name='manifestations', blank=True,
                             null=True,
                             limit_choices_to={'type': 'work'})
    
    title = models.CharField(max_length=255)
    creator = models.CharField(max_length=255, null=True, blank=True)
    created = models.CharField(max_length=255, null=True, blank=True)
    issued = models.DateTimeField(auto_now_add=True)
    
    thumbnail = models.URLField(null=True, blank=True)
    
    additional_metadata = MultiValueDictField(null=True, blank=True)
    
    type = models.CharField(max_length=32, default='extant', db_index=True,
                            choices=(
                                ('extant','Existing'),
                                ('canonical', 'Canonical'),
                                ('frankenbook', 'Frankenbook'),
                                ('work', 'Work')))
    
    published = models.BooleanField(default=True)
    
    class Meta:
        ordering = ('title',)
    
    def __unicode__(self):
        return self.title
    
    @property
    def get_detail_template_name(self):
        return u'bookreader/%s/detail.html' % (self.type,)
    
    @property
    def internal_pages(self):
        return self.pages.filter(internal=True)
    
    @property
    def external_views(self):
        return self.pages.filter(internal=False)
    
    @property
    def handle(self):
        return self.identifier.rsplit(':',1)[-1]
    
    @property
    def top_level_structure(self):
        annotations = self.annotations.filter(structural=True).order_by('offset','-length')
        
        s = []
        current = None
        
        for child in annotations:
            if current and child.offset <= current.end and child.end <= current.end:
                continue
            current = child
            s.append(child)
        
        return s
    
    @property
    def non_structural_annotations(self):
        return list(self.annotations.filter(structural=False))
    
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
    
    def clean(self):
        if self.type in ('work','canonical') and self.canonical:
            raise ValidationError('%s books cannot have the canonical field set.' % 
                                  (self.get_type_display().title(),))
        if self.type in ('work',) and self.work:
            raise ValidationError('Works cannot have the work field set.')
    
    def get_canonical_manifestations(self):
        return self.manifestations.filter(type='canonical')
    
    def get_unassociated_manifestations(self):
        return self.manifestations.exclude(type='canonical').filter(canonical=None)
        
            

class Page(models.Model):
    book = models.ForeignKey(Book, related_name='pages',
                             limit_choices_to={'type__in': ('frankenbook',
                                                            'canonical',
                                                            'extant')})
    internal = models.BooleanField(default=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    sequence = models.PositiveIntegerField(default=9999)
    jp2 = models.URLField(blank=True, null=True)
    thumbnail = models.URLField(blank=True, null=True)
    
    def __unicode__(self):
        return "%s (%s)" % (self.title, self.book.title)
    
    @property
    def annotations(self):
        if not self.internal:
            return []
        return list(Annotation.objects.raw("""
            SELECT
                *
            FROM
                bookreader_annotation
            WHERE
                bookreader_annotation.book_id = %s AND 
                bookreader_annotation.offset <= %s AND
                bookreader_annotation.offset+bookreader_annotation.length > %s
            ORDER BY
                bookreader_annotation.offset""",
            [self.book.pk, self.sequence, self.sequence]))
    
    @property
    def safe_title(self):
        if self.title:
            return self.title
        
        if self.sequence > 0:
            return 'Page #%d' % (self.sequence,)
        
        if self.jp2:
            return self.jp2
        
        return 'Page Missing'
        
    
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

class Annotation(models.Model):
    book = models.ForeignKey(Book, related_name='annotations')
    offset = models.PositiveIntegerField(blank=False)
    length = models.PositiveIntegerField(blank=False, default=1)
    structural = models.BooleanField(default=False, blank=False)
    text = models.TextField(blank=False)
    
    @property
    def children(self):
        if not self.structural:
            return None
        children = []
        current = None
        
        c = self.book.annotations.exclude(pk=self.pk)
        c = c.filter(structural=True,
                     offset__range=(self.offset, self.offset+self.length-1))
        c = c.order_by('offset','-length')
        
        for child in c:
            if current and child.offset <= current.end and child.end <= current.end:
                continue
            if child.end > self.end:
                continue
            
            current = child
            children.append(child)
        return children
    
    @property
    def end(self):
        return self.offset + self.length - 1
    
    def __unicode__(self):
        return self.text[:100]
    
    class Meta:
        ordering = ('book','offset','-length')
