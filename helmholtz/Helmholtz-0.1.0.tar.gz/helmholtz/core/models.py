#encoding:utf-8
from django.db import models
from django.utils.datastructures import SortedDict

class CastQuerySet(models.query.QuerySet):
    
    def cast(self, entity):
        """Return a QuerySet containing all objects of the same specified subclass."""
        subclasses = self.model.get_subclasses_recursively()
        if isinstance(entity, str) :
            names = [k.__name__ for k in subclasses]
            index = names.index(entity)
        else :
            index = subclasses.index(entity)
        selection = subclasses[index]
        lookup = selection.subclass_lookup()
        dct = {'%s__isnull' % lookup:False}
        pks = [k.id for k in self.filter(**dct).distinct()]
        objects = selection.objects.filter(pk__in=pks)
        return objects
    
class CastManager(models.Manager):
    """docstring needed"""
    
    def get_query_set(self):
        return CastQuerySet(self.model, using=self._db)
    
    def cast(self, entity):
        """Return a QuerySet containing all objects of the same specified subclass."""
        return self.get_query_set().cast(entity)

class Cast(models.Model):
    """docstring needed"""
    
    objects = CastManager()
    
    def sub_classes(self):
        return [k.__name__.lower() for k in self.__subclasses__()]
    
    @classmethod
    def get_subclasses(cls, proxies=False):
        """Get subclasses of a class."""
        if proxies :
            return cls.__subclasses__()
        else :
            return [k for k in cls.__subclasses__() if (k._meta.proxy == False)]
    
    @classmethod
    def get_subclasses_recursively(cls, strict=True, proxies=False):
        """Get recursively subclasses of a class."""
        subclasses = list()
        for subclass in cls.get_subclasses(proxies) :
            subclasses.append(subclass)
            subclasses.extend(subclass.get_subclasses_recursively(proxies=proxies))
        if not strict :
            subclasses.insert(0, cls)    
        return subclasses
    
    @classmethod
    def get_parents_recursively(cls):
        """Get the superclasses chain of a class."""
        result = list()
        for parent in cls._meta.parents :
            result.append(parent)
            result.extend(parent.get_parents_recursively())
        return result
    
    @classmethod
    def get_base_class(cls):
        """Get the base superclass of a class."""
        parents = cls.get_parents_recursively() 
        return parents[-1]
    
    @classmethod
    def subclass_lookup(cls):
        chain = cls.get_parents_recursively()[0:-1]
        chain.reverse()
        chain.append(cls)
        lookup = '__'.join([k.__name__.lower() for k in chain])
        return lookup
    
    def cast(self):
        """Cast an object to its actual class."""
        subclass_obj = self
        subclasses = self.__class__.get_subclasses()
        for subclass in subclasses :
            try :
                subclass_obj = getattr(self, subclass.__name__.lower())
            except :
                continue
            else :
                subclass_obj = subclass_obj.cast()
        return subclass_obj
    
    @property
    def get_type(self):
        return self.cast()._meta.verbose_name
    
    @classmethod
    def subclasses_dict(cls, proxies=False):
        """Return a dictionary linking a subclass name to the actual Python subclass."""
        classes = SortedDict()
        for subclass in cls.get_subclasses(proxies) :
            classes[subclass.__name__.lower()] = subclass
        return classes
    
    class Meta :
        abstract = True

class HierarchicalStructure(models.Model):
    """
    A convenient class to manage classes corresponding to hierarchical structures, 
    i.e. classes that have a ForeignKey pointing to itself.
    """
    
    def parents(self, field):
        """Get the parent chain."""
        result = list()
        parent = getattr(self, field)
        if parent :
            result.append(parent)
            result.extend(parent.parents(field))
        return result
            
    def root(self, field):
        """Get the root node of the hierarchy."""
        root = self
        parent = getattr(root, field)
        while parent :
            root = parent
            parent = getattr(root, field)
        return root 
    
    def children(self, field, children=None, recursive=False, starting_point=True, as_queryset=False):
        """Get recursively all children of a node."""
        if starting_point :
            children = list()
        manager = getattr(self, field)
        new_children = [k for k in manager.all()]
        for child in new_children :
            if not (child in children) :
                children.append(child)
            if recursive : 
                child.children(field, children, recursive, False)
        if starting_point :
            if not as_queryset :
                return children
            else :
                pks = [k.pk for k in children]
                queryset = self.__class__.objects.filter(pk__in=pks)
                return queryset
    
    class Meta :
        abstract = True