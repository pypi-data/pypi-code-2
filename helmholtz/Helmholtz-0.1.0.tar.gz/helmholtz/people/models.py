#encoding:utf-8

#Here's some usecases :
# 1 - define a laboratory, its hierarchical organization, specificities and research axes
# 2 - store information useful to contact people or their relative laboratory to ask more explanations concerning experiments 
# 3 - set the list of people that have been hired by a laboratory and that have collaborated on experiments
# 4 - track in time someone's position
# 5 - define more accurately the profile of a user

from django.db import models
from django.db.models import Count
from django.contrib.contenttypes import generic
from django.contrib.auth.models import Group, User
from helmholtz.core.models import Cast, HierarchicalStructure
from helmholtz.core.shortcuts import get_subclasses
from helmholtz.people.fields import PhoneNumberField
from helmholtz.access_control.models import IntegerPermission

class Contact(Cast):
    """Base class of all type of contacts like Address, Phone, Fax, E-mail or Website."""
    label = models.CharField(max_length=100)
    permissions = generic.GenericRelation(IntegerPermission, content_type_field='content_type', object_id_field='object_id')
    
    def __unicode__(self):
        return self.label
    
    def cast_keys(self):
        keys = [k.__name__.lower() for k in get_subclasses(self.__class__)]
        return keys
    
    class Meta :
        ordering = ['label']

class Address(Contact):
    """Address used into Contact."""
    street_address_1 = models.CharField(max_length=256, verbose_name="address 1")
    street_address_2 = models.CharField(max_length=256, null=True, blank=True, verbose_name="address 2")
    postal_code = models.CharField(max_length=10)
    town = models.CharField(max_length=256)
    state = models.CharField(max_length=256, null=True, blank=True)
    country = models.CharField(max_length=256)
    
    def __unicode__(self):
        st = "%s : %s " % (self.label, self.street_address_1)
        if self.street_address_2 :
            st += "%s " % (self.street_address_2)
        st += "%s %s %s" % (self.postal_code, self.town, self.country)
        if self.state :
            st += " (%s)" % self.state
        return st  
    
    class Meta:
        ordering = ['label']
        verbose_name_plural = "addresses"

class EMail(Contact):
    """docstring needed"""
    identifier = models.EmailField(verbose_name="address", max_length=256)
    
    def __unicode__(self):
        st = "%s : %s" % (self.label, self.identifier)
        return st
    
    class Meta:
        verbose_name = "e-mail"

class Phone(Contact):
    """docstring needed"""
    identifier = PhoneNumberField(verbose_name="number", max_length=16)
    
    def __unicode__(self):
        st = "%s : %s" % (self.label, self.identifier)
        return st

class Fax(Contact):
    """docstring needed"""
    identifier = PhoneNumberField(verbose_name="number", max_length=16)
    
    def __unicode__(self):
        st = "%s : %s" % (self.label, self.identifier)
        return st
    
    class Meta:
        verbose_name_plural = "faxes"

class WebSite(Contact):
    """docstring needed"""
    identifier = models.URLField(verbose_name="url", verify_exists=False)
    
    def __unicode__(self):
        st = "%s : %s" % (self.label, self.identifier)
        return st
    
    class Meta:
        verbose_name = "website"

class ScientificStructure(HierarchicalStructure):
    """Hierarchical structure representing a large variety of scientific structures.
    
    NB : The db_group parameter specifies the group relative to a scientific structure. 
    Consequently, it is possible to implement a hierarchical user administration.
     
    """
    diminutive = models.CharField(max_length=32) # should be called "shortname" or something. Not all structures have acronyms
    name = models.CharField(max_length=256)
    logo = models.ImageField(upload_to="uploads/images/logos", null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    is_data_provider = models.BooleanField(default=False, null=False, blank=False)
    foundation_date = models.DateField(null=True, blank=True)
    dissolution_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    contacts = models.ManyToManyField(Contact, null=True, blank=True)
    db_group = models.OneToOneField(Group, verbose_name="database group", null=True, blank=True)
    permissions = generic.GenericRelation(IntegerPermission, content_type_field='content_type', object_id_field='object_id')
    
    class Meta :
        ordering = ['diminutive']
    
    def __unicode__(self, separator=u" \u2192 "):
        complete_path = self.diminutive or self.name
        if self.parent:
            complete_path = u"%s%s%s" % (self.parent.__unicode__(separator=separator), separator, complete_path)
        return complete_path
    
    def __shortname__(self):
        """docstring needed"""
        if self.diminutive :
            return self.diminutive
        else :
            return self.name
    shortname = property(__shortname__)
    
    def create_diminutive(self, separator="_"):
        """docstring needed"""
        if not self.diminutive:
            self.diminutive = self.name.replace(" ", separator)
    
    def number_of_researchers(self):
        """Get the number of Researchers working in a ScientificStructure."""
        aggregate = self.position_set.all().aggregate(Count("researcher", distinct=True))
        count = aggregate["researcher__count"]
        if self.scientificstructure_set.count :
            for children in self.get_children(recursive=False) :
                count += children.number_of_researchers()
        return count
    
    def get_parents(self):
        """docstring needed"""
        return self.parents('parent')
        
    def get_root(self):
        """docstring needed"""
        return self.root('parent')
    
    def get_children(self, recursive=False):
        """docstring needed"""
        return self.children('scientificstructure_set', recursive=recursive)
    
    def get_groups(self, recursive=False):
        """Return groups corresponding to the ScientificStructure and its children."""
        groups = list()
        groups.append(self.db_group.name)
        if recursive :
            groups = [k.db_group.name for k in self.get_children(recursive)]
        return Group.objects.filter(name__in=groups)

class Researcher(models.Model):
    """Anybody working in a ScientificStructure."""
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    photo = models.ImageField(upload_to="uploads/images/photos", null=True, blank=True)
    db_user = models.OneToOneField(User, related_name="profile", null=True, blank=True)#duplication because an employee isn't necessary a database user
    contacts = models.ManyToManyField(Contact, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    def get_full_name(self):
        """Get the full name of a Researcher, i.e. the combination between its first and last names."""
        return "%s %s" % (self.first_name, self.last_name)
    
    def last_position(self):
        """Get the last effective position of a Researcher in a ScientificStructure."""
        if self.position_set.count():
            return self.position_set.latest("start")
        else:
            return None
    
    def number_of_structures(self):
        """Get the number of ScientificStructures where a Researcher has worked."""
        aggregate = self.position_set.all().aggregate(Count("structure", distinct=True))
        return aggregate["structure__count"]
    
    def __unicode__(self):
        return self.get_full_name()
    
    class Meta:
        ordering = ['last_name', 'first_name']

class PositionType(models.Model):
    """Type of 'contract' useful to define someone's position."""
    name = models.CharField(primary_key=True, max_length=32)
    
    def __unicode__(self):
        return u"%s" % (self.name)
    
    class Meta:
        ordering = ['name']

class Position(models.Model):
    """Contract linking a Researcher to a ScientificStructure.
    
    NB : this class brings more flexibility by separating people 
    descriptions from their positions in a hierarchical structure.
    """
    researcher = models.ForeignKey(Researcher)
    structure = models.ForeignKey(ScientificStructure)
    position_type = models.ForeignKey(PositionType)
    start = models.DateField()
    end = models.DateField(null=True)
    notes = models.TextField(null=True, blank=True) 
    
    def __unicode__(self):
        end = self.end or "present"
        st = u"%s, %s in %s from %s to %s" % (self.researcher, self.position_type, self.structure, self.start, end)
        return st
    
    class Meta:
        ordering = ['start', 'structure', 'researcher']

class Supplier(models.Model):
    """docstring needed"""
    name = models.CharField(max_length=32, primary_key=True)
    contacts = models.ManyToManyField(Contact, null=True, blank=True) 
    
    def __unicode__(self):
        return self.name
    shortname = property(__unicode__)
    
    class Meta:
        ordering = ['name']
