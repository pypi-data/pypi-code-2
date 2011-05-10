'''
Created on 13-aug-2009

@author: jm
'''
import re
import zope.interface
import zope.schema
import zope.container.interfaces
from zope.authentication.principal import PrincipalSource

from i18n import MessageFactory as _


class ILDAPGroupFolder(zope.interface.Interface):
    """LDAP-specifc GroupFolder Plugin for the Pluggable Authentication."""

    authenticatorName = zope.schema.Choice(
        title=_(u"LDAP Authenticator Name"),
        description=_(u"The LDAP Authenticator plugin name that authenticates users."),
        vocabulary="LDAP Authenticator Names",
        required=True,
        )

    groupsSearchBase = zope.schema.TextLine(
        title=_("Group search base"),
        description=_(u"The LDAP search base where groups are found."),
        required=False,
        default=u'ou=groups,dc=example,dc=com'
        )

    groupsSearchScope = zope.schema.TextLine(
        title=_("Group search scope"),
        description=_(u"The LDAP search scope used to find groups."),
        required=False,
        default=u'sub'
        )
    
    groupIdPrefix = zope.schema.TextLine(
        title=_("Group id prefix"),
        description=_(u"The prefix to add to all group ids."),
        default=u'group.ldap.',
        required=False,
        )

    groupIdAttribute = zope.schema.TextLine(
        title=_("Group Id attribute"),
        description=_(
        u"The LDAP attribute used to determine the "
        "group's id."),
        constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
        default=u'dn',
        required=False,
        )

    groupTitleAttribute = zope.schema.TextLine(
        title=_("Group Title attribute"),
        description=_(
            u"The LDAP attribute used to determine a group's title."),
        constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
        default=u'cn',
        required=True,
        )

    groupDescriptionAttribute = zope.schema.TextLine(
        title=_("Group Description attribute"),
        description=_(
            u"The LDAP attribute used to determine a group's description."),
        constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
        default=u'description',
        required=True,
        )
    
    groupMemberAttribute = zope.schema.TextLine(
        title=_("Group Member Attribute"),
        description=_(
            u"Group attribute to use for member lookup."),
        constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
        default=u'member',
        required=True,
        )
    
    groupMemberAttributeValue = zope.schema.TextLine(
        title=_("Group Member Attribute Value"),
        description=_(
            u"The attribute of the user entry that is used for the group member attribute."),
        constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
        default=u'dn',
        required=True,
        )


class IReadGroupInformation(zope.interface.Interface):

    title = zope.schema.TextLine(
        title=_("Title"),
        description=_("Provides a title for the permission."),
        required=True)

    description = zope.schema.Text(
        title=_("Description"),
        description=_("Provides a description for the permission."),
        required=False)

    principals = zope.schema.List(
        title=_("Principals"),
        value_type=zope.schema.Choice(
            source=PrincipalSource()),
        description=_(
        "List of ids of principals which belong to the group"),
        required=False)




class IReadGroupFolder(zope.container.interfaces.IReadContainer):

    zope.container.constraints.contains(IReadGroupInformation)

    prefix = zope.schema.TextLine(
        title=_("Group ID prefix"),
        description=_("Prefix added to IDs of groups in this folder"),
        readonly=True,
        )

    def getGroupsForPrincipal(principalid):
        """Get groups the given principal belongs to"""

    def getPrincipalsForGroup(groupid):
        """Get principals which belong to the group"""


