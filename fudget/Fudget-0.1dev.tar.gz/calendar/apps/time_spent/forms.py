from datetime import datetime
from django import forms
from time_spent.models import Stock

class StockForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = (
			'dt',
			'label',
			'cost',
			'slug',
		)