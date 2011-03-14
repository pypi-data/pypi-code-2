#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			September 2010
"""
from cocktail import schema
from woost.models.permission import Permission
from woost.models.messagestyles import permission_doesnt_match_style


class SendEmailPermission(Permission):
    """Permission to send an email."""

    instantiable = True

    roles = schema.Collection(
        items = schema.Reference(type = "woost.models.Role"),
        related_key = schema.Collection()
    )

    def match(self, role = None, verbose = False):

        if role and role not in self.roles:
            print permission_doesnt_match_style("Role doesn't match")
            return False

        return Permission.match(self, verbose)

    

