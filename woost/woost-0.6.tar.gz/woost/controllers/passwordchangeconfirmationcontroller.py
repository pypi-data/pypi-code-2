#-*- coding: utf-8 -*-
u"""Defines the `PasswordChangeConfirmationController` class.

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
import cherrypy
from cocktail import schema
from cocktail.events import event_handler
from cocktail.modeling import cached_getter
from cocktail.persistence import datastore
from cocktail.controllers.parameters import get_parameter
from cocktail.controllers.formcontrollermixin import FormControllerMixin
from woost.models.user import User
from woost.controllers.backoffice.usereditnode import PasswordConfirmationError
from woost.controllers.documentcontroller import DocumentController
from woost.controllers.passwordchangecontroller import generate_confirmation_hash
from woost.controllers.authentication import AuthenticationFailedError


class PasswordChangeConfirmationController(FormControllerMixin, DocumentController):

    class_view = "woost.views.PasswordChangeFormTemplate"

    @cached_getter
    def email(self):
        return cherrypy.request.params["email"]

    @cached_getter
    def hash(self):
        return cherrypy.request.params["hash"]

    @cached_getter
    def form_model(self):

        form_model = schema.Schema(u"PasswordChangeConfirmationForm")

        # A copy of user password member
        password_member = User.password.copy()
        form_model.add_member(password_member)

        # Password confirmation member
        password_confirmation_member = schema.String(
            name = "password_confirmation",
            edit_control = "cocktail.html.PasswordBox",
            required = password_member
        )

        # Add validation to compare password_confirmation and
        # password fields
        @password_confirmation_member.add_validation
        def validate_password_confirmation(member, value, ctx):
            password = ctx.get_value("password")
            password_confirmation = value

            if password and password_confirmation \
            and password != password_confirmation:
                yield PasswordConfirmationError(
                        member, value, ctx)

        form_model.add_member(password_confirmation_member)

        return form_model

    @event_handler
    def handle_traversed(cls, e):
        
        # Verify the received hash code
        controller = e.source

        if generate_confirmation_hash(controller.email) != controller.hash:
            raise ValueError("Wrong email hash")

    @cached_getter
    def submitted(self):
        return cherrypy.request.method == "POST"

    def submit(self):
        user = User.get_instance(email = self.email)
        user.password = self.form_data['password']
        self.context["cms"].authentication.set_user_session(user) # Auto-login
        datastore.commit()

    @cached_getter
    def output(self):
        output = DocumentController.output(self)
        output["email"] = self.email
        output["hash"] = self.hash
        return output

