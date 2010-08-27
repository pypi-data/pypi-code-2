#encoding:utf-8

#######################################################################################################
#Classes useful for tracking kinds of substances stored in a laboratory and used during an experiment #
#######################################################################################################

from django.db import models
from helmholtz.core.shortcuts import cast_object_to_leaf_class
from helmholtz.units.fields import PhysicalQuantityField
from helmholtz.people.models import Supplier

class Substance(models.Model):
    """Substance used during Experiment."""
    name = models.CharField(primary_key=True, max_length=32)
    
    def __unicode__(self):
        return u"%s" % (self.name)
    shortname = property(__unicode__)
    
    class Meta:
        ordering = ['name']

class Product(models.Model):
    """Product delivered by a Supplier."""
    catalog_ref = models.CharField(max_length=50, null=True, blank=True)#maybe CAS reference should be more useful than the supplier ? 
    name = models.CharField(max_length=256)
    substance = models.ForeignKey(Substance, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta : 
        unique_together = (("name", "supplier"),)


class Solution(models.Model):
    """Solution used in the following cases : drug applications, hollow electrodes and in vitro slices."""
    label = models.CharField(primary_key=True, max_length=256)

    def __unicode__(self):
        return self.label
    
    def perfusions(self):
        """
        Returns a :class:`QuerySet` containing all the
        :class:`helmholtz.drug_applications.Perfusion` items that used this solution.
        """
        applications = self.drugapplication_set.all()
        pks = [k.pk for k in applications if cast_object_to_leaf_class(k).__class__.__name__ == 'Perfusion']
        return applications.filter(pk__in=pks)
    
    def injections(self):
        """
        Returns a :class:`QuerySet` containing all the
        :class:`helmholtz.drug_applications.Injection` items that used this solution.
        """
        applications = self.drugapplication_set.all()
        pks = [k.pk for k in applications if cast_object_to_leaf_class(k).__class__.__name__ == 'Injection']
        return applications.filter(pk__in=pks)
    
    def hollow_electrodes(self):
        """
        Returns a :class:`QuerySet` containing all the
        :class:`helmholtz.electrophysiology.HollowElectrode` items that used this solution.
        """
        electrode = self.hollowelectrode_set.all()
        pks = [k.pk for k in electrode if cast_object_to_leaf_class(k).__class__.__name__ == 'HollowElectrode']
        return electrode.filter(pk__in=pks)
    
    def in_vitro_slices(self):
        """
        Returns a :class:`QuerySet` containing all the
        :class:`helmholtz.preparations.InVitroSlice` preparations that used this
        as the solution.
        """
        slices = self.preparation_set.all()
        pks = [k.pk for k in slices if cast_object_to_leaf_class(k).__class__.__name__ == 'InVitroSlice']
        return slices.filter(pk__in=pks)
    
    def list_components(self):
        """
        Returns a list of names of the chemical components of this solution and
        their concentrations.
        """
        return ["%s %s" % (s.concentration, s.chemical_product.name) for s in self.quantityofsubstance_set.all()]


class QuantityOfSubstance(models.Model):
    """Store the actual composition of a solution."""
    solution = models.ForeignKey(Solution)
    chemical_product = models.ForeignKey(Product)
    concentration = PhysicalQuantityField(unit='mol/L')
    
    def __unicode__(self):
        return "%s %s" % (self.chemical_product, self.concentration)
