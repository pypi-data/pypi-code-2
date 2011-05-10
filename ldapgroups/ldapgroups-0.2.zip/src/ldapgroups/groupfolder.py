'''
Created on 13-aug-2009

@author: jm
'''

from zope.interface import Interface, implements, adapter
from zope.pluggableauth.interfaces import (IAuthenticatorPlugin, IQueriableAuthenticator
                                                , IQuerySchemaSearch, IPrincipalInfo, IPrincipalCreated)
from zope import schema, component, location
from persistent import Persistent
from ldappas.interfaces import ILDAPAuthentication
from ldap.filter import filter_format
from zope.container.contained import Contained
from interfaces import ILDAPGroupFolder, IReadGroupFolder, IReadGroupInformation
from zope.security.interfaces import IGroupAwarePrincipal
from zope.componentvocabulary.vocabulary import UtilityVocabulary
from ldapadapter.interfaces import NoSuchObject, ServerDown
from ldap import LDAPError
from zope.size.interfaces import ISized
from i18n import _
from zope.schema.fieldproperty import FieldProperty
from zope.interface import alsoProvides
from zope.security.interfaces import IGroup



class IADGroupSearchSchema(Interface):
    """A LDAP-specific schema for searching for groups."""

    uid = schema.TextLine(
        title=u'uid',
        required=False)

    cn = schema.TextLine(
        title=u'cn',
        required=False)


class LDAPGroupInformation(Persistent):
    implements(IReadGroupInformation, IPrincipalInfo)
    
#    credentialsPlugin = None
#    authenticatorPlugin  = None
    
    def __init__(self, plugin, id, title, description):
        self.plugin = plugin
        self.id = id
        self.title = title
        self.description = description
        
    @property
    def principals(self):
        return self.plugin.getPrincipalsForGroup(self.id)
    
    def __repr__(self):
        return 'LDAPGroupInformation(%r)' % self.id
    
    def __eq__(self, other):
        return self.id == other.id



class LDAPGroupSize(object):
    implements(ISized)
    component.adapts(IReadGroupInformation)
    
    def __init__(self, context):
        self.context = context
        
    def sizeForSorting(self):
        return ('item', len(self.context.principals))
    def sizeForDisplay(self):
        return _('${items} items', mapping={'items': len(self.context.principals)})


class LDAPGroups(Persistent, Contained):
    implements(IAuthenticatorPlugin,
               ILDAPGroupFolder,
               IQueriableAuthenticator, 
               IQuerySchemaSearch, 
               IReadGroupFolder)
    
    groupsSearchBase = FieldProperty(ILDAPGroupFolder['groupsSearchBase'])
    groupsSearchScope = FieldProperty(ILDAPGroupFolder['groupsSearchScope'])  
    groupIdPrefix = FieldProperty(ILDAPGroupFolder['groupIdPrefix'])
    groupTitleAttribute = FieldProperty(ILDAPGroupFolder['groupTitleAttribute'])
    groupIdAttribute = FieldProperty(ILDAPGroupFolder['groupIdAttribute'])
    groupDescriptionAttribute = FieldProperty(ILDAPGroupFolder['groupDescriptionAttribute'])
    groupMemberAttribute = FieldProperty(ILDAPGroupFolder['groupMemberAttribute'])
    groupMemberAttributeValue = FieldProperty(ILDAPGroupFolder['groupMemberAttributeValue'])

    schema = IADGroupSearchSchema
    
    def __init__(self, ldapname='', prefix=''):
        super(LDAPGroups, self).__init__()
        self.authenticatorName = ldapname
        self.groupIdPrefix = prefix

    def getLDAPAuthenticator(self):
        """Get the LDAP adapter according to our configuration.

        Returns None if adapter connection is configured or available.
        """
        util = component.queryUtility(ILDAPAuthentication, self.authenticatorName)
        return util

    def authenticateCredentials(self, credentials):
        # user folders don't authenticate
        pass

    def principalInfo(self, id):
        if id.startswith(self.groupIdPrefix):
            id = id[len(self.groupIdPrefix):]
            res = self._search({self.groupIdAttribute:id}, attrs=[self.groupIdAttribute
                                                                  , self.groupTitleAttribute
                                                                  , self.groupDescriptionAttribute])
            if res and len(res) == 1:
                dn, entry = res[0]
                # Find the id we'll return.
                id_attr = self.groupIdAttribute
                if id_attr == 'dn':
                    id = dn
                elif entry.get(id_attr):
                    id = entry[id_attr][0]
                else:
                    raise KeyError
                id = self.groupIdPrefix + id
                return self._groupInfoFromEntry(id, entry)
        

    def _search(self, query={}, base=None, scope=None, attrs=None, util=None):
        if base is None:
            base = self.groupsSearchBase
        if scope is None:
            scope = self.groupsSearchScope
        if util is None:
            util = self.getLDAPAuthenticator()

        if util is None:
            return [] 

        da = util.getLDAPAdapter()
        if da is None:
            return []

        try:
            conn = da.connect()
        except ServerDown:
            return []

        # Build the filter based on the query
        filter_elems = []
        for key, value in query.items():
            if not value:
                continue
            filter_elems.append(filter_format('(%s=%s)',
                                              (key, value)))
        filter = ''.join(filter_elems)
        if len(filter_elems) > 1:
            filter = '(&%s)' % filter

        if not filter:
            filter = '(objectClass=group)'
        
        try:
            res = conn.search(base, scope, filter=filter, attrs=attrs)
        except (NoSuchObject,LDAPError):
            return []
        
        return res

    def search(self, query, start=None, batch_size=None):
        res = self._search(query, attrs=[self.groupIdAttribute])

        infos = []
        for dn, entry in res:
            try:
                infos.append(self.groupIdPrefix+entry[self.groupIdAttribute][0])
            except (KeyError, IndexError):
                pass

        if start is None:
            start = 0
        if batch_size is not None:
            return infos[start:start+batch_size]
        else:
            return infos[start:]

    def getGroupsForPrincipal(self, principalid):
        groups = []

        util = self.getLDAPAuthenticator()
        if util is None:
            return None

        principals = []
        if util.principalIdPrefix in principalid:
            internal_id = principalid[len(util.principalIdPrefix):]
            principals = self._search({util.idAttribute:internal_id, 'objectClass':'user'},
                         base = util.searchBase,
                         scope= util.searchScope,
                         attrs=[self.groupMemberAttributeValue], util=util)
        elif self.groupIdPrefix in principalid:
            internal_id = principalid[len(self.groupIdPrefix):]
            principals = self._search({self.groupIdAttribute:internal_id, 'objectClass':'group'},
                         attrs=[self.groupMemberAttributeValue], util=util)
        for dn, principal in principals:
            memberValue = principal[self.groupMemberAttributeValue][0]
            res = self._search({self.groupMemberAttribute:memberValue, 'objectClass':'group'}, attrs=[self.groupIdAttribute], util=util)
            for dn, entry in res:
                group_id = entry[self.groupIdAttribute][0]
                prefixed_id = self.groupIdPrefix + group_id
                groups.append(prefixed_id)
        return groups
        
    def getPrincipalsForGroup(self, groupid):
        principals = []

        util = self.getLDAPAuthenticator()
        if util is None:
            return None

        internal_id = groupid[len(self.groupIdPrefix):]

        res = self._search( {self.groupIdAttribute:internal_id, 'objectClass':'group'}, 
                           attrs=[self.groupMemberAttribute], util=util)
        for dn,entry in res:
            for value in entry.get(self.groupMemberAttribute, []):
                users = self._search({self.groupMemberAttributeValue:value, 'objectClass':'user'},
                             base = util.searchBase,
                             scope= util.searchScope,
                             attrs=[util.idAttribute], util=util)
                for dn,user in users:
                    principal_id = user[util.idAttribute][0]
                    prefixed_id = util.principalIdPrefix + principal_id
                    principals.append(prefixed_id)
        return principals
        
    def __len__(self):
        return len(self._search())
        
    
    def __iter__(self):
        res = self._search()
        for dn, entry in res:
            principal_id = entry[self.groupTitleAttribute][0]
            yield principal_id
                
    def keys(self):
        return list(iter(self))
    
    def items(self):
        ret = []
        res = self._search(attrs=[self.groupIdAttribute, self.groupTitleAttribute, self.groupDescriptionAttribute])
        for dn, entry in res:
            principal_id = entry[self.groupIdAttribute][0]
            prefixed_id = self.groupIdPrefix + principal_id
            title = entry[self.groupTitleAttribute][0]
            ret.append((title, self._groupInfoFromEntry(prefixed_id, entry)))
        return ret

    def values(self):
        ret = []
        res = self._search(attrs=[self.groupIdAttribute, self.groupTitleAttribute, self.groupDescriptionAttribute])
        for dn, entry in res:
            principal_id = entry[self.groupIdAttribute][0]
            prefixed_id = self.groupIdPrefix + principal_id
            ret.append(self._groupInfoFromEntry(prefixed_id, entry))
        return ret

    def __contains__(self, key):
        res = self._search({self.groupTitleAttribute:key}, attrs=[])
        return len(res)>0

    has_key = __contains__
    
    def __getitem__(self, key):
        res = self._search({self.groupTitleAttribute:key}, attrs=[self.groupIdAttribute, self.groupTitleAttribute, self.groupDescriptionAttribute])
        if res and len(res) == 1:
            dn, entry = res[0]
            # Find the id we'll return.
            id_attr = self.groupIdAttribute
            if id_attr == 'dn':
                id = dn
            elif entry.get(id_attr):
                id = entry[id_attr][0]
            else:
                raise KeyError
            id = self.groupIdPrefix + id
            return self._groupInfoFromEntry(id, entry)
        raise KeyError

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def _groupInfoFromEntry(self, id, entry):
        info = LDAPGroupInformation(self, id, entry[self.groupTitleAttribute][0]
                                    , self.groupDescriptionAttribute and self.groupDescriptionAttribute in entry and entry[self.groupDescriptionAttribute][0] or '')
        return location.location.LocationProxy(info, self, info.title)


@component.adapter(IPrincipalCreated)
def setGroupsForPrincipal(event):
    """Set group information when a principal is created"""

    principal = event.principal
    if not IGroupAwarePrincipal.providedBy(principal):
        return

    authentication = event.authentication

    for name, plugin in authentication.getAuthenticatorPlugins():
        if not ILDAPGroupFolder.providedBy(plugin):
            continue
        groupfolder = plugin
        principal.groups.extend(
            [authentication.prefix + id
             for id in groupfolder.getGroupsForPrincipal(principal.id)
             ])
        id = principal.id
        prefix = authentication.prefix + groupfolder.groupIdPrefix
        if id.startswith(prefix) and id[len(prefix):] in groupfolder:
            alsoProvides(principal, IGroup)
            
            

class LDAPAuthentcatorVocabulary(UtilityVocabulary):
    interface = ILDAPAuthentication
    nameOnly = True



