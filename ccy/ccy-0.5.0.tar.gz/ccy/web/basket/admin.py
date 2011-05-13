from django.contrib import admin
import models
from forms import BasketForm, BasketFormSet


class BasketInline(admin.TabularInline):
    model   = models.Basket
    form    = BasketForm
    formset = BasketFormSet
    extra   = 5

class BasketGroup(admin.ModelAdmin):
    list_display = ['code', 'num_baskets','nice_baskets']
    inlines = [BasketInline]
    save_on_top = True
    
admin.site.register(models.BasketGroup, BasketGroup)

