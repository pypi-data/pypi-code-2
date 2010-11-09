from django.db.utils import IntegrityError
from django.test import TestCase
from datetime import date
from datetime import timedelta
from random import uniform

from models import Country
from models import Currency
from models import CurrencyDateSeries
from models import Language
from models import Locale


class LocalisationTestCase( TestCase ):
    def test_language_model( self ):
        language = Language()
        language.name = 'English'
        language.native_name = 'English'
        language.iso_639_1 = 'en'
        language.iso_639_2b = 'eng'
        language.iso_639_2t = 'eng'
        language.iso_639_3 = 'eng'
        self.assertRaises( IntegrityError, language.save )

        language = None
        self.assertEquals( language, None )

        language = Language.objects.get( iso_639_1='en' )
        self.assertEquals( language.name, 'English' )


    def test_country_model( self ):
        country = Country()
        country.name = 'United Kingdom'
        country.iso_3166_1_alpha2 = 'gb'
        country.iso_3166_1_alpha3 = 'gbr'
        country.iso_3166_1_numeric = 826
        country.iso_3166_2 = 'gb'
        self.assertRaises( IntegrityError, country.save )

        country = None
        self.assertEquals( country, None )

        country = Country.objects.get( iso_3166_1_alpha2='gb' )
        self.assertEquals( country.name, 'United Kingdom' )


    def test_currency_model( self ):
        currency = Currency()
        currency.name = 'Pound sterling'
        currency.iso_4217_alpha = 'gbp'
        currency.iso_4217_numeric = 826
        self.assertRaises( IntegrityError, currency.save )

        currency = None
        self.assertEquals( currency, None )

        currency = Currency.objects.get( iso_4217_alpha='gbp' )
        self.assertEquals( currency.name, 'Pound sterling' )


    def test_currency_history_model( self ):
        currency = Currency.objects.get( iso_4217_alpha='gbp' )
        today = date.today()
        yesterday = date.today() - timedelta( days=1 )
        currency_date_series = CurrencyDateSeries()
        currency_date_series.currency = currency
        currency_date_series.date = today
        currency_date_series.value = uniform( 0.0, 1000.0 )
        currency_date_series.save()

        currency_date_series = None
        self.assertEquals( currency_date_series, None )

        currency_date_series = CurrencyDateSeries()
        currency_date_series.currency = currency
        currency_date_series.date = today
        currency_date_series.value = uniform( 0.0, 1000.0 )
        self.assertRaises( IntegrityError, currency_date_series.save )

        currency_date_series = None
        self.assertEquals( currency_date_series, None )

        currency_date_series = CurrencyDateSeries()
        currency_date_series.currency = currency
        currency_date_series.date = yesterday
        currency_date_series.value = uniform( 0.0, 1000.0 )
        currency_date_series.save()



    def test_locale_model( self ):
        country = Country.objects.get( iso_3166_1_alpha2='gb' )
        language = Language.objects.get( iso_639_1='en' )
        locale = Locale()
        locale.country = country
        locale.language = language
        self.assertRaises( IntegrityError, locale.save )

        locale = None
        self.assertEquals( locale, None )

        locale = Locale.objects.get( country=country, language=language )
        self.assertEquals( locale.name, 'en_GB' )



