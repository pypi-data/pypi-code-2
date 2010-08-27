#encoding:utf-8
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from helmholtz.core.models import Cast
from helmholtz.units.fields import PhysicalQuantityField

def annotate(object, annotation):
    """Annotate a database object with text or with an uploaded file."""
    # this function takes care of determining whether object has an int
    # or char primary key, and of choosing the right subclass of Annotation
    # to use.
    raise NotImplementedError

class Annotation(Cast):
    """Base class of all classes needed to annotate an object."""
    label = models.CharField(max_length=256)

class IntegerAnnotation(Annotation):
    """Annotate an object having integer as primary key."""
    content_type = models.ForeignKey(ContentType, related_name="integer_annotations") 
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('content_type', 'object_id') 
    
    class Meta:
        verbose_name = 'document'

class IntegerText(IntegerAnnotation):
    """Annotate an object having integer as primary key with a text."""
    notes = models.TextField()
    
    class Meta :
        verbose_name = 'text annotation'
    
    def __unicode__(self):
        return self.notes

class IntegerDocument(IntegerAnnotation):
    """Annotate an object having integer as primary key with an electronic document."""
    image = models.FileField(upload_to="uploads/documents")
    
    class Meta :
        verbose_name = 'document annotation'
    
    def __unicode__(self):
        return self.image.__unicode__()

class CharAnnotation(Annotation):
    """Annotate an object having text as primary key."""
    content_type = models.ForeignKey(ContentType, related_name="char_annotations") 
    object_id = models.TextField()
    object = generic.GenericForeignKey('content_type', 'object_id') 
    
    class Meta:
        verbose_name = 'document'

class CharText(CharAnnotation):
    """Annotate an object having text as primary key with a text."""
    notes = models.TextField()
    
    class Meta :
        verbose_name = 'text annotation'
    
    def __unicode__(self):
        return self.notes

class CharDocument(CharAnnotation):
    """Annotate an object having text as primary key with an electronic document."""
    image = models.FileField(upload_to="uploads/documents")
    
    class Meta :
        verbose_name = 'document annotation'
    
    def __unicode__(self):
        return self.image.__unicode__()

class Descriptor(models.Model):
    """Extend properties of an object."""
    name = models.CharField(max_length=45)
    human_readable = models.TextField(null=True)
    
    def __unicode__(self):
        st = self.name
        if self.human_readable :
            st += " : %s" % self.human_readable
        return self.name

class StaticDescription(models.Model):
    """Associate a Descriptor with a value."""
    descriptor = models.ForeignKey(Descriptor)
    value = PhysicalQuantityField(unit='');
    notes = models.TextField(null=True, blank=True)

#improvements for future releases
#avoid the some class redundancies

class TextAnnotation(Annotation):
    """Text Annotation."""
    text = models.TextField()
    
    class Meta :
        verbose_name = 'text annotation'
    
    def __unicode__(self):
        return self.text

class DocumentAnnotation(Annotation):
    """Electronic document Annotation."""
    text = models.FileField(upload_to="uploads/documents")
    
    class Meta :
        verbose_name = 'document annotation'
    
    def __unicode__(self):
        return self.text

class IsAnnotated(Cast):
    """
    Link an Annotation to an object. The effective link is done via 
    IntegerObjectIsAnnotated and CharObjectIsAnnotated subclasses
    """
    annotation = models.ForeignKey(Annotation)

class IntegerObjectIsAnnotated(IsAnnotated):
    """Annotate an object having integer as primary key."""
    content_type = models.ForeignKey(ContentType, related_name="integer_object_is_annotated_by") 
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('content_type', 'object_id') 

class CharObjectIsAnnotated(IsAnnotated):
    """Annotate an object having text as primary key."""
    content_type = models.ForeignKey(ContentType, related_name="char_object_is_annotated_by") 
    object_id = models.TextField()
    object = generic.GenericForeignKey('content_type', 'object_id') 
