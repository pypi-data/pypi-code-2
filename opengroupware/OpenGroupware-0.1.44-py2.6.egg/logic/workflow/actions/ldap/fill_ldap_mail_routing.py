#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
# THE SOFTWARE.
#
import json
from coils.core          import CoilsException, PropertyManager
from coils.foundation    import ldap_paged_search, LDAPConnectionFactory
from coils.core.logic    import ActionCommand

class MailUser(object):
    def __init__(self, dn):
        self.dn = dn

try:
    import ldap
except:
    class FillLDAPMailRoutingAction(object):
        pass
else:
    class FillLDAPMailRoutingAction(ActionCommand):
        __domain__ = "action"
        __operation__ = "fill-ldap-mail-routing"
        __aliases__   = [ 'fillLDAPMailRouting', "fillLDAPMailRoutingAction" ]

        def __init__(self):
            ActionCommand.__init__(self)

        @property
        def result_mimetype(self):
            return 'text/plain'

        def do_action(self):

            if not self._ctx.is_admin:
                raise CoilsException('Insufficient privilages to invoke {0}'.format(self.__operation__))

            dsa = LDAPConnectionFactory.Connect(self._dsa)

            # HACK: python-ldap does not like unicode attribute names
            #       hence - [str(x) for x in self._xmap.keys()]
            # WARN: This probably breaks in Python 3!
            attributes = [ ]
            if self._xuid1: attributes.append(self._xuid1)
            if self._xuid2: attributes.append(self._xuid2)
            if self._gn_attr: attributes.append(self._gn_attr)
            if self._mn_attr: attributes.append(self._sn_attr)
            if self._sn_attr: attributes.append(self._mn_attr)
            if self._mail_attr: attributes.append(self._mail_attr)
            attributes = [str(x) for x in attributes]

            results = ldap_paged_search(connection    = dsa,
                                        logger        = self.log,
                                        search_filter = self._xfilter,
                                        search_base   = self._xroot,
                                        attributes    = attributes,
                                        search_scope  = self._xscope)

            self.wfile.write('LDAP Filter:{0}\n'.format(self._xfilter))
            self.wfile.write('LDAP Base:{0}\n'.format(self._xroot))
            self.wfile.write('LDAP Attributes:{0}\n'.format(attributes))
            self.wfile.write('\n')
            self.wfile.write('Search found {0} results\n'.format(len(results)))
            self.wfile.write('\n')

            count = 0
            for user in results:

                self.log.info(user)

                count += 1

                user = MailUser(user[0])
                for key, value in user[1].items():
                    setattr(user, unicode(key).lower(), value)

                self.wfile.write('\n')
                self.wfile.write('LDAP DN:{0}\n'.format(user.dn))

                uid = attributes[self._xuid]
                if uid is None:
                    self.wfile.write('No UID attribute found for "{0}"\n'.format(ldap_dn))
                    self.wfile.write('\n')
                    continue

                # Strip the user login to the right-hand side based on the provided delimiter.
                if self._strip:
                    uid = uid.split(self._strip)[0]

                account = self._ctx.run_command('account::get', login=uid)
                is_new = False
                if not account:
                    if self._create == 'YES':
                       # TODO: Create an account!
                       account = self._ctx.run_command('contact::new', values={ 'login':      uid,
                                                                                'is_account': 1,
                                                                                'ldap_url':   ldap_dn,
                                                                                'source_url': ldap_dn } )
                       self.wfile.write('Creating new account for UID "{0}"'.format(uid))
                       is_new = True
                    else:
                        self.wfile.write('No account object foundfor UID "{0}"'.format(uid))
                        self.wfile.write('\n')
                        continue

                for source, target in self._xmap.items():
                    value = None
                    if source.lower() in attributes:
                        value = attributes[source.lower()]
                    if not value:
                        continue

                    target = target.split('.')
                    if len(target) == 1:
                        setattr(account, target[0], value)
                        self.wfile.write(' set contact value "{0}" to "{1}"\n'.format(target[0], value))
                    elif target[0] == 'cv':
                        # Set a companyValue attribute from map
                        cv = account.get_company_value(target[1])
                        if cv:
                            cv.set_value(value)
                            self.wfile.write(' set company value "{0}" to "{1}"\n'.format(cv.name, value))
                    elif target[0] == 'property':
                        namespace, name = PropertyManager.Parse_Property_Name('.'.join(target[1:]))
                        self._ctx.property_manager.set_property(account, namespace, name, value)
                        self.wfile.write(' assigned value "{0}" to property "{{{1}}}{2}"\n'.format(value, namespace, name))
                    elif target[0] == 'telephone':
                        # Set a telephone attribute from map
                        telephone = account.get_telephone(target[1])
                        if telephone:
                            setattr(telephone, target[2], value)
                            self.wfile.write(' set telephone type "{0}" attribute "{1}" to "{2}"\n'.format(target[1],target[2], value))
                    elif target[0] == 'address':
                        # Set an address attribute from map
                        address = account.get_address(target[1])
                        if address:
                            setattr(address, target[2], value)
                            self.wfile.write(' set address type "{0}" attribute "{1}" to "{2}"\n'.format(target[1], target[2],value))

            self.wfile.write('\n')

        def parse_action_parameters(self):
                self._dsa     = self.action_parameters.get('dsaName',     None)
                self._xfilter = self.action_parameters.get('filterText',  None)
                self._xroot   = self.action_parameters.get('searchScope', 'SUBTREE').upper()
                self._xscope  = self.action_parameters.get('searchScope', 'SUBTREE').upper()
                # Attributes
                self._domains = self.action_parameters.get('mailDomains',  None)
                self._xuid1   = self.action_parameters.get('uidAttribute1',  'uid')
                self._xuid2   = self.action_parameters.get('uidAttribute2',  None)
                # Attributes for building long-vanity e-mail aliases like adam.t.williams@example.com
                self._gn_attr = self.action_parameters.get('gnAttribute',  None)
                self._sn_attr = self.action_parameters.get('snAttribute',  None)
                self._mn_attr = self.action_parameters.get('mnAttribute',  None)
                self._mn_is_initials = self.action_parameters.get('mnIsInitials',  'NO')
                if self._mn_is_initials.upper() == 'YES':
                    self._mn_is_initials = True
                else:
                    self._mn_is_initials = False
                self._mail_attr  = self.action_parameters.get('mailAddressAttribute', 'mailLocalAddress')


                if not self._dsa:
                    raise CoilsException('No dsaNAME parameter specified for fillLDAPMailRoutingAction')

                if not self._xfilter:
                    raise CoilsException('No filterText [LDAP Search Filter] parameter specified for fillLDAPMailRoutingAction')


                if not self._xroot:
                    raise CoilsException('No searchRoot parameter specified for fillLDAPMailRoutingAction')

                if self._xscope == 'ONELEVEL':
                    self._xscope = ldap.SCOPE_ONELEVEL
                else:
                    self._xscope = ldap.SCOPE_SUBTREE
