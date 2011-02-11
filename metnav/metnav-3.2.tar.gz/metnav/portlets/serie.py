# -*- coding: utf-8 -*-
## Copyright (C) 2009 Ingeniweb - Alter Way Solutions - all rights reserved
## No publication or distribution without authorization.


from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from plone.memoize.view import memoize
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite

from zope import schema
from zope.formlib import form
from z3c.form.browser.multi import MultiWidget

from Products.CMFPlone import PloneMessageFactory as _
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class ISeriePortlet(IPortletDataProvider):
    """
    A portlet displaying a the dossier thématique

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    titre_dossier = schema.TextLine(title=_(u"Titre du dossier"),
                            description=_(u"Saisissez le titre du dossier"),
                            default= _(u"La spectroscopie en astronomie"),
                            required=True)
    url_dossier = schema.TextLine(title=_(u"Chemin du dossier"),
                            description=_(u"Saisissez le chemin relatif du dossier - Ex : /dossiersthematiques/spectroscopie"),
                            default= _(u"/dossiersthematiques/spectroscopie"),
                            required=True)
                            
    #url_dossier = schema.URI(title=_(u"URL du dossier"),
    #                        description=_(u"Saisissez l'URL du dossier"),
    #                        default = "http://niangqiang.ens-lyon.fr/csp-preprod/dossiersthematiques/spectroscopie/",
    #                        required=True)
    
    nbr_elt = schema.Int(title=_(u"Nombre d'éléments à afficher dans le portlet"),
                            description=_(u"Saisissez le nombre d'éléments à afficher dans le portlet"),
                            default = 5,
                            required=True)
    desc_dossier = schema.TextLine(title=_(u"Description à afficher dans le portlet"),
                            description=_(u"Saisissez une phrase de description."),
                            default= _(u"Une série d'articles montrant des applications actuelles de l'observation des spectres en astronomie."),
                            required=True)
                            
class Assignment(base.Assignment):
    implements(ISeriePortlet)

    def __init__(self, titre_dossier=_(u"La spectroscopie en astronomie"), url_dossier=_(u"/dossiersthematiques/spectroscopie/"), nbr_elt=5, desc_dossier=_(u"Une série d'articles montrant des applications actuelles de l'observation des spectres en astronomie.")):
        self.titre_dossier = titre_dossier
        self.url_dossier = url_dossier
        self.nbr_elt = nbr_elt
        self.desc_dossier = desc_dossier
    @property
    def title(self):
        return self.data.titre_dossier

        
class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('templates/serie.pt')

    def update(self):
        pp_tool = getToolByName(self.context, 'portal_properties')
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()
        self.metadataNav = getToolByName(self.context, 'portal_metadataNav')
        self.meta_url = pp_tool.metnav_properties.getProperty('COLLECTION_METADATA')
    def render(self):
        return self._template()
    
    @property
    def titre(self):
        return _(u"Série du moment")
    
    def dossierDesc(self):
        return self.data.desc_dossier
    
    def dossierTitre(self):
        return self.data.titre_dossier
    
    def dossierUrl(self):
        return self.site_url+self.data.url_dossier
        
    def dossierNbr(self):
        return self.data.nbr_elt 
        
    def getSerieDuMoment(self):
        context = self.context
        exist = context.exist
        siteUrl = self.site_url
        url = siteUrl+self.data.url_dossier
        meta_url = self.meta_url
        
        if siteUrl !="http://culturesciencesphysique.ens-lyon.fr":
            urlDsLom = url.replace(siteUrl, "http://culturesciencesphysique.ens-lyon.fr")
        else:
            urlDsLom=url
        #return str(dossierNom)     
        results = exist.query(str(context.xq_dossier).replace('$COLL', meta_url).replace('$URL_DOSSIER', urlDsLom) % {'site_url':self.site_url}, object_only=1).results
        nbrElt = 0
        limit = self.data.nbr_elt
        resultsLimites=""
        while(nbrElt<limit):
            resultsLimites += str(results[nbrElt])
            nbrElt = nbrElt + 1
        return resultsLimites  
        #return url
        
class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ISeriePortlet)

    def create(self, data):
        return Assignment()
        #return Assignment(**data)



class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ISeriePortlet)
    label=_(u"Editer le portlet Série du moment")
    description=_(u"Ce portlet affiche les ressources appartenant aux dossiers thématiques.")


