from django.db import models
from cstk.abstract_models import FloatValueDateSeriesModel



class Language( models.Model ):
    name = models.CharField( max_length=255 )
    native_name = models.CharField( max_length=255 )
    iso_639_1 = models.CharField( max_length=2, unique=True )
    iso_639_2t = models.CharField( max_length=3, unique=True )
    iso_639_2b = models.CharField( max_length=3, unique=True )
    iso_639_3 = models.CharField( max_length=10 )

    def __unicode__( self ):
        return self.name

    def save( self, *args, **kwargs ):
        self.iso_639_1 = self.iso_639_1.lower()
        self.iso_639_2b = self.iso_639_2b.lower()
        self.iso_639_2t = self.iso_639_2t.lower()
        self.iso_639_3 = self.iso_639_3.lower()

        super( Language, self ).save( *args, **kwargs )



class Country( models.Model ):
    name = models.CharField( max_length=255 )
    iso_3166_1_alpha2 = models.CharField( max_length=2, unique=True )
    iso_3166_1_alpha3 = models.CharField( max_length=3, unique=True )
    iso_3166_1_numeric = models.PositiveSmallIntegerField( unique=True )
    iso_3166_2 = models.CharField( max_length=2, unique=True )

    def __unicode__( self ):
        return self.name

    def save( self, *args, **kwargs ):
        self.iso_3166_1_alpha2 = self.iso_3166_1_alpha2.lower()
        self.iso_3166_1_alpha3 = self.iso_3166_1_alpha3.lower()
        self.iso_3166_2 = self.iso_3166_2.lower()
        super( Country, self ).save( *args, **kwargs )

    class Meta:
        verbose_name_plural = 'Countries'



class Locale( models.Model ):
    name = models.CharField( max_length=255 )
    language = models.ForeignKey( Language )
    country = models.ForeignKey( Country, blank=True, null=True )
    published_status = models.CharField( max_length=255, blank=True )
    publish_default = models.BooleanField()

    def __unicode__( self ):
        return self.name

    def save( self, *args, **kwargs ):
        if self.country is not None:
            self.name = u'%s_%s' % ( self.language.iso_639_1.lower(), self.country.iso_3166_1_alpha2.upper() )
        else:
            self.name = u'%s' % ( self.language.iso_639_1.lower() )

        if self.publish_default is True:
            try:
                old_default = Language.objects.get( publish_default=True )
                old_default.publish_default = False
                old_default.save()
            except:
                pass

        super( Locale, self ).save( *args, **kwargs )

    class Meta:
        unique_together = ( 
            ( 'country', 'language' ),
         )



class Currency( models.Model ):
    name = models.CharField( max_length=255 )
    iso_4217_alpha = models.CharField( max_length=3, unique=True )
    iso_4217_numeric = models.PositiveSmallIntegerField()

    def __unicode__( self ):
        return self.name

    class Meta:
        verbose_name_plural = 'Currencies'



class CurrencyDateSeries( FloatValueDateSeriesModel ):
    currency = models.ForeignKey( Currency )

    def __unicode__( self ):
        return self.value

    class Meta:
        verbose_name = 'Currency Value'
        verbose_name_plural = 'Currency Values'








