#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
import os, ldap
from coils.core              import *
from coils.core.logic        import ActionCommand
from dsml1_writer            import DSML1Writer


class SearchAction(ActionCommand):
    # TODO: Make page size a default (low priority)
    __domain__    = "action"
    __operation__ = "ldap-search"
    __aliases__   = [ 'ldapSearch', 'ldapSearchAction' ]
    __debugOn__   = None

    def __init__(self):
        ActionCommand.__init__(self)
        if (SearchAction.__debugOn__ is None):
            sd = ServerDefaultsManager()
            SearchAction.__debugOn__ = sd.bool_for_default('LDAPDebugEnabled')

    @property
    def debugOn(self):
        return SearchAction.__debugOn__

    def do_action(self):
        dsa = LDAPConnectionFactory.Connect(self._dsa)
        if (self.debugOn): self.log.debug('LDAP SEARCH: Got connection to DSA')
        if (len(self._xattrs) == 0):
            self.xattrs = None
        try:
            results = []
            control = ldap.controls.SimplePagedResultsControl(ldap.LDAP_CONTROL_PAGE_OID,True,(10,''))
            if (self.debugOn): self.log.debug('LDAP SEARCH: Created paging control')
            message_id = dsa.search_ext(self._xroot,
                                        self._xscope,
                                        self._xfilter,
                                        attrlist=self._xattrs,
                                        serverctrls=[control])
            if (self.debugOn): self.log.debug('LDAP SEARCH: Message id is {0}'.format(message_id))
            page = 0
            while True:
                page += 1
                if (self.debugOn): self.log.debug('LDAP SEARCH: Retrieving page {0}'.format(page))
                rtype, rdata, rmsgid, serverctrls = dsa.result3(message_id)
                if (self.debugOn): self.log.debug('LDAP SEARCH: {0} results received in page.'.format(len(rdata)))
                results.extend(rdata)
                if (len(results) > self._xlimit):
                    if (self.debugOn): self.log.debug('LDAP SEARCH: Search results have exceeded limit [count].')
                    break;
                if (len(rdata) < 10):
                    if (self.debugOn):
                        self.log.debug('LDAP SEARCH: Page contains less than page-size result, assuming search complete.')
                    break;
                pctrls = [
                    c
                    for c in serverctrls
                    if c.controlType == ldap.LDAP_CONTROL_PAGE_OID
                ]
                if pctrls:
                    est, cookie = pctrls[0].controlValue
                    if cookie:
                        control.controlValue = (10, cookie)
                        message_id = dsa.search_ext(self._xroot,
                                                    self._xscope,
                                                    self._xfilter,
                                                    attrlist=self._xattrs,
                                                    serverctrls=[control])
                        if (self.debugOn):
                            self.log.debug('LDAP SEARCH: Message id is {0}'.format(message_id))
                else:
                    if (self.debugOn): self.log.debug('LDAP SEARCH: Breaking paging loop.')
                    break
        except ldap.NO_SUCH_OBJECT, e:
            self.log.exception(e)
            self.log.info('LDAP NO_SUCH_OBJECT exception, generating empty message')
        except ldap.INSUFFICIENT_ACCESS, e:
            self.log.exception(e)
            self.log.info('LDAP INSUFFICIENT_ACCESS exception, generating empty message')
        except ldap.SERVER_DOWN, e:
            self.log.exception(e)
            self.log.warn('Unable to contact LDAP server!')
            raise e
        except Exception, e:
            self.log.error('Exception in action ldapSearch')
            self.log.exception(e)
            raise e
        else:
            if (self.debugOn): self.log.debug('LDAP SEARCH: Formatting results to DSML.')
            writer = DSML1Writer()
            writer.write(results, self._wfile)
        dsa.unbind()

    def parse_action_parameters(self):
        self._dsa    = self._params.get('dsaName',     None)
        self._xfilter = self._params.get('filterText',  None)
        self._xroot   = self._params.get('searchRoot',  None)
        self._xscope  = self._params.get('searchScope', 'SUBTREE').upper()
        self._xlimit = int(self._params.get('searchLimit', 150))
        self._xattrs = []
        for xattr in self._params.get('attributes', '').split(','):
            self._xattrs.append(str(xattr))
        if (self._dsa is None):
            raise CoilsException('No DSA defined for ldapSearch')
        # Check query value
        if (self._xfilter is None):
            raise CoilsException('No filter defined for ldapSearch')
        else:
            self._xfilter = self.decode_text(self._xfilter)
        # Check root parameter
        if (self._xroot is None):
            raise CoilsException('No root defined for ldapSearch')
        else:
            self._xroot = self.decode_text(self._xroot)
        # Convert subtree parameter
        if (self._xscope == 'SUBTREE'):
            self._xscope = ldap.SCOPE_SUBTREE
        else:
            self._xscope = ldap.SCOPE_SUBTREE
        if (self.debugOn):
            self.log.debug('LDAP SEARCH FILTER:{0}'.format(self._xfilter))
            self.log.debug('LDAP SEARCH BASE:{0}'.format(self._xroot))
            self.log.debug('LDAP SEARCH LIMIT:{0}'.format(self._xlimit))


    def do_epilogue(self):
        pass