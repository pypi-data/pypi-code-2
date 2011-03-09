# Python
from datetime import datetime
from itertools import cycle, count
from uuid import uuid1
import calendar
# Django
from django.db.models import Avg
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
# Fudget
from time_spent.models import Income, Expense


@login_required
def details(request, month=0, year=0, template_name="time_spent/details.html"):
	user = request.user
	calendar_dt = today = datetime.today()

	if month and year:
		calendar_dt = datetime(day=1, month=int(month), year=int(year))

	calendar.setfirstweekday(calendar.SUNDAY)
	days_of_week = calendar.weekheader(10).split()
	month = calendar.Calendar(calendar.SUNDAY).monthdatescalendar(calendar_dt.year, calendar_dt.month)

	# session (expire 60 days)
	# request.session.set_expiry(60*60*24*60)
	# slug = request.session.get('slug', uuid1())
	# request.session['slug'] = slug


	expenses = Expense.objects.filter(creator=user).order_by('pk')

	try:
		income = Income.objects.get(creator=user)
	except:
		income = Income.objects.create(
			label = "",
			amount = 3000,
			creator = user,
		)

	num_workdays = len(work_days(calendar_dt.month, month))
	
	hourly_income = income.per_hour(num_workdays)
	daily_income = income.per_day(num_workdays)

	# budget_per_day = float(month_budget) / len(work_days(calendar_dt.month, month))
	# budget_per_hour = budget_per_day / 8.0

	color_list = [
		'#AB2F27', # red
		'#D08021', # orange
		'#D19919', # yelloworange
		'#EFC443', # yellow
		'#A7B929', # olive
		'#84BB3B', # lime
		'#57A336', # green
		'#45A388', # bluegreen
		'#4784A3', # teal
		'#668ADE', # blue
	]

	colors = cycle(color_list)
	counter = count(0)

	expense_list = []
	for i in range(10): expense_list.append({'pk':0, 'label':'', 'amount':0, 'color':colors.next(), 'hours':0, 'days':0})

	colors = cycle(color_list)

	for expense in expenses[:10]:

		expense_list[counter.next()] = {
			'pk': expense.pk,
			'label': expense.label,
			'amount': expense.amount,
			'color': colors.next(),
			'hours': float(expense.amount) / hourly_income,
			'days': float(expense.amount) / daily_income,
		}

	if request.method == "POST":
		expense_list = []

		income.amount = request.POST.get('income-amount', None)
		income.save()

		post_items = ['stock-item-pk','stock-item-label','stock-item-amount','stock-item-color']
		expense_tuples = zip(*[dict(request.POST)[item] for item in post_items])

		counter = count(0)

		for expense_tuple in expense_tuples:
			pk, label, amount, color = expense_tuple[:4]

			if amount: amount = float(amount)
			else: amount = 0

			if pk: pk = int(pk)
			else: pk = 0

			if pk or amount > 0:
				try:
					expense = Expense.objects.get(pk=pk)
				except:
					expense = Expense()

				expense.dt = calendar_dt
				expense.label = label
				expense.amount = str(amount)
				expense.creator = user
				expense.save()

				pk = expense.pk

			expense_list.append({
				"pk":pk, 
				"label":label, 
				"amount":amount, 
				"color":color,
				"hours": float(amount) / hourly_income,
				"days": float(amount) / daily_income, 
			})

	total_expense = get_total_expense(expenses)
	extra_money = float(income.amount) - float(total_expense)
	month_name = calendar.month_name[calendar_dt.month]

	budget_hours = get_budget_hours(income.amount)

	expense_hours = get_expense_hours(total_expense)

	days_in_month = calendar.mdays[calendar_dt.month]
	hours_in_month = days_in_month*8

	print 'work days', num_workdays
	print 'work hours', num_workdays*8
	print 'total expense', total_expense
	print 'expense in hours', total_expense/hourly_income

	print 'hours spent making money', (num_workdays*8) - (total_expense/hourly_income)
	print 'days spent making money', (num_workdays) - (total_expense/daily_income)
	
	print "expense hours", expense_hours

	net_hours = (num_workdays*8) - (total_expense/hourly_income)
	net_days = (num_workdays) - (total_expense/daily_income)

	extra_hours = float(budget_hours) - float(expense_hours)

	next_month_url = reverse('time-spent', args=next_month(calendar_dt.month, calendar_dt.year))
	prev_month_url = reverse('time-spent', args=prev_month(calendar_dt.month, calendar_dt.year))

	return render_to_response(
		template_name,
		{
			'calendar':calendar, 
			'days_of_week':days_of_week, # list
			'month':month, # list
			'today':today, # datetime
			'month_int':calendar_dt.month, 
			'year_int': calendar_dt.year, 
			'next_month_url': next_month_url, 
			'prev_month_url':prev_month_url, 
			'total_expense':total_expense,
			'hourly_income':hourly_income, 
			'daily_income':daily_income, 
			'month_name':month_name, 
			'stock_list':expense_list,
			'income':income, 
			'extra_money':extra_money,
			'num_work_hours':num_workdays*8,
			'num_work_days':num_workdays,
			'net_hours':net_hours,
			'net_days':net_days,
		}, 
		context_instance=RequestContext(request))

def get_budget_hours(budget):
	return float(budget) / 24

def get_expense_hours(expense):
	return float(expense) / 24

def get_total_expense(expenses):
	"""
	get_total_expense:
		Required: List of expense objects.
		Returns the total amount of expenses
		for this month.
	"""
	total_expense = 0
	for expense in expenses:
		total_expense += expense.amount

	return float(total_expense)

def next_month(month, year):
	"""
	next_month(month_int, year_int):
		Returns next month tuple.
		i.e. (next_month_int, next_year_int)
	"""
	next_month = (month+1)%13
	next_year = year
	if next_month == 0:
		next_month = 1
		next_year += 1
	return (next_month, next_year)

def prev_month(month, year):
	"""Returns previous month tuple"""
	prev_month = (month-1)%13
	prev_year = year
	if prev_month == 0:
		prev_month = 12
		prev_year -= 1
	return (prev_month, prev_year)

def work_days(month_int=None, month=None):
	"""List of workdays"""
	work_days = []
	for week in month:
		for day in week:
			if day.month == month_int and day.weekday() < calendar.SATURDAY:
				work_days.append(day)
	return work_days
