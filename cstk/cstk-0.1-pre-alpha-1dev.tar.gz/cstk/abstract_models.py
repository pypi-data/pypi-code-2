from django.db import models



class BasicDateSeriesModel( models.Model ):
    date = models.DateField()

    class Meta:
        abstract = True
        ordering = ['date', ]



class FloatValueDateSeriesModel( BasicDateSeriesModel ):
    value = models.FloatField()

    class Meta:
        abstract = True



#class IntegerValueDateSeriesModel( BasicDateSeriesModel ):
#    value = models.IntegerField()
#
#    class Meta:
#        abstract = True
#
#
#
#class PositiveIntegerValueDateSeriesModel( BasicDateSeriesModel ):
#    value = models.PositiveIntegerField()
#
#    class Meta:
#        abstract = True
#
#
#
#class PositiveSmallIntegerValueDateSeriesModel( BasicDateSeriesModel ):
#    value = models.PositiveSmallIntegerField()
#
#    class Meta:
#        abstract = True
#
#
#
#class SmallIntegerValueDateSeriesModel( BasicDateSeriesModel ):
#    value = models.SmallIntegerField()
#
#    class Meta:
#        abstract = True
#
#
#
#class TextValueDateSeriesModel( BasicDateSeriesModel ):
#    value = models.TextField()
#
#    class Meta:
#        abstract = True
