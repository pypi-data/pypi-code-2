from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner,aq_parent
from plone.memoize.instance import memoize
from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from collective.multisitepanel.browser.multisitebase import MultisiteBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import transaction


class ProductsPanelView(BrowserView,MultisiteBase):
    
    title=_(u"Add-on Products")
    table = ViewPageTemplateFile('templates/msp_products_table.pt')
    details = ViewPageTemplateFile('templates/msp_products_details.pt')
    template = ViewPageTemplateFile('templates/skeleton.pt')

    def __init__(self, context, request):
        MultisiteBase.__init__(self, context, request)
        self.qi = getToolByName(self.context,'portal_quickinstaller')
        tmpList = self.qi.listInstallableProducts(skipInstalled=False)
        self.productsList = []
        for product in tmpList:
            product['version'] = self.qi.getProductVersion(product['id'])
            product['description'] = self.qi.getProductDescription(product['id'])
            self.productsList.append(product)

    def __call__(self):
        if self.request.form.has_key('reinstall_pid') and self.request.form.has_key('siteid') :
            if self.request.form['siteid'] == 'allSites':
                siteApps = [siteTuple[1] for siteTuple in self.sitesList]
            else : 
                siteApps = [self.context.restrictedTraverse('/'+self.request.form['siteid']),]
            self.multisite_reinstallProducts(siteApps,self.request.form['reinstall_pid'])
        return self.template()

    def productCompleteId(self,pid):
        """Return a string with the complete id of an old style products"""
        if pid.find('.') == -1 :
            return 'Products.'+pid
        else: return pid

    def pypiSearch(self, pid):
        """Return a string with the url for a research of the product on Pypi"""
        if pid is None: return pid
        return dict(label=_(u"Search on Pypy"),
                    url=u"http://pypi.python.org/pypi?%3Aaction=search&term="+self.productCompleteId(pid)+"&submit=search")

    def getProductByPid(self,pid):
        for product in self.productsList:
            if product['id'] == pid: return product
        else: return None

    def multisite_productInstalledVersion(self,this_site,pid):
        """Return a string with the installed version of a product on a plone site"""
        siteQi = getToolByName(this_site,'portal_quickinstaller')
        if siteQi.isProductInstalled(pid):
            obj = siteQi._getOb(pid)
            return obj.getInstalledVersion()
        return None

    def multisite_reinstallProducts(self,siteApps,product):
        for siteApp in siteApps:
            siteQi = getToolByName(siteApp,'portal_quickinstaller')
            if product and siteQi.isProductInstalled(product):
                siteQi.reinstallProducts([product])
                siteQi.notifyInstalled(product)
                transaction.savepoint()
        message = _(u"feedback", default=_(u"Reinstalled ${product}"), mapping={'product':product})
        self.messages.addStatusMessage(message,type="info")
        return 'Redirecting ...'