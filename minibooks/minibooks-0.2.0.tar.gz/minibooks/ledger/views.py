# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# $Id$
# ----------------------------------------------------------------------------
#
#    Copyright (C) 2008 Caktus Consulting Group, LLC
#
#    This file is part of minibooks.
#
#    minibooks is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of 
#    the License, or (at your option) any later version.
#    
#    minibooks is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#    
#    You should have received a copy of the GNU Affero General Public License
#    along with minibooks.  If not, see <http://www.gnu.org/licenses/>.
#


import datetime

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    raise ImportError('minibooks was unable to import the dateutil library. Please confirm it is installed and available on your current Python path.')

from urllib import urlencode

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse, QueryDict
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson as json
from django.db.models import Q
from django.contrib.auth.models import User
from django.conf import settings

from caktus.django.decorators import render_with
from caktus.django.db.util import query_to_table
from caktus.django.db.util import search_path as model_search_path
from caktus.django.forms import AutoCompleterForm

from crm import models as crm
from crm import forms as crm_forms

from minibooks.ledger import models as ledger
from minibooks.ledger import forms as ledger_forms
from minibooks.ledger.report import generate_exchange_pdf, generate_project_report_pdf
from minibooks.ledger.communication import send_project_report_email, send_exchange_email
from minibooks.ledger.report import generate_exchange_pdf, generate_project_report_pdf
from minibooks.ledger.models import Exchange, Account


@login_required
@render_with('books/ledger/index.html')
def dashboard(request):
    # there are no permissions on this view, so all DB access
    # must filter by request.user
    exchanges = ledger.Exchange.objects.filter(
        business__contacts=request.user
    ).select_related('type', 'business')[:10]
    
    # soonest first
    upcoming_interactions = request.user.interactions.select_related(
        'cdr',
        'contacts',
        'project',
        'project__business',
    ).filter(completed=False).order_by('date')
    
    # most recent first
    recent_interactions = request.user.interactions.select_related(
        'cdr',
        'contacts',
        'project',
        'project__business',
    ).filter(completed=True)[:6]
    
    projects = request.user.contact_projects.order_by(
        'name',
    ).select_related('business')
    
    context = {
        'recent_exchanges': exchanges,
        'recent_interactions': recent_interactions,
        'upcoming_interactions': upcoming_interactions,
        'projects': projects,
    }
    
    return context


@permission_required('ledger.view_exchange')
@render_with('books/ledger/exchange/list.html')
def list_exchanges(request, exchange_type_slug=None):
    if exchange_type_slug:
        exchange_type = get_object_or_404(
            ledger.ExchangeType, 
            slug=exchange_type_slug,
        )
    else:
        exchange_type = None
    
    if exchange_type:
        exchanges = ledger.Exchange.objects.filter(type=exchange_type)
    else:
        exchanges = ledger.Exchange.objects
    
    searching = False
    form = ledger_forms.SearchForm(request.GET)
    if form.is_valid() and form.cleaned_data['search']:
        searching = True
        search = form.cleaned_data['search']
        exchanges = exchanges.filter(
            Q(business__name__icontains=search) |
            Q(memo__icontains=search) |
            Q(transactions__memo__icontains=search) |
            Q(transactions__project__name__icontains=search)
        ).distinct()
    
    if not searching and not exchange_type:
        sql = []
        exchanges_types = ledger.ExchangeType.objects.all()
        for t in exchanges_types:
            sql.append(
                "(SELECT id FROM ledger_exchange WHERE type_id=%s ORDER BY date DESC LIMIT 5)" % t.id
            )
        exchanges = exchanges.extra(
            where=['ledger_exchange.id IN (%s)' % " UNION ".join(sql)]
        )
    
    exchanges = exchanges.select_related(
        'business',
        'type',
    ).order_by('type', '-date', '-id',)
    
    context = {
        'form': form,
        'searching': searching,
        'exchange_type': exchange_type,
        'exchanges': exchanges,
    }
    return context


@permission_required('ledger.view_exchange')
def view_exchange_as_pdf(request, exchange_id):
    exchange = get_object_or_404(ledger.Exchange, id=exchange_id)
    pdf = generate_exchange_pdf(exchange)
    
    return HttpResponse(pdf, content_type='application/pdf')


@permission_required('ledger.email_exchange')
@transaction.commit_on_success
@render_with('books/ledger/exchange/email/exchange.html')
def new_exchange_email(request, exchange_id):
    try:
        exchange = Exchange.objects.select_related().get(pk=exchange_id)
    except Exchange.DoesNotExist:
        raise Http404
    
    project = exchange.get_project()
    
    if request.method == 'POST':
        form = ledger_forms.EmailForm(
            request.POST, 
            business=exchange.business, 
            project=project,
        )
        if form.is_valid():
            memo = form.cleaned_data['memo']
            recipient = form.cleaned_data['to']
            context = {
                "exchange": exchange,
                "memo": memo,
                "recipient": recipient,
            }
            recipients = [recipient.email,]
            attachment = generate_exchange_pdf(exchange)
            if project:
                subject = project.name + ' ' + exchange.type.label
            elif exchange.business:
                subject = exchange.business.name + ' ' + exchange.type.label
            else:
                subject = exchange.type.label
            subject += ' %s' % exchange.date
            
            if not send_exchange_email(
                exchange_type=exchange.type,
                recipients=recipients,
                subject=subject,
                context=context,
                attachment=attachment,
            ):
                request.notifications.add('Failed to send email')
                return HttpResponseRedirect(
                    reverse(
                        'view_business',
                        kwargs={'business_id': exchange.business.id},
                    )
                )
            
            # create and save interaction
            message = 'Successfully sent %s to %s (%s)' % (
                exchange.type.label,
                recipient.get_full_name(),
                recipient.email,
            )
            interaction = crm.Interaction.objects.create(
                date=datetime.datetime.now(),
                type='business',
                completed=True,
                memo='%s: %s' % (message, memo),
            )
            exchange.delivered = True
            exchange.save()
            
            # add projects contacts to contacts list
            if project:
                for contact in project.contacts.all():
                    interaction.contacts.add(contact)
            elif exchange.business:
                for contact in exchange.business.contacts.all():
                    interaction.contacts.add(contact)
            
            request.notifications.add(message)
            
            return HttpResponseRedirect(
                reverse(
                    'view_business',
                    kwargs={'business_id': exchange.business.id},
                )
            )
    else:
        form = ledger_forms.EmailForm(
            business=exchange.business, 
            project=project,
        )
    
    context = {
        'exchange': exchange,
        'form': form,
    }
    return context


@permission_required('crm.email_project_report')
@transaction.commit_on_success
@render_with('books/ledger/exchange/email/project_report.html')
def new_project_report_email(request, project):
    if request.method == 'POST':
        form = ledger_forms.EmailForm(request.POST, project=project)
        if form.is_valid():
            memo = form.cleaned_data['memo']
            recipient = form.cleaned_data['to']
            
            context = {
                "project": project,
                "memo": memo,
                "recipient": recipient,
            }
            recipients = [recipient.email,]
            attachment = generate_project_report_pdf(project)
            subject = "%s project report" % project.name
            
            if not send_project_report_email(
                recipients=recipients,
                context=context,
                attachment=attachment
            ):
                request.notifications.add('Failed to send email')
                return HttpResponseRedirect(
                    reverse(
                        'view_project',
                        kwargs={
                            'business_id': project.business.id,
                            'project_id': project.id,
                        },
                    )
                )
            
            message = 'Successfully sent Project Report to %s (%s)' % (
                recipient.get_full_name(),
                recipient.email,
            )
            interaction = crm.Interaction.objects.create(
                date=datetime.datetime.now(),
                type='business',
                completed=True,
                project=project,
                memo='%s: %s' % (message, memo),
            )
            # add projects contacts to contacts list
            for contact in interaction.project.contacts.all():
                interaction.contacts.add(contact)
            request.notifications.add(message)
            
            return HttpResponseRedirect(
                reverse(
                    'view_project',
                    kwargs={
                        'business_id': project.business.id,
                        'project_id': project.id,
                    },
                )
            )
    else:
        form = ledger_forms.EmailForm(project=project)
    
    context = {
        'project': project,
        'form': form,
    }
    return context


@permission_required('ledger.add_exchange')
@permission_required('ledger.change_exchange')
@transaction.commit_on_success
@render_with('books/ledger/exchange/create.html')
def create_edit_exchange(
    request,
    exchange_type_slug,
    business=None,
    project=None,
    exchange_id=None,
  ):
    exchange_type = get_object_or_404(
        ledger.ExchangeType, 
        slug=exchange_type_slug
    )
    exchange = None
    repeat_period = None
    
    if exchange_id:
        exchange = get_object_or_404(
            ledger.Exchange, 
            pk=exchange_id, 
            type=exchange_type,
        )
        repeat_period = exchange.repeat_period
    
    repeat_period_form = ledger_forms.RepeatPeriodForm(
        request,
        instance=repeat_period,
        prefix='repeat',
    )
    exchange_form = ledger_forms.ExchangeForm(
        request,
        instance=exchange,
        exchange_type=exchange_type,
    )
    
    if request.POST:
        transaction_formset = ledger_forms.TransactionFormSet(
            request.POST,
            # workaround for http://code.djangoproject.com/ticket/9462
            instance=exchange or ledger.Exchange(), 
            exchange_type=exchange_type,
        )
        
        if (request.POST
            and exchange_form.is_valid()
            and transaction_formset.is_valid()
            and repeat_period_form.is_valid()
          ):
            exchange = exchange_form.save(commit=False)
            exchange.repeat_period = repeat_period_form.save()
            exchange.save()
            
            def save_transaction(transaction):
                transaction.exchange = exchange
                debit_or_credit = exchange_type.debit_or_credit()
                setattr(
                    transaction,
                    debit_or_credit,
                    exchange_form.cleaned_data[debit_or_credit],
                )
                if project:
                    transaction.project = project
                else:
                    transaction.project = \
                        exchange_form.cleaned_data['project']
                transaction.save()
            
            transactions = transaction_formset.save(commit=False)
            for transaction in transactions:
                save_transaction(transaction)
                
            ids = [t.id for t in transactions]
            for transaction in exchange.transactions.exclude(id__in=ids):
                save_transaction(transaction)
                
            request.user.message_set.create(
                message='%s successfully saved.' % exchange_type,
            )
            return HttpResponseRedirect(
                reverse(
                    'list_exchanges_by_type',
                    kwargs={'exchange_type_slug': exchange.type.slug},
                )
            )
    else:
        transaction_formset = ledger_forms.TransactionFormSet(
            instance=exchange, 
            exchange_type=exchange_type,
        )

    context = {
        'exchange': exchange,
        'exchange_type': exchange_type,
        'exchange_form': exchange_form,
        'transaction_formset': transaction_formset,
        'repeat_period_form': repeat_period_form,
    }
    return context


@permission_required('ledger.change_exchange')
@transaction.commit_on_success
@render_with('books/ledger/exchange/edit_exchange_type.html')
def edit_exchange_type(request, exchange_type_slug, exchange_id):
    exchange_type = get_object_or_404(
      ledger.ExchangeType, 
      slug=exchange_type_slug,
    )
    exchange = get_object_or_404(
      ledger.Exchange, 
      pk=exchange_id, 
      type=exchange_type,
    )
    exchange_form = ledger_forms.ExchangeTypeForm(
        request,
        instance=exchange,
    )
    if request.POST and exchange_form.is_valid():
        exchange = exchange_form.save()
        request.notifications.add(
            'Successfully change exchange type from %s to %s' % (
                exchange_type,
                exchange.type,
            )
        )
        return HttpResponseRedirect(
            reverse('edit_exchange', kwargs={
                'exchange_id': exchange.id,
                'exchange_type_slug': exchange.type.slug,
            })
        )
    context = {
        'exchange': exchange,
        'exchange_form': exchange_form,
    }
    return context

@permission_required('ledger.delete_exchange')
@render_with('books/ledger/exchange/remove.html')
@transaction.commit_on_success
def remove_exchange(request, exchange_id):
    exchange = get_object_or_404(ledger.Exchange, pk=exchange_id)
    
    if request.POST and not exchange.reconciled:
        exchange.delete()
        return HttpResponseRedirect(reverse('list_exchanges'))
    
    context = {
        'reconciled': exchange.reconciled,
        'exchange': exchange,
    }
    return context


@permission_required('ledger.add_exchange')
@permission_required('ledger.change_exchange')
@transaction.commit_on_success
def duplicate_exchange(request, exchange_id):
    exchange = get_object_or_404(ledger.Exchange, pk=exchange_id)
    transactions = exchange.transactions.all()
    
    exchange.id = None
    exchange.memo = 'Copy of %s' % (exchange.memo)
    exchange.delivered = False
    exchange.save(force_insert=True)
    for transaction in transactions:
        transaction.id = None
        transaction.memo = 'Copy of %s' % (transaction.memo)
        transaction.exchange = exchange
        transaction.debit_reconciled = False
        transaction.credit_reconciled = False
        transaction.save(force_insert=True)
    
    if request.GET['next']:
        return HttpResponseRedirect(request.GET['next'])
    else:
        return HttpResponseRedirect(reverse('list_exchanges'))


### not a view
def date_filters(
    request,
    from_slug='from_date',
    to_slug='to_date',
    use_range=True,
  ):
    def construct_url(from_date, to_date):
        url = '%s?%s=%s' % (
            request.path,
            to_slug,
            to_date.strftime('%m/%d/%Y'),
        )
        if use_range:
            url += '&%s=%s' % (
                from_slug,
                from_date.strftime('%m/%d/%Y'),
            )
        return url
        
    filters = {}
    filters['Past 12 Months'] = []
    single_month = relativedelta(months=1)
    from_date = datetime.date.today().replace(day=1) + relativedelta(months=1)
    for x in range(12):
        to_date = from_date
        from_date = to_date - single_month
        url = construct_url(from_date, to_date - relativedelta(days=1))
        filters['Past 12 Months'].append((from_date.strftime("%b '%y"), url))
    filters['Past 12 Months'].reverse()
    
    filters['Years'] = []
    for year in ledger.Transaction.objects.dates('date', 'year'):
        from_date = year
        to_date = year + relativedelta(years=1)
        url = construct_url(from_date, to_date - relativedelta(days=1))
        filters['Years'].append((str(from_date.year), url))
    
    filters['Quaters (Calendar Year)'] = []
    to_date = datetime.date(datetime.date.today().year - 1, 1, 1)
    for x in range(8):
        from_date = to_date
        to_date = from_date + relativedelta(months=3)
        url = construct_url(from_date, to_date - relativedelta(days=1))
        filters['Quaters (Calendar Year)'].append(
            ('Q%s %s' % ((x % 4) + 1, from_date.year), url)
        )
    
    return filters


@permission_required('ledger.view_account')
@render_with('books/ledger/account/ledger.html')
def account_ledger(request, account_id=None):
    if account_id:
        accounts = [ get_object_or_404(ledger.Account, pk=account_id) ]
    else:
        if request.GET and 'accounts' in request.GET:
            accounts = ledger.Account.objects.filter(
                id__in=request.GET.getlist('accounts')
            )
        else:
            accounts = ledger.Account.objects.all()
    
    date_form = ledger_forms.DateForm(request, use_get=True)
    if request.GET and date_form.is_valid():
        from_date, to_date = date_form.save()
    else:
        from_date = None
        to_date = None
    
    context = {
        'accounts': accounts,
        'reconcile_enabled': bool(account_id),
        'filters': date_filters(request),
        'to_date': to_date,
        'from_date': from_date,
        'date_form': date_form,
    }
    return context


@permission_required('ledger.view_account')
@render_with('books/ledger/account/business_balance.html')
def account_business_balances(request, account_id):
    account = get_object_or_404(ledger.Account, pk=account_id)
    
    date_form = ledger_forms.SingleDateForm(request, use_get=True)
    if request.GET and date_form.is_valid():
        date = date_form.save()
    else:
        date = None
    
    def sum_by_business(debit=None, credit=None, to_date=None):
        args = []
        where = []
        
        if debit:
            where.append("t.debit_id = %s")
            args.append(debit.id)
        if credit:
            where.append("t.credit_id = %s")
            args.append(credit.id)
        if to_date:
            where.append("t.date <= %s")
            args.append(to_date)
            
        sql = """
    SELECT
        c.name,
        e.business_id,
        COALESCE(SUM(ROUND(amount * quantity, 2)), 0.0) 
    FROM ledger_transaction t
    JOIN ledger_exchange e ON (t.exchange_id = e.id)
    JOIN crm_contact c ON (c.id = e.business_id AND c.type = 'business')
    """
        if where:
            sql += " WHERE %s" % ' AND '.join(where)
            
        sql += " GROUP BY e.business_id, c.name ORDER BY c.name"
        
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute(sql, args)
        result = {}
        for name, id, total in cursor.fetchall():
            result[id] = (name, total)
        return result
    
    credit_totals = sum_by_business(credit=account, to_date=date)
    debit_totals = sum_by_business(debit=account, to_date=date)
    
    balances = []
    for id in set(credit_totals.keys() + debit_totals.keys()):
        credit_name, credit_total = credit_totals.get(id, ('', 0))
        debit_name, debit_total = debit_totals.get(id, ('', 0))
        if account.type in ('asset', 'expense', 'equity',):
            balance = debit_total - credit_total
        else:
            balance = credit_total - debit_total
        balances.append({
            'id': id,
            'name': credit_name or debit_name,
            'debit_total': debit_total,
            'credit_total': credit_total,
            'balance': balance,
        })
    
    context = {
        'account': account,
        'balances': balances,
        'filters': date_filters(request, to_slug='date', use_range=False),
        'to_date': date,
        'date_form': date_form,
    }
    return context


@permission_required('ledger.add_account')
@permission_required('ledger.change_account')
@transaction.commit_on_success
@render_with('books/ledger/account/create_edit.html')
def create_edit_account(request, account_id=None):
    if account_id:
        account = ledger.Account.objects.get(pk=account_id)
    else:
        account = None
    
    if request.POST:
        account_form = ledger_forms.AccountForm(request.POST, instance=account)
        if account_form.is_valid():
            account_form.save()
            return HttpResponseRedirect(reverse('list_accounts'))
        
    else:
        account_form = ledger_forms.AccountForm(instance=account)
    
    context = {
        'account': account,
        'account_form': account_form,
    }
    return context

@permission_required('ledger.delete_account')
@transaction.commit_on_success
@render_with('books/ledger/account/remove.html')
def remove_account(request, account_id):
    account = get_object_or_404(ledger.Account, pk=account_id)
    transaction_count = account.get_transactions().count()
    
    if transaction_count == 0 and request.POST:
        account.delete()
        return HttpResponseRedirect(reverse('list_accounts'))
    
    context = {
        'account': account,
        'transaction_count': transaction_count,
    }
    return context


@permission_required('ledger.view_account')
@render_with('books/ledger/account/list.html')
def list_accounts(request):
    context = {
        'accounts': ledger.Account.objects.all(),
    }
    return context


@permission_required('crm.view_project')
def project_report(request, project):
    ar = ledger.Account.objects.get(number=1200)
    credit_total = ar.credit_total_for_project(project.id)
    debit_total = ar.debit_total_for_project(project.id)
    credits = ar.credits.filter(project=project.id)
    debits = ar.debits.filter(project=project.id)
    client = project.business
    
    if not credit_total: credit_total = 0
    if not debit_total:   debit_total = 0
    outstanding_balance = debit_total - credit_total
    
    return render_to_response('books/report/report.html', locals())


@permission_required('crm.view_project')
def show_project_report(request, project):
    pdf = generate_project_report_pdf(project)
    
    return HttpResponse(pdf, content_type='application/pdf')


@permission_required('ledger.change_transaction')
def reconcile_transaction(request):
    value = False
    reconciled_balance = '0.0'
    errors = []
    
    if request.POST:
        form = ledger_forms.ReconcileTransactionForm(request.POST)
        if form.is_valid():
            try:
                transaction = form.cleaned_data['transaction']
                account = form.cleaned_data['account']
                value = not getattr(transaction, '%s_reconciled' % account)
                setattr(transaction, '%s_reconciled' % account, value)
                transaction.save()
                account_id = getattr(transaction, '%s_id' % account)
                account = ledger.Account.objects.get(pk=account_id)
                to_date = form.cleaned_data['to_date']
                reconciled_balance = \
                  '%.2f' % account.reconciled_balance(to_date=to_date)
            except Exception, e:
                errors.append('%s: %s' % (type(e).__name__, e.message))
        else:
            for k, v in form.errors.iteritems():
                errors.append('%s: %s' % (k, v))
    else:
        errors.append('Must use form POST to reconcile a transaction')
    
    if errors:
        errors = '</li><li>'.join(errors)
        errors = '<ul class="errorlist"><li>%s</li></ul>' % errors
    else:
        errors = ''
    
    response = {
        'reconciled': value,
        'reconciled_balance': reconciled_balance,
        'errors': errors,
    }
    return HttpResponse(json.dumps(response), mimetype="text/json")


@permission_required('ledger.transfer_funds')
def list_transfer_debit_accounts(request):
    results = []
    
    if 'credit_id' in request.GET:
        credit = ledger.Account.objects.get(id=request.GET['credit_id'])
        accounts = ledger.Account.objects.filter(type=credit.type)
        accounts = accounts.exclude(id=credit.id)
        for account in accounts:
            results.append({
                'value': account.id,
                'label': unicode(account),
            })
    
    return HttpResponse(json.dumps(results), mimetype="text/json")


@permission_required('ledger.transfer_funds')
@transaction.commit_on_success
@render_with('books/ledger/account/transfer.html')
def transfer_funds(request, transaction_id=None):
    if transaction_id:
        transaction = get_object_or_404(ledger.Transaction, id=transaction_id)
    else:
        transaction = None
    
    if request.POST:
        form = ledger_forms.TransferForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('list_accounts'))
    else:
        form = ledger_forms.TransferForm(instance=transaction)
    
    context = {
        'form': form,
    }
    return context


@permission_required('ledger.add_transaction')
@permission_required('ledger.change_transaction')
@transaction.commit_on_success
@render_with('books/ledger/account/general_entry.html')
def general_entry(request, transaction_id=None):
    transaction = None
    if transaction_id:
        transaction = get_object_or_404(
            ledger.Transaction,
            id=transaction_id,
            project__isnull=True,
            exchange__isnull=True,
        )
    form = ledger_forms.GeneralEntryForm(request, instance=transaction)
    if request.POST and form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('list_accounts'))
    context = {
        'form': form,
        'transaction': transaction,
    }
    return context


@permission_required('ledger.view_account_reports')
@render_with('books/ledger/reports/profit_loss.html')
def profit_loss(request):
    date_form = ledger_forms.DateForm(request, use_get=True)
    if request.GET and date_form.is_valid():
        from_date, to_date = date_form.save()
    else:
        from_date = None
        to_date = None
    
    total_profits = 0
    total_losses = 0
    profit_accounts = ledger.Account.objects.filter(
        type='income',
    ).order_by('name')
    loss_accounts = ledger.Account.objects.filter(
        type='expense',
    ).order_by('name')
    
    for account in profit_accounts:
        account.date_range_total = account.total_for_date_range(
            from_date=from_date,
            to_date=to_date,
        )
        total_profits += account.date_range_total
    
    for account in loss_accounts:
        account.date_range_total = account.total_for_date_range(
            from_date=from_date,
            to_date=to_date,
        )
        total_losses += account.date_range_total
    
    # for links to account pages
    date_query = {}
    if to_date:
        date_query['to_date'] = to_date.strftime('%m/%d/%Y')
    if from_date:
        date_query['from_date'] = from_date.strftime('%m/%d/%Y')
    date_query_string = urlencode(date_query)
    
    context = {
        'date_query_string': date_query_string,
        'date_form': date_form,
        'to_date': to_date,
        'filters': date_filters(request),
        'from_date': from_date,
        'profit_accounts': profit_accounts,
        'loss_accounts': loss_accounts,
        'total_profits': total_profits,
        'total_losses': total_losses,
        'net_income': total_profits - total_losses,
    }
    return context


@permission_required('ledger.view_account_reports')
@render_with('books/ledger/reports/balance_sheet.html')
def balance_sheet(request):
    date_form = ledger_forms.SingleDateForm(request, use_get=True)
    if request.GET and date_form.is_valid():
        date = date_form.save()
    else:
        date = None
    
    total_assets = 0
    total_liabilities = 0
    asset_accounts = ledger.Account.objects.filter(
        type='asset',
    ).order_by('name')
    liability_accounts = ledger.Account.objects.filter(
        type='liability',
    ).order_by('name')
    
    for account in asset_accounts:
        account.date_range_total = account.total_for_date_range(
            to_date=date,
        )
        total_assets += account.date_range_total
    
    for account in liability_accounts:
        account.date_range_total = account.total_for_date_range(
            to_date=date,
        )
        total_liabilities += account.date_range_total
    
    # for links to account pages
    date_query = {}
    if date:
        date_query['to_date'] = date.strftime('%m/%d/%Y')
    date_query_string = urlencode(date_query)
    
    context = {
        'date_query_string': date_query_string,
        'date_form': date_form,
        'filters': date_filters(request, to_slug='date', use_range=False),
        'date': date,
        'asset_accounts': asset_accounts,
        'liability_accounts': liability_accounts,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'owners_equity': total_assets - total_liabilities,
        'liabilities_and_owners_equity': total_assets,
    }
    return context


@permission_required('ledger.view_account_reports')
@render_with('books/ledger/reports/list.html')
def list_reports(request):
    today = datetime.date.today()
    dates = (
        ('This Month',
            {
                'from_date': today.replace(day=1),
                'to_date': today,
            }
        ),
        ('Last Month',
            {
                'from_date': today.replace(day=1) - relativedelta(months=1),
                'to_date': today.replace(day=1),
            }
        ),
        ('This Year',
            {
                'from_date': today.replace(day=1, month=1),
                'to_date': today,
            }
        ),
        ('Last Year',
            {
                'from_date': \
                    today.replace(day=1, month=1) - relativedelta(years=1),
                'to_date': today.replace(day=1, month=1),
            }
        ),
    )
    headers = []
    revenue = []
    expenses = []
    totals = []
    for label, date_range in dates:
        headers.append(label)
        income = ledger.Account.sum_by_type('income', **date_range)
        revenue.append(income)
        expense = ledger.Account.sum_by_type('expense', **date_range)
        expenses.append(expense)
        totals.append(income - expense)

    context = {
        'summary': {
            'headers': headers,
            'revenue': revenue,
            'expenses': expenses,
            'totals': totals,
        }
    }
    return context


@render_with('books/ledger/cron.html')
def cron(request):
    from minibooks.ledger.cron import create_recurring_exchanges
    messages = create_recurring_exchanges()
    
    if messages:
        email = EmailMessage(
            'minibooks cron messages', 
            '\n'.join(messages), 
            settings.DEFAULT_FROM_EMAIL, 
            ['%s <%s>' % (name, email) for name, email in settings.ADMINS],
        )
        email.send()
    else:
        messages.append('nothing done')
    
    if request.user.is_staff:
        context = {
            'messages': messages,
        }
    else:
        context = {}
    
    return context
