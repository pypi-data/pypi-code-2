"""
amonymize_data command
"""
from __future__ import with_statement

import sys
import os.path

from django.db.models.loading import get_models
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import AppCommand, CommandError
from django.utils import importlib

from anonymizer import Anonymizer
from anonymizer import introspect

class Command(AppCommand):

    def handle_app(self, app, **options):

        anonymizers_module_parent = ".".join(app.__name__.split(".")[:-1])
        mod = importlib.import_module(anonymizers_module_parent)

        parent, discard = os.path.split(mod.__file__)  # lop off __init__.pyc
        path = os.path.join(parent, 'anonymizers.py') # and add anonymizers.

        if os.path.exists(path):
            raise CommandError("File '%s' already exists." % path)

        model_names = []
        imports = []
        output = []
        output.append("")
        imports.append("from anonymizer import Anonymizer")
        for model in get_models(app):
            model_names.append(model.__name__)
            output.append(introspect.create_anonymizer(model))

        imports.insert(0, "from %s import %s" % (app.__name__, ", ".join(model_names)))

        with open(path, "w") as fd:
            fd.write("\n".join(imports) + "\n".join(output))
