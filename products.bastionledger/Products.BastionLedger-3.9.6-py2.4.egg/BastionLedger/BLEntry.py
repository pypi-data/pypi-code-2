#
#    Copyright (C) 2002-2010  Corporation of Balclutha. All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#    GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#    OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import Globals, logging, types, sys, traceback, string
from Acquisition import aq_base
from DateTime import DateTime
from Acquisition import aq_base
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionBanking.Exceptions import UnsupportedCurrency
from utils import floor_date, assert_currency
from BLBase import BSimpleItem
from BLTransaction import BLTransaction
from AccessControl.Permissions import view, view_management_screens, manage_properties, \
     access_contents_information
from Permissions import OperateBastionLedgers, ManageBastionLedgers
from Exceptions import PostingError, AlreadyPostedError

from zope.interface import Interface, implements

LOG = logging.getLogger('BLEntry')

def _addEntry(self, klass, account, amount, title='', id=None):
    """
    helper to add an entry - with lots of validation checking
    """
    #
    # self is an App.FactoryDispatcher instance if called via product factory - (whoooeee....)
    # but if we're called directly, then the _d attribute won't be set ...
    #
    realself = self.this()
    assert isinstance(realself, BLTransaction), \
           'Woa - accounts are ONLY manipulated via transactions!'

    # hmmm - an empty status is because workflow tool hasn't yet got to it ...
    assert realself.status() in ('', 'incomplete', 'complete'), \
           'Woa - invalid txn state (%s)' % (str(realself))

    if not title:
        title = realself.title

    try:
        assert_currency(amount)
    except:
        try:
            amount = ZCurrency(amount)
        except:
            raise ValueError, "Not a valid amount: %s" % amount

    if amount == 0:
        raise ValueError,"Please post an amount"

    #
    # self is an App.FactoryDispatcher instance if called via product factory - (whoooeee....)
    # but if we're called directly, then the _d attribute won't be set ...
    #
    if not id:
        id = realself.generateId()
        
    if type(account) == types.StringType:
        account = getattr(self.Ledger, account)

    account_url = '%s/%s' % (account.blLedger().getId(), account.getId())

    entry = klass(id, title, account_url, amount)
    realself._setObject(id, entry)
    
    return id

manage_addBLEntryForm = PageTemplateFile('zpt/add_entry', globals()) 
def manage_addBLEntry(self, account, amount, title='', id=None, REQUEST=None):
    """
    Add an entry - to a transaction ...
    """
    #
    # self is an App.FactoryDispatcher instance if called via product factory - (whoooeee....)
    # but if we're called directly, then the _d attribute won't be set ...
    #
    realself = self.this()
    assert isinstance(realself, BLTransaction), \
           'Woa - accounts are ONLY manipulated via transactions!'

    # hmmm - an empty status is because workflow tool hasn't yet got to it ...
    assert realself.status() in ('', 'incomplete', 'complete'), \
           'Woa - invalid txn state (%s)' % (str(realself))

    if not title:
        title = realself.title

    try:
        assert_currency(amount)
    except:
        try:
            amount = ZCurrency(amount)
        except:
            message = "Not a valid amount: %s" % amount
            if REQUEST is not None:
                REQUEST.set('manage_tabs_message', message)
                return realself.manage_main(realself, REQUEST)
            raise ValueError, message

    if amount == 0:
        message = "Please post an amount"
        if REQUEST is not None:
            if REQUEST is not None:
                REQUEST.set('manage_tabs_message', message)
                return realself.manage_main(realself, REQUEST)
        raise ValueError, message

    #
    # self is an App.FactoryDispatcher instance if called via product factory - (whoooeee....)
    # but if we're called directly, then the _d attribute won't be set ...
    #
    if not id:
        id = realself.generateId()
        
    if type(account) == types.StringType:
        account = getattr(self.Ledger, account)

    account_url = '%s/%s' % (account.blLedger().getId(), account.getId())

    entry = BLEntry(id, title, account_url, amount)
    realself._setObject(id, entry)
    
    if REQUEST is not None:
       return self.manage_main(self, REQUEST)

    # return the entry in context
    return id
    #return realself._getOb(id)

class IEntry(Interface): pass


class BLEntry( PropertyManager, BSimpleItem ):
    """
    An account/transaction entry

    Once the transaction has been posted, the entry has a date attribute
    Also, if there was any fx required, it will have an fx_rate attribute - from which the
    original currency trade may be derived ??
    """
    meta_type = portal_type = 'BLEntry'

    implements(IEntry)

    #  SECURITY MACHINERY DOES NOT LIKE PropertyManager.__ac_permissions__ '' ENTRY !!!!!!!!
    __ac_permissions__ = (
        (manage_properties, ('manage_addProperty', 'manage_editProperties',
                             'manage_delProperties', 'manage_changeProperties',
                             'manage_propertiesForm', 'manage_propertyTypeForm',
                             'manage_changePropertyTypes', )),
        (access_contents_information, ('hasProperty', 'propertyIds', 'propertyValues',
				       'propertyItems', 'getProperty', 'getPropertyType',
				       'propertyMap','blAccount', 'blTransaction',
                                       'blLedger', 'accountId' ), ('Anonymous', 'Manager')),
        (view, ('amountStr', 'absAmount', 'absAmountStr', 'isDebit', 'isCredit', 'status',
                'effective',  'reference',
                'isControlEntry', 'asCSV')),
        (OperateBastionLedgers, ('edit', 'setReference',)),
        (ManageBastionLedgers, ('manage_edit',)),
        ) + BSimpleItem.__ac_permissions__

    #
    # we have some f**ked up stuff because id's may be used further up the aquisition path ...
    #
    __replaceable__ = 1

    manage_options =  (
        {'label': 'Details',    'action' : 'manage_main'},
        {'label': 'View',       'action' : ''},
        {'label': 'Properties', 'action' : 'manage_propertiesForm'},
        ) + BSimpleItem.manage_options

    manage_main = PageTemplateFile('zpt/view_entry', globals())
    manage_propertiesForm = PageTemplateFile('zpt/edit_entry', globals())

    property_extensible_schema__ = 0
    _properties = (
        { 'id'   : 'title',    'type' : 'string',    'mode' : 'w' },
        { 'id'   : 'ref',      'type' : 'string',    'mode' : 'w' },  # this seems to screw up!
        { 'id'   : 'account',  'type' : 'string',    'mode' : 'w' },
        { 'id'   : 'amount',   'type' : 'currency',  'mode' : 'w' },
        { 'id'   : 'ledger',   'type' : 'selection', 'mode' : 'w' , 'select_variable': 'ledgerIds'},
        )

    def __init__(self, id, title, account, amount, ref='', ledger=''):
        assert type(account) == types.StringType, "Invalid Account: %s" % account
        assert_currency(amount)
        self.id = id
        self.title = title
        # account is actually the account path from the Ledger
        self.account = account
        self.amount = amount
        self.ref = ref
        # this is the Ledger Id
        self.ledger = ledger   # not know until posted ...

    def Title(self):
        """
        return the description of the entry, guaranteed non-null
        """
        return self.title or self.blAccount().title

    def amountStr(self): return self.amount.strfcur()
    def absAmount(self): return abs(self.amount)
    def absAmountStr(self): return self.absAmount().strfcur()
    def isDebit(self): return self.amount > 0
    def isCredit(self): return not self.isDebit()
    def effective(self):
        """
        return the effective date of the entry - usually deferring to the effective
        date of the underlying transaction the entry relates to

        a None value represents a control entry
        """
        dt = getattr(aq_base(self), '_effective_date', None)
        if dt:
            return dt
        try:
            txn = self.blTransaction()
            if txn:
                return txn.effective_date
        except:
            # hmmm - don't want to crash spectacularly ...
            return None
        return None

    # stop shite getting into the catalog ...
    def _noindex(self): pass
    tags = type = subtype = accno = _noindex

    def ledgerIds(self):
        """
        return list of valid id's which this could be posted to
        """
        # acquire ledgerValues from Ledger
        ids = ['']
        ids.extend(map(lambda x: x.getId(), self.ledgerValues()))
        return ids

    def blLedger(self):
        """
        return the ledger which I relate to (or None if I'm not yet posted)
        """
	if self.ledger:
            try:
                # I'm contained in <Ledger>/<BLLedger>/<BLAccount> ...
                #theledger = self.aq_parent.blLedger().aq_parent
                theledger = self.bastionLedger()
                return theledger._getOb(self.ledger)
            except:
                raise AttributeError, 'No BLLedger (%s), BastionLedger=%s\n%s' % (self.ledger, theledger, self)

	return None

    def accountId(self):
        """
        returns the id of the account which the entry is posted/postable to
        """
        if self.account.find('/') != -1:
            return self.account.split('/')[1]
        return self.account

    def blAccount(self):
        """
        return the underlying account to which this affects
        """
        #
        # hmmm - we may be acquiring bad context info doing this ...
        #
        if self.account:
            try:
                return self.unrestrictedTraverse(self.account)
            except:
                pass
        return None

    def blTransaction(self, id=None):
        """
        A context independent way of retrieving the txn.  If it's posted then there
        are issues with the object id not being identical in container and object ...

        """
        #TODO - remove the id parameter ...
        parent = self.aq_parent
        if isinstance(parent, BLTransaction):
            return parent
        # I must be in an account, acquire my Ledger's Transactions ...
        try:
            return parent.aq_parent._getOb(self.getId())
        except KeyError:
	    if self.ledger == '':
		# maybe I'm a control account entry ...
                if self.isControlEntry():
                    return None
		raise PostingError, 'unknown entry: %s' % self

            # OK - I must be in a subsidiary ledger ... - so parent is a account, within
            # a subsidiary ledger - we traverse from the Ledger root
            try:
                return parent.aq_parent.aq_parent.restrictedTraverse('%s/%s' % (self.ledger, self.getId()))
            except Exception, e:
                LOG.error('Transaction(ledger=%s) %s' % (self.ledger, self))
                # hmmm - soak these up for the moment ...
                return None
                raise KeyError, 'Transaction not found: %s/%s' %(self.ledger, self.getId())
        except AttributeError, e:
            raise AttributeError, '%s:%s - %s' % (parent.aq_parent, self.getId(), e)

    def _setEffectiveDate(self, dt):
        """
        some entry's don't belong to transaction's specifically, but we still want to give them a date
        """
        self._effective_date = floor_date(dt)
        self.unindexObject()
        self.indexObject()

    def edit(self, title, amount):
        """
        Plone edit
        """
        self._updateProperty('title', title)
        try:
            status = self.status()
            if not status in ('posted', 'reversed', 'cancelled', 'postedreversal'):
                self._updateProperty('amount', amount)
        except:
            pass
        
    def manage_edit(self, amount, ledger, title='', ref='', fx_rate='', posted_amount=None, REQUEST=None):
        """
        priviledged edit mode for experts only ...
        """
        self.manage_changeProperties(amount=amount,
                                     ledger=ledger,
                                     title=title,
                                     ref=ref)
        if type(fx_rate) == types.FloatType and isinstance(self.aq_parent, BLTransaction):
            self.fx_rate = fx_rate

        if posted_amount:
            self.posted_amount = ZCurrency(posted_amount)
            
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def isControlEntry(self):
        """
        returns if this is an entry for a control account
        """
        return False
    
    def __str__(self):
        """
        Debug representation
        """
        try:
            acct_str = self.blAccount().title
        except:
            acct_str = ''
            
        #fx = getattr(aq_base(self), 'fx_rate', '')
        fx = getattr(aq_base(self), 'posted_amount', '')
        if fx:
            fx = '%s, ' % fx
        return "<%s instance - %s, %s, %s,%s %s (%s) at %s>" % (self.meta_type,
                                                                self.id,
                                                                self.effective(),
                                                                self.amount,
                                                                fx,
                                                                self.account,
                                                                acct_str,
                                                                self.absolute_url())

    __repr__ = __str__

    def indexObject(self):
        """ Handle indexing """
        cat = self.aq_parent.catalog()   # either BLTransactions or BLAccounts ..
        if cat.meta_type == 'BLAccounts':
            try:
                url = '/'.join(self.getPhysicalPath())
                cat.catalog_object(self, url)
            except:
                pass
        
    def unindexObject(self):
        """ Handle unindexing """
        cat = self.aq_parent.catalog() # either BLTransactions or BLAccounts ...
        try:
             url = '/'.join(self.getPhysicalPath())
             cat.uncatalog_object(url)
        except:
            pass

    def posted(self):
        """
        return the posted amount, or fallback to amount - this is used to more
        accurately return multi-currency values
        """
        return getattr(aq_base(self), 'posted_amount', None) or self.amount

    def _post(self, force=False):
        """
        write a copy of yourself to the account - changing id to txn id
        """
        txn = self.blTransaction()
        account = self.blAccount()
        id = txn.getId()
        # copy itself into the account using the parent txn id as the id
        entry = self._getCopy(self)
        entry.id = id
        entry.ledger = txn.blLedger().getId()

        # do any FX conversion ...
        currency = entry.amount.currency()
        if currency != account.base_currency:
            rate = self.portal_bastionledger.crossMidRate(account.base_currency, currency, txn.effective_date)
            entry.amount = ZCurrency(account.base_currency, self.amount._amount * rate)
            self.fx_rate = rate   # record this for posterity ...

        # post it ...
        try:
            account._setObject(id, entry)
        except KeyError:
            if force:
                account._delObject(id, force=True)
                account._setObject(id, entry)
            else:
                raise AlreadyPostedError, (str(entry), str(account),list(account.objectItems()), str(txn))
        
        # return the posted entry
        return entry

    def setReference(self, value):
        self._updateProperty('ref', value)
        
    def reference(self):
        # return a string, or the underlying object if available ...
        if self.ref:
            try:
                return self.unrestrictedTraverse(self.ref)
            except:
                return self.ref
        return ''

    def status(self):
	"""
	my status is the status of my transaction ...
	"""
        try:
            txn = self.blTransaction()
            if txn:
                # hmmm - this is old cruft and only here to support really old imports ...
                if not callable(txn.status):
                    return txn.status
                return txn.status()
        except:
            pass
        # OK - must be a special entry ...
        return 'posted'

    def _repair(self):
        #
        # date is irrelevant on the entry - it's an attribute of the txn ...
        #
        if getattr(aq_base(self), 'date', None):
            delattr(self, 'date')
	ledger = getattr(aq_base(self), 'ledger', None)
        if ledger and type(ledger) != type(''):
            self._updateProperty('ledger', self.aq_parent.blLedger().getId())
        if self.account.find('Accounts/') != -1:
            self.account = self.account.replace('Accounts/', '')
        if self.account.find('Transactions/') != -1:
            self.account = self.account.replace('Transactions/', '')

    def _updateProperty(self, name, value):
        """
        do a status check on the transaction after updating amount
        """
        # we don't update any entries except those in Transactions - ie not posted ...
        #if not isinstance(self.aq_parent, BLTransaction) and name not in ('ref', 'title', 'ledger'):
        #    return
        
        PropertyManager._updateProperty(self, name, value)
        if name == 'amount' and isinstance(self.aq_parent, BLTransaction):
            self.aq_parent.setStatus()

    def __add__(self, other):
	"""
	do any necessary currency conversion ...
	"""
        if not isinstance(other, BLEntry):
	    raise TypeError, other
            # do any FX conversion ...
	if not other.account == self.account:
	    raise ArithmeticError, other

        other_currency = other.amount.currency()
        self_currency = self.amount.currency()
        if other_currency != self_currency:
            rate = self.portal_bastionledger.crossMidRate(self_currency, other_currency, self.getTransaction().effective_date)
	    entry = BLEntry(self.getId(), 
			    self.title,
                            self.account, 
                            ZCurrency(self_currency, (other.amount.amount() * rate + self.amount.amount())), 
                            self.ref, 
                            self.ledger)
	    entry.fx_rate = rate
	    return entry
	else:
	    return BLEntry(self.getId(), 
                           self.title, 
                           self.account, 
                           other.amount + self.amount,
                           self.ref, 
                           self.ledger)

    def asCSV(self, datefmt='%Y/%m/%d', curfmt='%a'):
        """
        """
        txn = self.blTransaction()
        return ','.join((self.getId(),
                         self.ledger or txn and txn.aq_parent.getId() or '',
                         txn and txn.getId() or '',
                         '"%s"' % self.Title(),
                         txn and '"%s"' % txn.effective_date.toZone(self.timezone).strftime(datefmt) or '',
                         '"%s"' % self.amount.strfcur(curfmt),
                         self.account,
                         self.status()))

    def __cmp__(self, other):
        """
        sort entries on effective date
        """
        other_dt = getattr(other, 'effective', None)
        if not other_dt:
            return 1
        if callable(other_dt):
            other_dt = other_dt()

        self_dt = self.effective()

        if self_dt < other_dt: return 1
        if self_dt > other_dt: return -1
        return 0

Globals.InitializeClass(BLEntry)

