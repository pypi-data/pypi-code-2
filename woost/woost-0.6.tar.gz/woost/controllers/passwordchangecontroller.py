#-*- coding: utf-8 -*-
u"""Defines the `PasswordChangeController` class.

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
import hashlib
import cherrypy
from cocktail import schema
from cocktail.modeling import cached_getter
from cocktail.schema.exceptions import ValidationError
from cocktail.controllers.location import Location
from cocktail.controllers.parameters import get_parameter
from cocktail.controllers.formcontrollermixin import FormControllerMixin
from woost.models.emailtemplate import EmailTemplate
from woost.models import User, StandardPage, Site
from woost.controllers.documentcontroller import DocumentController

class UserIdentifierNotRegisteredError(ValidationError):
    pass

def generate_confirmation_hash(email):
    hash = hashlib.sha1()
    hash.update(email)
    hash.update(Site.main.secret_key)
    return hash.hexdigest()

class PasswordChangeController(FormControllerMixin, DocumentController):

    def __init__(self, *args, **kwargs):
        DocumentController.__init__(self, *args, **kwargs)
        FormControllerMixin.__init__(self)

    class_view = "woost.views.PasswordChangeRequestTemplate"

    @cached_getter
    def user_instance(self):
        # Try to get user instance with received email parameter
        if self.form_data and self.form_data["email"]:
            return User.get_instance(
                email = self.form_data["email"]
            )

    @cached_getter
    def form_model(self):

        form_model = schema.Schema(u"PasswordChangeRequestForm")

        #To validate if user identifier exists on database
        def validate_user_identifier_exists(member, value, context):
            if value and self.user_instance is None:
                yield UserIdentifierNotRegisteredError(member, value, context)

        # Copy user identifier member
        email_member = User.email.copy()

        email_member.add_validation(validate_user_identifier_exists)
        form_model.add_member(email_member)
        return form_model

    @cached_getter
    def submitted(self):
        return cherrypy.request.method == "POST"

    def submit(self):
        confirmation_email_template = EmailTemplate.get_instance(
            qname="woost.views.password_change_confirmation_email_template"
        )
        if confirmation_email_template:
            confirmation_email_template.send({
                "user": self.user_instance,
                "confirmation_url": self.confirmation_url
            })

    @cached_getter
    def confirmation_url(self):
        publishable = self.context["publishable"]
        target_page = StandardPage.get_instance(
            qname = 'woost.password_change_confirmation_page'
        )
        confirmation_target = self.context["cms"].uri(target_page)
        location = Location.get_current(relative=False)
        location.path_info = confirmation_target
        location.query_string = {
            "email": self.user_instance.email,
            "hash": generate_confirmation_hash(self.user_instance.email)
        }
        return str(location)
