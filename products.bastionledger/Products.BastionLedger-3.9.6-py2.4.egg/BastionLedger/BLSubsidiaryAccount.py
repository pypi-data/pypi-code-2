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

import Globals, logging
from AccessControl import getSecurityManager, ClassSecurityInfo
from Acquisition import aq_base
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.BastionBanking.ZCurrency import ZCurrency
from DateTime import DateTime

from utils import floor_date
from BLBase import *
from BLAccount import BLAccount
from BLEntry import BLEntry
from BLSubsidiaryEntry import BLSubsidiaryEntry, manage_addBLSubsidiaryEntry
from BLSubsidiaryTransaction import manage_addBLSubsidiaryTransaction
from AccessControl.Permissions import manage_properties
from Permissions import OperateBastionLedgers, OverseeBastionLedgers
from email.Utils import parseaddr

manage_addBLSubsidiaryAccountForm = PageTemplateFile('zpt/add_subsidiaryaccount', globals()) 
def manage_addBLSubsidiaryAccount(self, title, description, type, subtype,
                                  accno, currency, tags=[], REQUEST=None):
    """ an account """

    try:
        id = self.nextAccountId()
        self._setObject(id, BLSubsidiaryAccount(id, title, description, type,
                                                subtype, currency,
                                                accno or id, tags))
    except:
        # TODO: a messagedialogue ...
        raise
    
    acct = self._getOb(id)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s/manage_workspace" % acct.absolute_url())
        
    return acct

def addBLSubsidiaryAccount(self, id, title='', description='', type='Asset', subtype='', accno='', tags=[]):
    """
    Plone constructor
    """
    account = manage_addBLSubsidiaryAccount(self,
                                            title=title,
                                            description=description,
                                            type=type,
                                            subtype=subtype,
                                            accno=accno or id,
                                            currency=self.defaultCurrency(),
                                            tags=tags)
    id = account.getId()
    return id
    
class BLSubsidiaryAccount( BLAccount ):

    meta_type = portal_type = 'BLSubsidiaryAccount'

    __ac_permissions__ = BLAccount.__ac_permissions__ + (
        (OverseeBastionLedgers, ('manage_mergeForm', 'manage_merge')),
        )

    _properties = BLAccount._properties + (
        {'id':'email',          'type':'string',    'mode': 'w'},
    )

    def manage_options(self):
        options = BLAccount.manage_options(self)
        return options[0:4] + [
            {'label':'Merge', 'action':'manage_mergeForm' },
            ] + options[4:]

    manage_mergeForm = PageTemplateFile('zpt/merge_accounts', globals())

    def manage_merge(self, ids=[], REQUEST=None):
        """
        move entries from nominated account(s) into this one, adjusting their postings
        and removing those account(s) from the ledger
        """
        merged = 0

        for id in ids:
            try:
                account = self.aq_parent._getOb(id)
            except:
                continue

            # we need to take a copy because otherwise we're unindexing stuff we previously
            # had just indexed with the account number changes/substitutions ...
            for v in list(account.objectValues()):
                k = v.getId()
                account._delObject(k)
                if isinstance(v, BLEntry):
                    # adjust the posted entry
                    v.account = '%s' % self.getId()
                    # adjust the original pre-posting in the transaction
                    txn = v.blTransaction()
                    txn.entry(account.getId()).account = '%s' % self.getId()
                self._setObject(k, v)
            # remove the old account
            self._delObject(id)
            merged += 1
            
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'merged %i accounts' % merged)
            return self.manage_main(self, REQUEST)

    def _setObject(self, id, object, Roles=None, User=None, set_owner=1):
        #
        # this should get called by the Ledger::manage_postTransaction method ...
        #
        # object is probably a BLEntry/BLSubsidiaryEntry
        #
        BLAccount._setObject(self, id, object, Roles, User, set_owner)
        if isinstance(object, BLSubsidiaryEntry):
            # retrieve it in acquisition context ...
            object = self._getOb(id)
            
            ledger = self.blLedger()
            control = ledger.controlAccount()
            controlEntry = ledger.controlEntry()

            # we may need to do a fx conversion ...
            if control.base_currency != object.amount._currency:
                rate = self.portal_bastionledger.crossBuyRate(control.base_currency,
                                                              object.amount.currency())
                amount = ZCurrency(control.base_currency, object.amount.amount() / rate)
                object.fx_rate = rate
            else:
                amount = object.amount
            controlEntry.amount += amount

            # adjust effective date on control entry to reflect latest txn in
            # subsidiary ledger
            effective = object.effective()
            if effective > controlEntry.lastTransactionDate():
                controlEntry._setEffectiveDate(effective)

        return id

    def _delObject(self, id, tp=1, suppress_events=False, force=0):
        if not force:
            object = self._getOb(id)
            if isinstance(object, BLEntry):
                try:
                    sub_entry = getattr( aq_base(self.controlAccount()), object.Account().getId() )
                    sub_entry._amount -= object._amount
                except:
                    # this is a f**ked entry delete it if we're god ...
                    if getSecurityManager().getUser().has_role('Manager'):
                        pass
                    else:
                        raise
        BLAccount._delObject(self, id, tp, suppress_events=suppress_events, force=force)

    def Xentries(self, effective=None, status=['posted',]):
        """
        returns all entries in given state
        """
        return filter(lambda x,status=status: x[1].status() in status,
                      self.objectItemsByDate(['BLEntry', 'BLSubsidiaryEntry'], effective or DateTime()))

    def entryItems(self, effective=[], status=['posted',], query={}, REQUEST=None):
        """
        returns all entries in given state
        """
        if effective:
            entries = self.objectItemsByDate(['BLEntry', 'BLSubsidiaryEntry'], effective)
        else:
            entries = self.objectItems(['BLEntry', 'BLSubsidiaryEntry'])

        if query and query.has_key('accno'):
            results = []
            for entry in entries:
                # go check the other legs of the transaction to see if they match
                txn = entry[1].blTransaction()
                for accno in query['accno']:
                    try:
                        other = txn.entry(accno)
                        if other.amount > 0 and query['debit'] or query['credit']:
                            results.append(entry)
                            break
                    except KeyError:
                        continue

            entries = results

        return filter(lambda x, status=status: x[1].status() in status, entries)


    def createTransaction(self, title='',reference=None, effective=None):
        """
        polymorphically create correct transaction for ledger ...
        """
	transactions = self.blLedger()
        tid = manage_addBLSubsidiaryTransaction(transactions, '',
                                                title or self.getId(), 
                                                effective or DateTime(),
                                                reference)
        return transactions._getOb(tid)

    def createEntry(self, txn, amount, title=''):
        """ transparently create a transaction entry"""
        manage_addBLSubsidiaryEntry(txn, self, amount, title)

    def getMemberIds(self, mt=None):
        """
        link account to member(s)
        """
        ids = []
        mt = mt or getToolByName(self, 'portal_membership')
        
        for raw_email in map(lambda x: parseaddr(x)[1],
                             self.emailAddresses()):
            if raw_email:
                ids.extend(map(lambda x: x['username'],
                               mt.searchMembers('email', raw_email)))
        if not ids:
            ids = [ self.getOwnerTuple()[1] ]

        return ids

    def getMembers(self, mt=None):
        """
        we link members based upon email address.  If the account is severally owned,
        you should add multiple email addresses
        """
        mt = mt or getToolByName(self, 'portal_membership')
  
        return map(lambda x: mt.getMemberById(x), self.getMemberIds(mt))

    def emailAddresses(self):
        """
        return email address as a list, useful if multiple addresses stored in email field
        """
        for separator in (',', ';'):
            if self.email.find(separator) != -1:
                return self.email.split(separator)
        return [ self.email ]

    def isJointAccount(self):
        """ returns whether or not this is a joint account """
        return len(self.getMemberIds()) > 1


    def _repair(self):
        BLAccount._repair(self)
        
Globals.InitializeClass(BLSubsidiaryAccount)

def date_field(x,y):
    x_dt = x[1].effective_date()
    y_dt = y[1].effective_date()
    if x_dt == y_dt: return 0
    if x_dt > y_dt: return 1
    return -1


