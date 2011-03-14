#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""

import random
import string
from cocktail import schema
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail.persistence import datastore
from woost.models import (
    Controller,
    Document,
    EmailTemplate,
    Extension,
    StandardPage,
    Template,
    User
)

translations.define("SignUpExtension",
    ca = u"Alta d'usuaris",
    es = u"Alta de usuarios",
    en = u"Sign Up"
)

translations.define("SignUpExtension-plural",
    ca = u"Altas d'usuaris",
    es = u"Altas de usuarios",
    en = u"Signs Up"
)

class SignUpExtension(Extension):

    # To indicate if the extension was loaded at least one time
    # will be set to True at the end of the first load
    initialized = False

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet als usuaris registrar-se autònomament en el lloc web""",
            "ca"
        )
        self.set("description",            
            u"""Permite a los usuarios registrarse por si mismos en el sitio""",
            "es"
        )
        self.set("description",
            u"""Allows users to register themselves on the site""",
            "en"
        )
        self.secret_key = self._generate_secret_key()

    def _generate_secret_key(self):
        secret_key = ''
        for i in range(0,8):
            secret_key = secret_key + \
                random.choice(
                    string.letters + string.digits
                )
        return secret_key

    @event_handler
    def handle_loading(cls, event):
        
        from woost.extensions.signup.signuppage import SignUpPage
        from woost.extensions.signup.signupcontroller import SignUpController
        from woost.extensions.signup import strings

        extension = event.source

        # Extend User model
        if not hasattr(User, "confirmed_email"):
            User.add_member(
                schema.Boolean(
                    "confirmed_email",
                    default = False,
                    Required = True
                )
            )

        # Make sure the sign up controller exists
        signup_controller = Controller.get_instance(
            qname = u"woost.extensions.signup.signup_controller"
        )
        
        if signup_controller is None:
            signup_controller = Controller()
            signup_controller.python_name = u"woost.extensions.signup.signupcontroller.SignUpController"
            signup_controller.qname = u"woost.extensions.signup.signup_controller"
            signup_controller.set("title", u"Sign Up controller", "en")
            signup_controller.set("title", u"Controlador de alta de usuarios", "es")
            signup_controller.set("title", u"Controlador d'alta d'usuaris", "ca")
            signup_controller.insert()

        # Make sure the sign up confirmation controller exists
        signup_confirmation_controller = Controller.get_instance(
            qname = u"woost.extensions.signup.signup_confirmation_controller"
        )
        
        if signup_confirmation_controller is None:
            signup_confirmation_controller = Controller()
            signup_confirmation_controller.python_name = u"woost.extensions.signup.signupconfirmationcontroller.SignUpConfirmationController"
            signup_confirmation_controller.qname = u"woost.extensions.signup.signup_confirmation_controller"
            signup_confirmation_controller.set("title", u"Sign Up confirmation controller", "en")
            signup_confirmation_controller.set("title", u"Controlador de confirmación alta de usuarios", "es")
            signup_confirmation_controller.set("title", u"Controlador de confirmació d'alta d'usuaris", "ca")
            signup_confirmation_controller.insert()

        # Make sure the sign up template exists
        signup_view = Template.get_instance(
            qname = u"woost.extensions.signup.signup_template"
        )

        if signup_view is None:
            signup_view = Template()
            signup_view.identifier = u"woost.extensions.signup.SignUpView"
            signup_view.engine = u"cocktail"
            signup_view.qname = u"woost.extensions.signup.signup_template"
            signup_view.set("title", u"Sign up view", "en")
            signup_view.set("title", u"Plantilla de alta de usuarios", "es")
            signup_view.set("title", u"Plantilla d'alta d'usuaris", "ca")
            signup_view.insert()

        # Make sure the sign up confirmation template exists
        signup_confirmation_view = Template.get_instance(
            qname = u"woost.extensions.signup.signup_confirmation_template"
        )

        if signup_confirmation_view is None:
            signup_confirmation_view = Template()
            signup_confirmation_view.identifier = u"woost.extensions.signup.SignUpConfirmationView"
            signup_confirmation_view.engine = u"cocktail"
            signup_confirmation_view.qname = u"woost.extensions.signup.signup_confirmation_template"
            signup_confirmation_view.set("title", u"Sign up confirmation template", "en")
            signup_confirmation_view.set("title", u"Plantilla de confirmación de alta de usuarios", "es")
            signup_confirmation_view.set("title", u"Plantilla de confirmació d'alta d'usuaris", "ca")
            signup_confirmation_view.insert()

        # Make sure the default confirmation email template exists
        confirmation_email_template = EmailTemplate.get_instance(
            qname = u"woost.extensions.signup.signup_confirmation_email_template"
        )
        
        if confirmation_email_template is None:
            confirmation_email_template = EmailTemplate()
            confirmation_email_template.python_name = u"woost.extensions.signup.signupconfirmationemailtemplate.SignUpConfirmationEmailTemplate"
            confirmation_email_template.qname = u"woost.extensions.signup.signup_confirmation_email_template"
            # title
            confirmation_email_template.set("title", u"Sign Up Confirmation email template ", "en")
            confirmation_email_template.set("title", u"Plantilla de email de confirmación de alta de usuario", "es")
            confirmation_email_template.set("title", u"Plantilla de correu electrònic de confirmació d'alta d'usuari", "ca")
            # subject
            confirmation_email_template.set("subject", u"User account confirmation", "en")
            confirmation_email_template.set("subject", u"Confirmación de cuenta de usuario", "es")
            confirmation_email_template.set("subject", u"Confirmació de compte d'usuari", "ca")
            # template engine
            confirmation_email_template.template_engine = u"mako"
            # body
            confirmation_email_template.set("body", u"""
                Hello ${user.email}. Click here to confirm your email account.
                <br/> <a href='${confirmation_url}'>${confirmation_url}</a>
            """, "en")
            confirmation_email_template.set("body", u"""
                Hola ${user.email}. Haz clic para confirmar tu cuenta de usuario.
                <br/> <a href='${confirmation_url}'>${confirmation_url}</a>
            """, "es")
            confirmation_email_template.set("body", u"""
                Hola ${user.email}. Fes clic per confirmar el teu compte d'usuari.
                <br/> <a href='${confirmation_url}'>${confirmation_url}</a>
            """, "ca")
            # sender
            admin = User.get_instance(qname="woost.administrator")
            confirmation_email_template.set("sender", admin.email)
            # receivers
            confirmation_email_template.set("receivers", u"[user.email]")

            confirmation_email_template.insert()

        # Make sure the default confirmation target exists
        confirmation_target = StandardPage.get_instance(
            qname = u"woost.extensions.signup.signup_confirmation_target"
        )
        
        if confirmation_target is None and not extension.initialized:
            confirmation_target = StandardPage()
            confirmation_target.qname = u"woost.extensions.signup.signup_confirmation_target"
            # title
            confirmation_target.set("title", u"Sign Up Confirmation Page", "en")
            confirmation_target.set("title", u"Confirmación de alta de usuario", "es")
            confirmation_target.set("title", u"Confirmació d'alta d'usuari", "ca")
            # Controller
            confirmation_target.controller = signup_confirmation_controller
            confirmation_target.template = signup_confirmation_view
            # parent
#            confirmation_target.parent = Document.get_instance(qname="woost.home")
            # hidden
            confirmation_target.hidden = True

            confirmation_target.insert()

        # Make sure the default signup page exists
        signup_page = SignUpPage.get_instance(
            qname = u"woost.extensions.signup.signup_page"
        )
        
        if signup_page is None and not extension.initialized:
            signup_page = SignUpPage()
            signup_page.qname = u"woost.extensions.signup.signup_page"
            # title
            signup_page.set("title", u"Sign Up", "en")
            signup_page.set("title", u"Registro de usuario", "es")
            signup_page.set("title", u"Registre d'usuari", "ca")
            # User type
            signup_page.user_type = User
            # confirmation target
            signup_page.confirmation_target = confirmation_target
            # parent
            signup_page.parent = Document.get_instance(qname="woost.home")
            # children
            signup_page.children.append(confirmation_target)

            signup_page.insert()

        extension.initialized = True

        datastore.commit()

