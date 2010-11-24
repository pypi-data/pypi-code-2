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
import re

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    raise ImportError('minibooks was unable to import the dateutil library. Please confirm it is installed and available on your current Python path.')

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.urlresolvers import reverse

from caktus.django.db.util import slugify_uniquely
from caktus.django.db.util import query_to_table

from crm import models as crm

from timepiece import models as timepiece

class AccountManager(models.Manager):
    def get_query_set(self):
        debit_total_sql = """
        SELECT COALESCE(SUM(ROUND(amount * quantity, 2)),0.0) 
        FROM ledger_transaction 
        WHERE debit_id = ledger_account.id
        """
        
        credit_total_sql = """
        SELECT COALESCE(SUM(ROUND(amount * quantity, 2)),0.0)
        FROM ledger_transaction
        WHERE credit_id = ledger_account.id
        """
        
    #    balance_sql = """
    #    COALESCE((%s) - (%s), 0.0)
    #    """ % (debit_total_sql, credit_total_sql)
        
        return super(AccountManager, self).get_query_set().extra(
            select={
                'debit_total': debit_total_sql,
                'credit_total': credit_total_sql,
    #            'balance': balance_sql,
            }
        )


class Account(models.Model):
    """
    Accounts for use in your business chart of accounts
    
    There will normally be far more expense accounts than any other type of account.
    
    The information which you collect in your income accounts will be used to prepare your profit and loss statements periodically.
    Profit and loss statement = income and expense statement
    
    phone - Telephone expenses
    google - Advertising expenses
    celito - 
    business meals and lodging
    business insurance
    charitable contributions
    auto expenses
    server expenses
    
    Asset and liability accounts are collectively referred to as balance sheet accounts
        Accounts receivable (current asset)
        Bank checking account (current asset)
        
        Accounts payable (current debt)
        Equipement (fixed asset)
    """
    
    ACCOUNT_TYPES = (
        ('income', 'Income' ),
        ('expense', 'Expense' ),
        ('asset','Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
    )
    
    name = models.CharField(max_length=255, unique=True)
    number = models.IntegerField(unique=True)
    type = models.CharField(max_length=15, choices=ACCOUNT_TYPES)
    
    objects = AccountManager()

    def balance(self):
        if self.type in ('asset', 'expense', 'equity',):
            return self.debit_total - self.credit_total
        else:
            return self.credit_total - self.debit_total
    
    def _difference(self, debit_amt, credit_amt):
        if self.type in ('asset', 'expense', 'equity',):
            return debit_amt - credit_amt
        else:
            return credit_amt - debit_amt
        
    def _total(self, type=None, reconciled=None, **kwargs):
        if type in ('credit', 'debit'):
            kwargs[type] = self
            if reconciled is not None:
                kwargs['%s_reconciled' % type] = reconciled
        else:
            raise Exception('Invalid type %s' % type)
        
        return Transaction.sum(**kwargs)
    
    def reconciled_balance(self, to_date=None):
        debit_total = self._total('debit', reconciled=True, to_date=to_date)
        credit_total = self._total('credit', reconciled=True, to_date=to_date)
        return self._difference(debit_total, credit_total)
    
    def debit_total_for_project(self, project_id=None):
        return self._total('debit', project_id=project_id)
        
    def credit_total_for_project(self, project_id=None):
        return self._total('credit', project_id=project_id)    
    
    def total_for_date_range(self, from_date=None, to_date=None):
        debit_total = self._total('debit', from_date=from_date, to_date=to_date)
        credit_total = self._total('credit', from_date=from_date, to_date=to_date)
        return self._difference(debit_total, credit_total)
    
    def get_transactions(self, from_date=None, to_date=None):
        if self.type in ('asset', 'expense', 'equity',):
            balance_order = ('debit', 'credit',)
        else:
            balance_order = ('credit', 'debit',)
        
        transactions = Transaction.objects.filter(
            Q(credit=self) | Q(debit=self)
        ).extra(
            select={
                'balance': 'ledger_account_balance.%s_balance - ledger_account_balance.%s_balance' % balance_order,
            },
            tables=[
            #    'running_balance(%s) ledger_account_balance' % self.id,
                 'ledger_account_balance',
            ],
            where=[
                'ledger_account_balance.account_id = %s',
                'ledger_account_balance.transaction_id = ledger_transaction.id',
            ],
            params=[
                self.id,
            ]
        # this order MUST match the order in ledger_account_ledger
        ).order_by(
            'date',
            'exchange__id',
            'id',
        ).select_related(
            'exchange__business', 
            'credit', 
            'debit', 
            'exchange', 
            'exchange__type',
        )
        
        if from_date:
            transactions = transactions.filter(date__gte=from_date)
            
        if to_date:
            transactions = transactions.filter(date__lte=to_date)
            
        return transactions
    
    def get_table(self, from_date=None, to_date=None):
        sql = "SELECT date, business, memo, debit, credit, total FROM ledger_account_ledger WHERE account = %s"
        args = [self.id,]
        
        if from_date:
            sql += " AND date >= %s"
            args.append(from_date)
            
        if to_date:
            sql += " AND date <= %s"
            args.append(to_date)
        
        return query_to_table(sql, args)
    
    @classmethod
    def profit_loss(cls, from_date=None, to_date=None):
        total_profits = 0
        total_losses = 0
        profit_accounts = cls.objects.filter(
            type='income',
        ).order_by('name')
        loss_accounts = cls.objects.filter(
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
        
        return {
            'profit_accounts': profit_accounts,
            'loss_accounts': loss_accounts,
            'total_profits': total_profits,
            'total_losses': total_losses,
            'net_income': total_profits - total_losses,
        }
    
    @classmethod
    def sum_by_type(cls, account_type, from_date, to_date):
        sql = ''
        if account_type in ('asset', 'expense', 'equity',):
            sql += 'SELECT SUM(debit_sum) - SUM(credit_sum) AS sum'
        else:
            sql += 'SELECT SUM(credit_sum) - SUM(debit_sum) AS sum'
        args = []
        args.append(from_date)
        args.append(to_date)
        args.append(from_date)
        args.append(to_date)
        args.append(account_type)
        sql += """
        FROM
            (
                SELECT
                    (SELECT COALESCE(SUM(ROUND(amount * quantity, 2)), 0.0)
                        FROM
                            ledger_transaction
                        WHERE
                            ledger_transaction.credit_id = ledger_account.id
                            AND ledger_transaction.date >= %s
                            AND ledger_transaction.date < %s
                    ) AS credit_sum,
                    (SELECT COALESCE(SUM(ROUND(amount * quantity, 2)), 0.0)
                        FROM
                            ledger_transaction
                        WHERE
                            ledger_transaction.debit_id = ledger_account.id
                            AND ledger_transaction.date >= %s
                            AND ledger_transaction.date < %s
                    ) AS debit_sum
                FROM
                    ledger_account
                WHERE
                    ledger_account.type = %s
            ) AS debit_and_credit_sum
        """
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute(sql, args)
        row = cursor.fetchone()
        return row[0]
        
    class Meta:
        ordering = ('type', 'name',)
        permissions = (
            ('view_account', 'Can view account'),
            ('view_account_reports', 'Can view account reports'),
            ('transfer_funds', 'Can transfer funds')
        )
        
    def __unicode__(self):
        return "%i - %s (%s)" % (self.number, self.name, self.type)


class ExchangeTypeManager(models.Manager):
    def get_query_set(self):
        return super(ExchangeTypeManager, self).get_query_set().extra(
            select={
                'exchange_count': 'SELECT COUNT(*) FROM ledger_exchange WHERE type_id = ledger_exchangetype.id',
            }
        )
    pass


class ExchangeType(models.Model):
    """
    Links exchanges to default accounts
    """
    
    label = models.CharField(max_length=100, unique=True)
    slug = models.CharField(max_length=100, unique=True)
    debit = models.ForeignKey(
        Account,
        null=True,
        blank=True,
        related_name='debit_exchange_types',
    )
    credit = models.ForeignKey(
        Account,
        null=True,
        blank=True,
        related_name='credit_exchange_types',
    )
    common_account = models.ForeignKey(
        Account,
        null=True,
        blank=True,
        related_name='common_account_exchange_types',
    )
    deliverable = models.BooleanField(default=False)
    
    business_types = models.ManyToManyField(
        crm.BusinessType,
        related_name='exchange_types',
    )
    
    objects = ExchangeTypeManager()
    
    class Meta:
        ordering = ('label',)
    
    def save(self, *args, **kwargs):
        queryset = ExchangeType.objects.all()
        if self.id:
            queryset = queryset.exclude(id__exact=self.id)
        self.slug = slugify_uniquely(self.label, queryset, 'slug')
        super(ExchangeType, self).save(*args, **kwargs)
    
    def debit_or_credit(self):
        if self.common_account:
            if self.debit is None:
                return 'debit'
            elif self.credit is None:
                return 'credit'
            else:
                raise ValueError('common_account must take the place of the debit or credit account in ExchangeType')
        return None

    def _get_credit_accounts(self, base_account):
        # TODO make this stuff part of the data model
        if base_account and self.slug == 'invoice':
            qs = Account.objects.filter(Q(type='income') | Q(type='expense'))
        elif base_account and self.slug == 'purchase':
            qs = Account.objects.filter(Q(type='liability') | Q(type='asset'))
        elif base_account:
            qs = Account.objects.filter(type=base_account.type)
        else:
            qs = Account.objects.none()
        return qs
    credit_accounts = property(
        lambda self: self._get_credit_accounts(self.credit)
    )

    def _get_debit_accounts(self, base_account):
        if base_account and self.slug == 'purchase-credit':
            qs = Account.objects.filter(Q(type='liability') | Q(type='asset'))
        elif base_account:
            qs = Account.objects.filter(type=base_account.type)
        else:
            qs = Account.objects.none()
        return qs
    debit_accounts = property(
        lambda self: self._get_debit_accounts(self.debit)
    )
    
    def _get_common_accounts(self):
        if self.debit:
            qs = self._get_credit_accounts(self.common_account)
        elif self.credit:
            qs = self._get_debit_accounts(self.common_account)
        else:
            qs = Account.objects.none()
        return qs
    common_accounts = property(_get_common_accounts)
    
    def __unicode__(self):
        return self.label


class ExchangeManager(models.Manager):
    def get_query_set(self):
        return super(ExchangeManager, self).get_query_set().extra(
            select={
                'total': 'SELECT SUM(ROUND(amount * quantity, 2)) FROM ledger_transaction WHERE exchange_id = ledger_exchange.id',
                'reconciled': 'SELECT bool_or(t.debit_reconciled OR t.credit_reconciled) FROM ledger_transaction t WHERE exchange_id = ledger_exchange.id',
            }
        )


class RepeatPeriod(models.Model):
    INTERVAL_CHOICES = (
        ('day', 'Day(s)'),
        ('week', 'Week(s)'),
        ('month', 'Month(s)'),
        ('year', 'Year(s)'),
    )
    active = models.BooleanField(default=False)
    count = models.PositiveSmallIntegerField(null=True, blank=True, choices=[(x,x) for x in range(1,32)])
    interval = models.CharField(null=True, blank=True, max_length=10, choices=INTERVAL_CHOICES)

    def delta(self):
        return relativedelta(**{str(self.interval + 's'): self.count})


class Exchange(models.Model):
    """ Collection of specific transactions """
    
    business = models.ForeignKey(crm.Contact, related_name="exchanges")
    type = models.ForeignKey(ExchangeType, related_name='exchanges')
    memo = models.TextField(null=True, blank=True)
    date = models.DateField()
    date_due = models.DateField(null=True, blank=True)
    delivered = models.BooleanField(default=False)
    
    repeat_period = models.ForeignKey(RepeatPeriod, null=True, blank=True, related_name='exchanges')
    
    objects = ExchangeManager()
    
    def previous_project_balance(self):
        if self.transactions.all().count() > 0:
            return self.transactions.all()[0].previous_project_balance()
        
    def new_project_balance(self):
        if self.type.slug == 'receipt':
            return self.previous_project_balance() - self.total
        elif self.type.slug == 'invoice':
            return self.previous_project_balance() + self.total
    
    def get_common_account(self):
        if self.transactions.all().count() > 0 and self.type.debit_or_credit():
            return getattr(self.transactions.all()[0], self.type.debit_or_credit())
        else:
            return None
        
    def get_project(self):
        if self.transactions.all().count() > 0:
            return self.transactions.all()[0].project
        else:
            return None
    
    def subtotal(self):
        return self.total
    
    @classmethod
    def get_user_payment_hours(cls):
        from trac_tickets.models import TracConnection
        projects = crm.Project.objects.order_by('name')
        try:
            trac = TracConnection()
    
            paycheck = ExchangeType.objects.get(label='Paycheck')
            now = datetime.datetime.now()
            tomorrow = now + datetime.timedelta(days=1)
            previous_pay_date_end = Exchange.objects.filter(type=paycheck)[0].date - datetime.timedelta(days=1)
            previous_pay_date_start = Exchange.objects.filter(type=paycheck,date__lt=previous_pay_date_end)[0].date - datetime.timedelta(days=1)
    
            curr_paychecks = trac.getUserTotalHours( projects, min_date=previous_pay_date_end, max_date=tomorrow, hash_prefix='curr_paychecks')
            prev_paychecks = trac.getUserTotalHours( projects, min_date=previous_pay_date_start, max_date=previous_pay_date_end, hash_prefix='prev_paychecks')
            paychecks = {}
            for key in curr_paychecks.keys():
                paychecks[key] = curr_paychecks[key]
                paychecks[key].update( prev_paychecks[key] )
    
        except Exception, e:
            raise

        return paychecks
        
    class Meta:
        ordering = ('-date', '-id', 'type',)
        permissions = (
            ('view_exchange', 'Can view exchange'),
            ('email_exchange', 'Can email exchange'),
        )

    def __unicode__(self):
        if self.id:
            return "%s: %s" % (self.type, self.memo)
        else:
            return unicode(self.memo)


class TransactionManager(models.Manager):
    def get_query_set(self):
        return super(TransactionManager, self).get_query_set().extra(
            select={
                'total': 'ROUND(amount * quantity, 2)'
            }
        )


class Transaction(models.Model):
    date = models.DateField()
    debit = models.ForeignKey(Account, related_name='debits')
    credit = models.ForeignKey(Account, related_name='credits')
    project = models.ForeignKey(timepiece.Project, null=True, related_name='transactions')
    exchange = models.ForeignKey(Exchange, null=True, related_name='transactions')
    
    memo = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    debit_reconciled = models.BooleanField()
    credit_reconciled = models.BooleanField()
    
    objects = TransactionManager()
    
    def previous_project_balance(self):
        billed = Transaction.sum(
            project_id=self.project.id,
            before=self,
            exchange_type=ExchangeType.objects.get(slug='invoice'),
        )
        paid = Transaction.sum(
            project_id=self.project.id,
            before=self,
            exchange_type=ExchangeType.objects.get(slug='receipt'),
        )
        return billed - paid
    
    def new_project_balance(self):
        return self.previous_project_balance() + self.total
    
    @classmethod
    def sum(cls, 
        debit=None, 
        credit=None, 
        project_id=None, 
        debit_reconciled=None, 
        credit_reconciled=None, 
        from_date=None, 
        to_date=None,
        before=None,
        exchange_type=None,
      ):
        args = []
        where = []
        join = []
        
        if debit:
            where.append("ledger_transaction.debit_id = %s")
            args.append(debit.id)
        if credit:
            where.append("ledger_transaction.credit_id = %s")
            args.append(credit.id)
        if project_id:
            where.append("ledger_transaction.project_id = %s")
            args.append(project_id)
        if from_date:
            where.append("ledger_transaction.date >= %s")
            args.append(from_date)
        if to_date:
            where.append("ledger_transaction.date <= %s")
            args.append(to_date)
        if debit_reconciled is not None:
            where.append("ledger_transaction.debit_reconciled = %s")
            args.append(debit_reconciled)
        if credit_reconciled is not None:
            where.append("ledger_transaction.credit_reconciled = %s")
            args.append(credit_reconciled)
        if before:
            where.append("""
            (ledger_exchange.date < %s OR 
            (ledger_exchange.date = %s AND ledger_exchange.id < %s) OR
            (ledger_exchange.date = %s AND ledger_exchange.id = %s AND ledger_transaction.date < %s) OR
            (ledger_exchange.date = %s AND ledger_exchange.id = %s AND ledger_transaction.date = %s AND ledger_transaction.id < %s))
            """)
            args.append(before.exchange.date)
            args.append(before.exchange.date)
            args.append(before.exchange.id)
            args.append(before.exchange.date)
            args.append(before.exchange.id)
            args.append(before.date)
            args.append(before.exchange.date)
            args.append(before.exchange.id)
            args.append(before.date)
            args.append(before.id)
        if exchange_type:
            join.append('JOIN ledger_exchange ON ledger_exchange.id = ledger_transaction.exchange_id')
            where.append('ledger_exchange.type_id = %s')
            args.append(exchange_type.id)
            
        sql = "SELECT COALESCE(SUM(ROUND(amount * quantity, 2)), 0.0) FROM ledger_transaction"
        if join:
            sql += ' ' + ' '.join(join)
        if where:
            sql += " WHERE %s" % ' AND '.join(where)
            
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute(sql, args)
        row = cursor.fetchone()
        return row[0]
    
    def reconciled(self):
        return (self.debit_reconciled or self.credit_reconciled)
    
    def __unicode__(self):
        return '%s: %s (%s)' % (self.date, self.memo, self.amount)
        
    class Meta:
        ordering = ('exchange__date', 'exchange__id', 'date', 'id',)


class ProjectManager(models.Manager):
    def get_query_set(self):
        invoice_sql = """
SELECT COALESCE(SUM(ROUND(amount * quantity, 2)), 0.0) 
FROM ledger_transaction t
INNER JOIN ledger_exchange e 
  ON (t.exchange_id=e.id) 
INNER JOIN ledger_exchangetype et 
  ON (e.type_id=et.id) 
WHERE t.project_id=crm_project.id
  AND et.slug='invoice'
        """
        receipt_sql = """
SELECT COALESCE(SUM(ROUND(amount * quantity, 2)), 0.0) 
FROM ledger_transaction t
INNER JOIN ledger_exchange e 
  ON (t.exchange_id=e.id) 
INNER JOIN ledger_exchangetype et 
  ON (e.type_id=et.id) 
WHERE t.project_id=crm_project.id
  AND et.slug='receipt'
        """
        return super(ProjectManager, self).get_query_set().extra(
            select={
                'balance': '(%s) - (%s)' % (invoice_sql, receipt_sql),
            }
        )
#crm.Project.objects = ProjectManager()


def install():
    group, created = Group.objects.get_or_create(name='Ledger Admin')
    if created:
        perms = Permission.objects.filter(
            content_type__in=ContentType.objects.filter(app_label='ledger')
        )
        for perm in perms:
            group.permissions.add(perm)
    
    if Account.objects.count() > 0 or ExchangeType.objects.count() > 0:
        return
    
    account_list = (
        (1060, 'Checking', 'asset'),
        (1200, 'Accounts Receivable', 'asset'),
        (1300, 'Owner Draws', 'asset'),
        (2100, 'Accounts Payable', 'liability'),
        (2200, 'Credit Card', 'liability'),
        (4020, 'Consulting', 'income'),
        (5020, 'General Expenses', 'expense'),
        (5615, 'Advertising & Promotions', 'expense'),
        (5620, 'Telephone', 'expense'),
        (5685, 'Insurance', 'expense'),
        (5695, 'Internet', 'expense'),
    )    
    
    exchange_type_list = (
        ('Invoice',  None, 4020, 1200),
        ('Receipt',  1060, None, 1200),
        ('Order',    5020, None, 2100),
        ('Payment',  None, 1060, 2100),
        ('Paycheck',  1060, None, 1300),
        ('Purchase', 5020, None, 1060),
        ('Purchase Credit', None, 5020, 2200),
        ('Credit Card Payment', None, 1060, 2200),
    )
    
    for number, name, type in account_list:
        Account(number=number, name=name, type=type).save()
    
    for label, debit, credit, common_account in exchange_type_list:
        tt = ExchangeType(label=label)
        if debit is not None:
            tt.debit = Account.objects.get(number=debit)
        if credit is not None:
            tt.credit = Account.objects.get(number=credit)
        if common_account is not None:
            tt.common_account = Account.objects.get(number=common_account)
        tt.save()
    
    if crm.BusinessType.objects.count() > 0:
        return
    
    business_types = (
        ('Vendor', 
            ('purchase', 'order', 'payment', 'purchase-credit',), 
            True,
        ),
        ('Client', 
            ('invoice', 'receipt',),
            False,
        ),
        ('Member', 
            ('paycheck',),
            False,
        ),
        ('Creditor', 
            ('credit-card-payment',),
            False,
        ),
    )
    
    for name, exchange_type_slugs, view_all_projects in business_types:
        bt = crm.BusinessType.objects.create(
            name=name,
            can_view_all_projects=view_all_projects
        )
        for slug in exchange_type_slugs:
            bt.exchange_types.add(ExchangeType.objects.get(slug=slug))
    
    print 'Accounts and Exchange Types successfully loaded'
    print
    print '--------------------------------------'
    print 'Install the minibooks SQL like so:'
    print '  createlang plpgsql minibooks'
    print '  ./manage.py dbshell < ledger/sql/minibooks.sql'
    print '--------------------------------------'
    print
