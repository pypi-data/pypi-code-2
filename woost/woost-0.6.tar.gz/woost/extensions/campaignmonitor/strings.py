#-*- coding: utf-8 -*-
u"""

@author:        Jordi Fernández
@contact:       jordi.fernandez@whads.com
@organization:  Whads/Accent SL
@since:         March 2010
"""
from cocktail.translations import translations

# UI
#------------------------------------------------------------------------------
translations.define("Action sync_campaign_monitor_lists",                                                                                                                                                                       
    ca = u"Sincronitzar amb Campaign Monitor",
    es = u"Sincronizar con Campaign Monitor",
    en = u"Synchronize with Campaign Monitor"
)

# CampaignMonitorExtension
#------------------------------------------------------------------------------
translations.define("CampaignMonitorExtension.api_key",
    ca = u"Clau d'API",
    es = u"Clave de API",
    en = u"API key"
)

translations.define("CampaignMonitorExtension.client_id",
    ca = u"Id de client",
    es = u"Id de cliente",
    en = u"Client id"
)

translations.define("CampaignMonitorExtension.lists",
    ca = u"Llistes",
    es = u"Listas",
    en = u"Lists"
)

# CampaignMonitorList
#------------------------------------------------------------------------------
translations.define("CampaignMonitorList",
    ca = u"Llista de subscripció",
    es = u"Lista de suscripción",
    en = u"Subscription list"
)

translations.define("CampaignMonitorList-plural",
    ca = u"Llistes de subscripció",
    es = u"Listas de suscripción",
    en = u"Subscription lists"
)

translations.define("CampaignMonitorList.list_id",
    ca = u"Id de llista",
    es = u"Id de lista",
    en = u"List id"
)

translations.define("CampaignMonitorList.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("CampaignMonitorList.pending_page",
    ca = u"Pàgina d'instruccions",
    es = u"Página de instrucciones",
    en = u"Instructions page"
)

translations.define("CampaignMonitorList.unsubscribe_page",
    ca = u"Pàgina de baixa",
    es = u"Página de baja",
    en = u"Unsubscribe page"
)

translations.define("CampaignMonitorList.confirmation_success_page",
    ca = u"Pàgina de confirmació d'alta",
    es = u"Página de confirmación de alta",
    en = u"Confirmation success page"
)

# CampaignMonitorSubscriptionPage
#------------------------------------------------------------------------------
translations.define("CampaignMonitorSubscriptionPage",
    ca = u"Pàgina de subscripció a mailing",
    es = u"Página de suscripción a mailing",
    en = u"Mailing subscription page"
)

translations.define("CampaignMonitorSubscriptionPage-plural",
    ca = u"Pàgines de subscripció a mailing",
    es = u"Páginas de suscripción a mailing",
    en = u"Mailing subscription pages"
)

translations.define("CampaignMonitorSubscriptionPage.body",
    ca = u"Cos",
    es = u"Cuerpo",
    en = u"Body"
)

translations.define("CampaignMonitorSubscriptionPage.lists",
    ca = u"Llistes",
    es = u"Listas",
    en = u"Lists"
)

translations.define("CampaignMonitorSubscriptionPage.subscription_form",
    ca = u"Formulari de subscripció",
    es = u"Formulario de suscripción",
    en = u"Subscription form"
)

# CampaignMonitorListsSynchronizationView
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView outcome",
    ca = u"S'ha completat la sincronització.",
    es = u"Se ha completado la sincronización.",
    en = u"Synchronization complete."
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView no changes",
    ca = u"No ha estat necessari realitzar cap actualització.",
    es = u"No ha sido necesario realizar ninguna actualización.",
    en = u"No update was needed."
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView cancel button",                                                                                                                                
    ca = u"Tancar",
    es = u"Cerrar",
    en = u"Close"
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView created lists title",
    ca = u"Llistes afegides",
    es = u"Listas añadidas",
    en = u"Added lists"
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView created lists explanation",
    ca = u"Les següents llistes s'han incorporat al lloc web:",
    es = u"Las listas siguientes se han incorporado al sitio web:",
    en = u"The following lists were added to the web site:"
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView modified lists title",
    ca = u"Llistes modificades",
    es = u"Listas modificadas",
    en = u"Modified lists"
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView modified lists explanation",
    ca = u"S'ha actualitzat la informació de les llistes següents:",
    es = u"Se ha actualizado la información de las listas siguientes:",
    en = u"The following lists had changes that have been reflected on the "
         u"web site:"
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView deleted lists title",
    ca = u"Llistes eliminades",
    es = u"Listas eliminadas",
    en = u"Deleted lists"
)

translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorListsSynchronizationView deleted lists explanation",
    ca = u"Les següents llistes ja no són presents a Campaign Monitor i s'han "
         u"eliminat del lloc web:",
    es = u"Las listas siguientes ya no están disponibles en Campaign Monitor y se "
         u"han eliminado del sitio web:",
    en = u"The following lists are no longer available at Campaign Monitor and "
         u"have been deleted from the web site:"
)

# CampaignMonitorSubscriptionView
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorSubscriptionView api error",
    ca = u"Hi ha hagut algun problema. Siusplau, provi-ho de nou més tard.",
    es = u"Ha habido algun problema, por favor pruebelo más tarde.",
    en = u"An error occurred, please try again later."
)

# CampaignMonitorUnsubscriptionView
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.campaignmonitor.CampaignMonitorUnsubscriptionView resubscribe",
    ca = u"""No volies donar-te de baixa? <a href="%s">Clica aquí</a> per 
resubscriure't i continuar rebent comunicacions nostres.""",
    es = u"""No querías darte de baja? <a href="%s">Clica aquí</a> para 
resuscribirte y continuar recibiendo comunicaciones nuestras.""",
    en = u"""Didn't mean to unsubscribe? <a href="%s">Click here</a> to 
re-subscribe and continue receiving emails from us."""
)

# SubscriptionForm
#------------------------------------------------------------------------------
translations.define("SubscriptionForm.name",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("SubscriptionForm.email",
    ca = u"Correu electrònic",
    es = u"Correo electrónico",
    en = u"E-mail address"
)

translations.define("SubscriptionForm.list",
    ca = u"Llista",
    es = u"Lista",
    en = u"List"
)

