from zope.interface import alsoProvides, noLongerProvides
from Products.Five import BrowserView

from Products.galleriffic.interfaces import IGallerifficView

try:
    from Products.Archetypes.interfaces._base import IBaseFolder
except:
    from Products.Archetypes.interfaces.base import IBaseFolder

from Products.ATContentTypes.interface.topic import IATTopic

interfaces_dict = {
    'IGallerifficView': IGallerifficView
}

class CheckInterface(BrowserView):
    """ """
    def checkInterface(self, interface, unset=''):
        """ """
        
        def flagCondition():
            """
                se verifico una interfaccia di unset (unset=True), la condizione di visualizzazione della relativa azione
                e' il valore ritornato dal metodo

                se verifico una interfaccia di set, la condizione di visualizzazione della relativa azione
                e' negato rispetto al valore ritornato dal metodo
            """
            if unset:
                return False
            return True
            
        if not interfaces_dict.has_key(interface):
            return flagCondition()
        
        context = self.context
        
        if self.context.restrictedTraverse('@@plone').isDefaultPageInFolder():
            context = context.aq_inner.aq_parent
        
        if not (IBaseFolder.providedBy(context) or IATTopic.providedBy(context)):
            return flagCondition()
        
        iface = interfaces_dict[interface]
        
        return iface.providedBy(context)

class SetUnsetInterface(BrowserView):
    """ """
    def __call__(self):
        
        unset = self.request.get('unset', False)
        interface = self.request.get('iface', '')
        
        if not interfaces_dict.has_key(interface):
            self.context.plone_utils.addPortalMessage(interface + ' not exist')
            return self.request.response.redirect(self.context.absolute_url())
        
        context = self.context

        if self.context.restrictedTraverse('@@plone').isDefaultPageInFolder():
            context = context.aq_inner.aq_parent
    
        iface = interfaces_dict[interface]
        
        if unset == 'True':
            noLongerProvides(context, iface)
            context.setLayout(context.getDefaultLayout())
            self.context.plone_utils.addPortalMessage(interface + ' unset')
        else:
            alsoProvides(context, iface)
            context.setLayout('galleriffic_view')
            self.context.plone_utils.addPortalMessage(interface + ' set')
        
        context.reindexObject()
        return self.request.response.redirect(self.context.absolute_url())