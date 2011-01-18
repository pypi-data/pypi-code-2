# Copyright (C) 2011 Luci Stanescu <luci@cnix.ro>. See debian/copyright for details.
#

"""
Templating support.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = ['TemplateManager', 'TemplateResponse']

import os

from genshi.core import Markup, PI
from genshi.template import MarkupTemplate, TemplateLoader

from authenticity.configuration import Boolean, Configuration, GenshiOutputType, List, Option, Section
from authenticity.http import Response


class GeneralSection(Section):
    __section__ = 'General'
    public_directories = Option(type=List(unicode), default=[], nillable=True)


class TemplateConfiguration(Configuration):
    general = GeneralSection


class TemplateManager(TemplateLoader):
    """
    The TemplateManager is responsible for reading the template configuration
    and loading individual templates.
    """
    def __init__(self, configuration, logger):
        """
        Initialize a TemplateManager using the specified configuration.
        """
        templates_directory = os.path.join(configuration.general.data_path, configuration.general.templates_directory)
        self.directory = os.path.join(templates_directory, configuration.general.template)
        super(TemplateManager, self).__init__(self.directory, auto_reload=True)
        try:
            file = open(os.path.join(self.directory, 'template.ini'))
        except (IOError, OSError):
            file = None
        self.configuration = TemplateConfiguration.read(file, dict(), logger)
        self.logger = logger


class ConfigurationFilter(object):
    """
    A stream filter which catches the processing instructions with a name that
    starts with "authenticity." and saves the output of the known options on
    itself.
    """

    __options__ = ['output_type', 'content_type', 'xml_declaration']

    output_type     = Option(type=GenshiOutputType, default='xhtml', nillable=False)
    content_type    = Option(type=unicode, default='application/xhtml+xml', nillable=False)
    xml_declaration = Option(type=Boolean, default=False, nillable=False)

    def __init__(self, logger):
        self.logger = logger

    def __call__(self, stream):
        for type, data, pos in stream:
            if type is PI and data[0].startswith('authenticity.'):
                option = data[0][len('authenticity.'):].replace('-', '_')
                if option in self.__options__:
                    try:
                        setattr(self, option, data[1])
                    except ValueError, e:
                        self.logger.warn('Illegal value for processing instruction %s in template: %s.', data[0], e)
                else:
                    self.logger.warn('Unknown processing instruction %s in template.', data[0])
            else:
                yield (type, data, pos)


class TemplateResponse(Response):
    """
    An HTTP response built from a template.
    """
    def __init__(self, template, status, request, context, headers=None, head_elements='', data={}):
        """
        Initializes the HTTP response using the template identified by name,
        and the request, context and data provided.
        """
        if not isinstance(template, MarkupTemplate):
            template = context.template_manager.load(template)
        head_elements = Markup(head_elements)
        filter = ConfigurationFilter(context.logger)
        # The lambda filter is required to force the processing of the other filter
        stream = template.generate(request=request, context=context, head_elements=head_elements, **data) \
                 | filter \
                 | (lambda stream: list(stream))
        options = dict(drop_xml_decl=not filter.xml_declaration) if filter.output_type=='xhtml' else dict()
        body = stream.render(filter.output_type, **options) + '\n'
        super(TemplateResponse, self).__init__(status,
                                               headers=headers,
                                               content_type=filter.content_type+';charset=UTF-8',
                                               body=body)


