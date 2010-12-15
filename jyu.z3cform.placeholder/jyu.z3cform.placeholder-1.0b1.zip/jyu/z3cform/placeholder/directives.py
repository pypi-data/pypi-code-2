# -*- coding: utf-8 -*-
""" Grok directives and adapters for settings field placeholder """

import martian

from plone.directives.form.schema import FormMetadataDictStorage

from jyu.z3cform.placeholder.config import PLACEHOLDERS_KEY


class placeholder(martian.Directive):
    """Directive used to define placeholder for a field.
    """
    scope = martian.CLASS
    store = FormMetadataDictStorage()

    key = PLACEHOLDERS_KEY

    def factory(self, **kw):
        placeholders = {}
        for field_name, placeholder in kw.items():
            placeholders[field_name] = placeholder
        return placeholders
