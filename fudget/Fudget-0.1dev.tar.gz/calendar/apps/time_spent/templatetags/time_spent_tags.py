import calendar
from datetime import datetime
from django import template

register = template.Library()

@register.inclusion_tag('time_spent/draw-stock.html')
def draw_stock(stock=[], month_int=None, month=None, month_budget=0):
	"""
	Inclusion Tag that draws the stock markup
	Parameter(s): stock_list
	"""

	budget = temp_budget = get_daily_budget(month_int, month, month_budget)
	expense_set = []

	while budget > 0 and stock:

		if stock[0]['amount'] > 0:

			budget = temp_budget - float(stock[0]['amount'])
			stock[0]['amount'] = float(stock[0]['amount']) - temp_budget
			temp_budget = budget

			if stock[0]['amount'] < 0:
				stock[0]['amount'] = 0
			
			expense_set.append(stock[0])
		else:
			if stock: stock.pop(0)

	return {"expense_set": expense_set}

def get_daily_budget(month_int, month, month_budget):
	return float(month_budget) / len(work_days(month_int, month))

def work_days(month_int=None, month=None):
	"""List of workdays"""
	work_days = []
	for week in month:
		for day in week:
			if day.month == month_int and day.weekday() < calendar.SATURDAY:
				work_days.append(day)
	return work_days

@register.filter
def today_class(day):
	"""
	If the day and today are equal then
	return a class name of "today."
	"""
	if day == datetime.today().date(): return "today"
	else: return ""






