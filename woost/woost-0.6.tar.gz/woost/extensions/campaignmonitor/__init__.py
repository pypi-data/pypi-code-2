#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			March 2010
"""

from cocktail import schema
from cocktail.events import event_handler
from cocktail.persistence import datastore
from cocktail.translations import translations
from woost.models import (
    Site,
    StandardPage,
    Language,
    Controller,
    Template,
    Extension, 
    get_current_user,
    CreatePermission,                                                                                                                                                                                          
    ModifyPermission,
    DeletePermission,
    PermissionExpression
)

translations.define("CampaignMonitorExtension",
    ca = u"Campaign Monitor",
    es = u"Campaign Monitor",
    en = u"Campaign Monitor"
)

translations.define("CampaignMonitorExtension-plural",
    ca = u"Campaign Monitor",
    es = u"Campaign Monitor",
    en = u"Campaign Monitor"
)

class CampaignMonitorExtension(Extension):

    initialized = False

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet la integració amb el sistema de mailing Campaign Monitor""",
            "ca"
        )
        self.set("description",            
            u"""Permite la integración con el sistema de mailing Campaign Monitor""",
            "es"
        )
        self.set("description",
            u"""Allows the integration with the Campaign Monitor mailing system""",
            "en"
        )


    @event_handler
    def handle_loading(cls, event):

        extension = event.source

        from woost.extensions.campaignmonitor import (
            campaignmonitorlist,
            strings,
            useraction
        )

        from woost.extensions.campaignmonitor.campaignmonitorsubscriptionpage \
            import CampaignMonitorSubscriptionPage

        # Setup the synchronization view
        from woost.controllers.backoffice.backofficecontroller \
            import BackOfficeController
        from woost.extensions.campaignmonitor.synccontroller import \
            SyncCampaignMonitorListsController

        BackOfficeController.sync_campaign_monitor_lists = \
            SyncCampaignMonitorListsController

        # Extension fields
        from woost.extensions.campaignmonitor.campaignmonitorlist \
            import CampaignMonitorList

        CampaignMonitorExtension.add_member(
            schema.String(
                "api_key",
                required = True,
                text_search = False
            )
        )

        CampaignMonitorExtension.add_member(
            schema.String(
                "client_id",
                required = True,
                text_search = False
            )
        )

        CampaignMonitorExtension.add_member(
            schema.Collection(
                "lists",
                items = schema.Reference(
                    type = CampaignMonitorList
                ),
                integral = True,
                related_end = schema.Reference()
            )   
        )

        site_languages = Language.codes
            
        # Subscription controller
        campaign_monitor_controller = Controller.get_instance(
            qname = u"woost.extensions.campaignmonitor.subscription_controller"
        )   

        if campaign_monitor_controller is None:
            campaign_monitor_controller = Controller()
            campaign_monitor_controller.python_name = \
                u"woost.extensions.campaignmonitor.campaignmonitorcontroller.CampaignMonitorController"
            campaign_monitor_controller.qname = u"woost.extensions.campaignmonitor.subscription_controller"
            if "en" in site_languages:
                campaign_monitor_controller.set(
                    "title", u"Subscription to Campaign Monitor controller", "en"
                )
            if "es" in site_languages:
                campaign_monitor_controller.set(
                    "title", u"Controlador de suscripicón a Campaign Monitor", "es"
                )
            if "ca" in site_languages:
                campaign_monitor_controller.set(
                    "title", u"Controlador de subscripció a Campaign Monitor", "ca"
                )
            campaign_monitor_controller.insert()

        # Unsubscription controller
        unsubscription_controller = Controller.get_instance(
            qname = u"woost.extensions.campaignmonitor.unsubscription_controller"
        )   

        if unsubscription_controller is None:
            unsubscription_controller = Controller()
            unsubscription_controller.python_name = \
                u"woost.extensions.campaignmonitor.campaignmonitorunsubscriptioncontroller.CampaignMonitorUnsubscriptionController"
            unsubscription_controller.qname = u"woost.extensions.campaignmonitor.unsubscription_controller"
            if "en" in site_languages:
                unsubscription_controller.set(
                    "title", u"Unsubscription to Campaign Monitor controller", "en"
                )
            if "es" in site_languages:
                unsubscription_controller.set(
                    "title", u"Controlador de baja de Campaign Monitor", "es"
                )
            if "ca" in site_languages:
                unsubscription_controller.set(
                    "title", u"Controlador de baixa de Campaign Monitor", "ca"
                )
            unsubscription_controller.insert()

        # Subscription template
        subscription_view = Template.get_instance(
            qname = u"woost.extensions.campaignmonitor.subscription_template"
        )

        if subscription_view is None:
            subscription_view = Template()
            subscription_view.identifier = \
                u"woost.extensions.campaignmonitor.CampaignMonitorSubscriptionView"
            subscription_view.engine = u"cocktail"
            subscription_view.qname = u"woost.extensions.campaignmonitor.subscription_template"
            if "en" in site_languages:
                subscription_view.set("title", u"Subscription to Campaign Monitor view", "en")
            if "es" in site_languages:
                subscription_view.set("title", u"Vista de suscripción a Campaign Monitor", "es")
            if "ca" in site_languages:
                subscription_view.set("title", u"Vista de subscripció a Campaign Monitor", "ca")
            subscription_view.insert()
        
        # Unsubscription template
        unsubscription_view = Template.get_instance(
            qname = u"woost.extensions.campaignmonitor.unsubscription_template"
        )

        if unsubscription_view is None:
            unsubscription_view = Template()
            unsubscription_view.identifier = \
                u"woost.extensions.campaignmonitor.CampaignMonitorUnsubscriptionView"
            unsubscription_view.engine = u"cocktail"
            unsubscription_view.qname = u"woost.extensions.campaignmonitor.unsubscription_template"
            if "en" in site_languages:
                unsubscription_view.set("title", u"Unsubscription from Campaign Monitor view", "en")
            if "es" in site_languages:
                unsubscription_view.set("title", u"Vista de baja de Campaign Monitor", "es")
            if "ca" in site_languages:
                unsubscription_view.set("title", u"Vista de baixa de Campaign Monitor", "ca")
            unsubscription_view.insert()
        
        # Default subscription page
        subscription_page = CampaignMonitorSubscriptionPage.get_instance(
            qname = u"woost.extensions.campaignmonitor.subscription_page"
        )

        if subscription_page is None and not extension.initialized:
            subscription_page = CampaignMonitorSubscriptionPage(
                qname = u"woost.extensions.campaignmonitor.subscription_page"
            )
            if "en" in site_languages:
                subscription_page.set("title", u"Subscription page", "en")
            if "ca" in site_languages:
                subscription_page.set("title", u"Pàgina de subscripció", "ca")
            if "es" in site_languages:
                subscription_page.set("title", u"Página de suscripción", "es")
            subscription_page.parent = Site.main.home
            subscription_page.hidden = True
            subscription_page.insert()

        # Standard Template
        standard_template = Template.get_instance(
            qname = "woost.standard_template"
        )

        # Default pending page
        pending_page = StandardPage.get_instance(
            qname = u"woost.extensions.campaignmonitor.pending_page"
        )

        if pending_page is None and not extension.initialized:
            pending_page = StandardPage(
                qname = u"woost.extensions.campaignmonitor.pending_page"
            )
            if "en" in site_languages:
                pending_page.set("title", u"Page with instructions for subscription", "en")
                pending_page.set("body", u"""We've just been sent an email to 
confirm your email address. Please click on the link in this email to confirm 
your subscription.""", "en")
            if "es" in site_languages:
                pending_page.set("title", u"Pàgina d'instruccions de subscripció", "ca")
                pending_page.set("body", u"""Te hemos enviado un e-mail para 
confirmar tu dirección de correo electrónico. Por favor, haz clic en el enlace 
que aparece en el e-mail para confirmar tu suscripción.""", "es")
            if "ca" in site_languages:
                pending_page.set("title", u"Página de instrucciones de suscripcion", "es")
                pending_page.set("body", u"""T'hem enviat un e-mail per confirmar 
la teva adreça de correu electrònic. Si et plau, fes clic a l'enllaç que 
apareix a l'e-mail per confirmar la teva subscripció.""", "ca")
            pending_page.parent = Site.main.home
            pending_page.template = standard_template
            pending_page.hidden = True
            pending_page.insert()

        # Default confirmation success page
        confirmation_success_page = StandardPage.get_instance(
            qname = u"woost.extensions.campaignmonitor.confirmation_success_page"
        )

        if confirmation_success_page is None and not extension.initialized:
            confirmation_success_page = StandardPage(
                qname = u"woost.extensions.campaignmonitor.confirmation_success_page"
            )
            if "en" in site_languages:
                confirmation_success_page.set("title", u"Confirmation page", "en")
                confirmation_success_page.set("body", u"""Your subscription has 
been confirmed. You've been added to our list and will hear from us soon.""", "en")
            if "ca" in site_languages:
                confirmation_success_page.set("title", u"Pàgina de confirmació", "ca")
                confirmation_success_page.set("body", u"""La teva subscripció ha 
sigut confirmada. La teva adreça ha sigut afegida a la nostra llista i en breu 
rebràs notícies nostres.""", "ca")
            if "es" in site_languages:
                confirmation_success_page.set("title", u"Página de confirmación", "es")
                confirmation_success_page.set("body", u"""Tu suscripción ha sido 
confirmada. Tu dirección ha sido añadida a nuestra lista y en breve recibirás 
noticias nuestras.""", "es")
            confirmation_success_page.parent = Site.main.home
            confirmation_success_page.template = standard_template
            confirmation_success_page.hidden = True
            confirmation_success_page.insert()

        # Default unsubscribe page
        unsubscribe_page = StandardPage.get_instance(
            qname = u"woost.extensions.campaignmonitor.unsubscribe_page"
        )

        if unsubscribe_page is None and not extension.initialized:
            unsubscribe_page = StandardPage(
                qname = u"woost.extensions.campaignmonitor.unsubscribe_page"
            )
            if "en" in site_languages:
                unsubscribe_page.set("title", u"Unsubscribe page", "en")
                unsubscribe_page.set("body", u"""You have been successfully removed 
from this subscriber list. You will no longer hear from us.""", "en")
            if "ca" in site_languages:
                unsubscribe_page.set("title", u"Pàgina de baixa", "ca")
                unsubscribe_page.set("body", u"""La teva adreça ha sigut eliminada 
amb èxit d'aquesta llista de subscripció. No tornaràs a rebre comunicacions 
nostres.""", "ca")
            if "es" in site_languages:
                unsubscribe_page.set("title", u"Página de baja", "es")
                unsubscribe_page.set("body", u"""Tu dirección ha sido eliminada con 
éxito de esta lista de suscripción. No volverás a recibir comunicaciones 
nuestras.""", "es")
            unsubscribe_page.controller = unsubscription_controller
            unsubscribe_page.template = unsubscription_view
            unsubscribe_page.parent = Site.main.home
            unsubscribe_page.hidden = True
            unsubscribe_page.insert()

        extension.initialized = True
        datastore.commit()


    def synchronize_lists(self, restricted = False):                                                                                                                                                      
        """Synchronizes the list of Lists of the given Campaign Monitor account 
        with the site's database.

        The method queries Campaing Monitor API, retrieving the list of
        Lists for the indicated account and comparing it with the set of
        already known Lists (from previous executions of this method). The
        local database will be updated as follows:

            * Lists declared by Campaing Monitor that are not present in the 
              database will generate new instances.
            * Lists that exist on both ends will be updated with the data
              provided by the Campaing Monitor service (only non editable 
              members will be updated, so that data entered by users in the 
              backoffice is preserved).
            * Lists that were instantiated in a previous run but which have
              been deleted at the Campaign Monitor side will be removed from 
              the database.
                
        @param restricted: Indicated if access control should be applied to the
            operations performed by the method.
        @type restricted: bool
        """
        from campaign_monitor_api import CampaignMonitorApi
        from cocktail.controllers import context
        from cocktail.controllers.location import Location
        from woost.extensions.campaignmonitor.campaignmonitorlist import \
            CampaignMonitorList

        if restricted:
            user = get_current_user()

        api = CampaignMonitorApi(
            self.api_key,
            self.client_id
        )

        remote_lists = set()
        
        for list_data in api.client_get_lists():

            list_id = list_data["ListID"]
            cmlist = CampaignMonitorList.get_instance(list_id = list_id)
            remote_lists.add(list_id)

            # Check permissions
            if restricted and not user.has_permission(
                CreatePermission if cmlist is None else ModifyPermission,
                target = (cmlist or CampaignMonitorList)
            ):
                continue

            # Create new lists
            if cmlist is None:
                cmlist = CampaignMonitorList()
                cmlist.insert()
                cmlist.list_id = list_id
                self.lists.append(cmlist)

            # Modify new or updated lists with remote data
            cmlist.title = list_data.get("Name")

            list_detail_data = api.list_get_detail(list_id)

            # Modify remote lists with page urls

            def absolute_uri(publishable, *args, **kwargs):
                location = Location.get_current_host()
                location.path_info = context["cms"].uri(
                    publishable,
                    *args,
                    **kwargs
                )
                return str(location)

            if cmlist.unsubscribe_page:
                unsubscribe_page = "%s?user=[email]" % absolute_uri(cmlist.unsubscribe_page)
            else:
                unsubscribe_page = list_detail_data.get("UnsubscribePage")

            if cmlist.confirmation_success_page:
                confirmation_success_page = absolute_uri(cmlist.confirmation_success_page)
            else:
                confirmation_success_page = list_detail_data.get("ConfirmationSuccessPage")

            api.list_update(
                list_id,
                list_detail_data.get("Title"), 
                unsubscribe_page,
                list_detail_data.get("ConfirmOptIn"), 
                confirmation_success_page
            )

        # Delete lists that have been deleted from the user account
        missing_lists = CampaignMonitorList.select(
            CampaignMonitorList.list_id.not_one_of(remote_lists),
        )

        if restricted:
            missing_lists.add_filter(
                PermissionExpression(user, DeletePermission)
            )

        missing_lists.delete_items()
