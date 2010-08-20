from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner,aq_parent
from plone.memoize.instance import memoize
from pprint import PrettyPrinter
from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage


class UsersPanelView(BrowserView):
    
    template = ViewPageTemplateFile('templates/users_dashboard.pt')
    role_order = ('Manager', 'Reviewer', 'Reader', 'Member', 'Contributor', 'Editor')
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.messages=IStatusMessage(self.request)
        
    def back_link(self):
        return dict(label=_(u"Up to Multisite Panel"),
                    url=self.context.absolute_url())

    def __call__(self):
        self.request.set('disable_border', True)
        form = self.request.form
        self.searchstring = form.get('searchstring', '')
        self.userid = form.get('userid', '')
        if self.searchstring:
            self.distinctUsers = self.multisite_searchUser(self.searchstring)
            if len(self.distinctUsers)==1: self.userid = self.distinctUsers[0][0].getId()
            if len(self.distinctUsers)==0:
                message = _(u"feedback", default=_(u"No user found"))
                self.messages.addStatusMessage(message,type="info")
                self.searchstring = None
        return self.template()
    
    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    @property
    def zope(self):
        return self.context.restrictedTraverse('/')

    @memoize
    def listAllSites(self):
        return self.portal.ZopeFind(self.zope,obj_metatypes=['Plone Site'])

    def listRolesBySite(self,this_site):
        pm = getToolByName(this_site,'portal_membership')
        roles = [r for r in pm.getPortalRoles() if r != 'Owner']
        final_roles = [ r for r in self.role_order if r in roles ] + [ r for r in roles if r not in self.role_order ]
        return final_roles

    def listUidBySite(self,this_site):
        acl_users = getToolByName(this_site, "acl_users")
        siteUsers = acl_users.searchUsers() or ();
        return [user['userid'] for user in siteUsers]
    
    def filterUidByRole(self,this_site,role):
        uids = self.listUidBySite(this_site)
        mtool = getToolByName(this_site,'portal_membership')
        members = [mtool.getMemberById(uid) for uid in uids ]
        members = [member for member in members if member is not None ]
        return [this_user.id for this_user in members if this_user.has_role(role)]

    def countUsersByRoles(self,users):
        return [(role,len(self.filterUidByRole(users,role))) for role in self.role_order]
    
    def multisite_getRoles(self,this_site,uid):
        mtool = getToolByName(this_site,'portal_membership')
        member = mtool.getMemberById(uid)
        return member.getRoles()
    
    def multisite_searchUser(self,searchstring,this_site='all'):
        if this_site == 'all' :
            siteApps = [site[1] for site in self.listAllSites()]
        else : siteApps = [this_site,]
        distinctUsers = {}
        for siteApp in siteApps:
            acl_users = getToolByName(siteApp, "acl_users")
            siteUsers = acl_users.searchUsers(id=searchstring) or ();
            for user in siteUsers:
                if distinctUsers.has_key(user['userid']) and self.sameUsers(distinctUsers[user['userid']][0],self.multisite_getMemberById(siteApp,user['userid'])):
                    userSitesList = distinctUsers[user['userid']][1] or []
                    userSitesList.append(siteApp.id)
                else :
                    member = self.multisite_getMemberById(siteApp,user['userid'])
                    distinctUsers[user['userid']] = member, [siteApp.id,]
        return [(distinctUsers[key][0],distinctUsers[key][1]) for key in distinctUsers]
    
    def multisite_getMemberById(self,this_site,uid):
        mtool = getToolByName(this_site,'portal_membership')
        return mtool.getMemberById(uid)
    
    def sameUsers(self,user1,user2):
        if user1.getId() != user2.getId(): return False
        elif user1.email != user2.email: return False
        else: return True 