#
# Django models for Basket of currencies
#
from django.db import models
from django.core import exceptions

from ccy import currency, currencydb

def clean_ccys(value):
    value = value.replace(' ','')
    ccys = value.split(',')
    cd = {}
    for code in ccys:
        if not code:
            continue
        ccy = currency(code)
        if ccy:
            cd[ccy.code] = ccy
        else:
            raise exceptions.ValidationError("Currency %s not recognized" % code)

    if not cd:
        return ''
    else:
        return ','.join(cd.keys())  


class CurrenciesField(models.TextField):
    
    def to_python(self, value):
        cd = clean_ccys(value)
        if not cd and not self.blank:
            raise exceptions.ValidationError("No Currency specified")
        return cd
    

class BasketGroup(models.Model):
    code       = models.CharField(max_length = 64, unique = True)
    description = models.TextField(blank = True)
    
    def add(self, code, currencies, color = ''):
        b = Basket(code = code, currencies = currencies, group = self, color = color)
        b.save()
        return b
    
    def others(self):
        '''
        Return a list of currencies not included in the baskets group
        '''
        ccys = dict([(c,c) for c in currencydb()])
        for b in self.baskets.all():
            for c in b.ccys():
                ccys.pop(c)
        return ccys.keys()
            
    @property
    def num_baskets(self):
        return self.baskets.count()
    
    def nice_baskets(self):
        return ', '.join([b.code for b in self.baskets.all()])
    nice_baskets.short_description = 'baskets'


class Basket(models.Model):
    code       = models.CharField(max_length = 64)
    color      = models.CharField(max_length = 10, blank = True)
    currencies = CurrenciesField(blank = False)
    group      = models.ForeignKey(BasketGroup, related_name = 'baskets')
    
    class Meta:
        unique_together = ('code','group')
    
    def __unicode__(self):
        return self.code
    
    def save(self, **kwargs):
        self.currencies = clean_ccys(self.currencies)
        super(Basket,self).save(**kwargs)
        
    def ccys(self):
        '''
        List of currencies included in the basket
        '''
        return self.currencies.split(',')

