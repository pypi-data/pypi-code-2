################################################################
# zopyx.smartprintng.lite
# (C) 2009,  ZOPYX Limited & Co. KG, D-72070 Tuebingen, Germany
################################################################

import os
import glob
import shutil
import tempfile
import urllib2
import BeautifulSoup

from compatible import InitializeClass
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile as ViewPageTemplateFile2

from zopyx.convert2 import Converter
from zopyx.smartprintng.lite.logger import LOG
from zopyx.smartprintng.lite.resources import resources_registry
from transformation import Transformer
from util import getLanguageForObject

cwd = os.path.dirname(os.path.abspath(__file__))


class PDFView(BrowserView):
    """ PDF view (using SmartPrintNG server) """

    template = ViewPageTemplateFile('resources/pdf_template.pt')
    resources = 'resources'

    # default transformations used for the default PDF view.
    # 'transformations' can be overriden within a derived PDFView.
    # If you don't need any transformation -> redefine 'transformations'
    # as empty list or tuple

    transformations = (
        'makeImagesLocal',
        )

    def copyResources(self, resources_dir, destdir):
        """ Copy over resources for a global or local resources directory into the 
            destination directory.
        """
        if os.path.exists(resources_dir):
            for name in os.listdir(resources_dir):
                fullname = os.path.join(resources_dir, name)
                if os.path.isfile(fullname):
                    shutil.copy(fullname, destdir)

    def transformHtml(self, html, destdir, transformations=None):
        """ Perform post-rendering HTML transformations """

        if transformations is None:
            transformations = self.transformations

        # the request can override transformations as well
        if self.request.has_key('transformations'):
            t_from_request = self.request['transformations']
            if isinstance(t_from_request, basestring):
                transformations = t_from_request and t_from_request.split(',') or []
            else:
                transformations = t_from_request

        T = Transformer(html, destdir, self.context)
        T(transformations)
        return T.render()

    def __call__(self, *args, **kw):

        try:
            return self.__call2__(*args, **kw)
        except:
            LOG.error('Conversion failed', exc_info=True)
            raise


    def __call2__(self, *args, **kw):
        """ URL parameters:
            'language' -  'de', 'en'....used to override the language of the
                          document
            'converter' - default to on the converters registered with
                          zopyx.convert2 (default: pdf-prince)
            'resource' - the name of a registered resource (directory)
            'template' - the name of a custom template name within the choosen
                         'resource' 
        """

        # Output directory
        destdir = tempfile.mkdtemp()

        # debug/logging
        params = kw.copy()
        params.update(self.request.form)
        LOG.debug('new job (%s, %s) - outdir: %s' % (args, params, destdir))

        # get hold of the language (hyphenation support)
        language = getLanguageForObject(self.context)
        if params.get('language'):
            language = params.get('language')

        # Check for CSS injection
        custom_css = None
        custom_stylesheet = params.get('custom_stylesheet')
        if custom_stylesheet:
            custom_css = str(self.context.restrictedTraverse(custom_stylesheet, None))
            if custom_css is None:
                raise ValueError('Could not access custom CSS at %s' % custom_stylesheet)

        # check for resource parameter
        resource = params.get('resource')
        if resource:
            resources_directory = resources_registry.get(resource)
            if not resources_directory:
                raise ValueError('No resource "%s" configured' % resource)
            if not os.path.exists(resources_directory):
                raise ValueError('Resource directory for resource "%s" does not exist' % resource)
            self.copyResources(resources_directory, destdir)

            # look up custom template in resources directory
            template_name = params.get('template', 'pdf_template')
            if not template_name.endswith('.pt'):
                template_name += '.pt'
            template_filename = os.path.join(resources_directory, template_name)
            if not os.path.exists(template_filename):
                raise IOError('No template found (%s)' % template_filename)
            template = ViewPageTemplateFile2(template_filename)

        else:
            template = self.template

        # call the dedicated @@asHTML on the top-level node. For a leaf document
        # this will return either a HTML fragment for a single document or @@asHTML
        # might be defined as an aggregator for a bunch of documents (e.g. if the
        # top-level is a folderish object

        html_fragment = ''
        html_view = self.context.restrictedTraverse('@@asHTML', None)
        if html_view:
            html_fragment = html_view()

        # arbitrary application data
        data = params.get('data', None)

        # Now render the complete HTML document
        html = template(self,
                        language=language,
                        request=self.request,
                        body=html_fragment,
                        custom_css=custom_css,
                        data=data,
                        )

        html = self.transformHtml(html, destdir)

        # hack to replace '&' with '&amp;'
        html = html.replace('& ', '&amp; ')

        # and store it in a dedicated working directory
        dest_filename = os.path.join(destdir, 'index.html')

        # inject BASE tag
        pos = html.lower().find('<head>')
        if pos == -1:
            raise RuntimeError('HTML does not contain a HEAD tag')
        html = html[:pos] + '<head><base href="%s"/>' % dest_filename + html[pos+6:]

        file(dest_filename, 'wb').write(html)

        # copy over global styles etc.
        resources_dir = os.path.join(cwd, 'resources')
        self.copyResources(resources_dir, destdir)

        # copy over language dependent hyphenation data
        if language:
            hyphen_file = os.path.join(resources_dir, 'hyphenation', language + '.hyp')
            if os.path.exists(hyphen_file):
                shutil.copy(hyphen_file, destdir)

            hyphen_css_file = os.path.join(resources_dir, 'languages', language + '.css')
            if os.path.exists(hyphen_css_file):
                shutil.copy(hyphen_css_file, destdir)

        # now copy over resources (of a derived view)
        self.copyResources(getattr(self, 'local_resources', ''), destdir)

        c = Converter(dest_filename)
        result = c(params.get('converter', 'pdf-fop'))
        if result['status'] != 0:
            raise RuntimeError('Error during PDF conversion (%r)' % result)
        pdf_file = result['output_filename']
        LOG.debug('Output file: %s' % pdf_file)
        return pdf_file

InitializeClass(PDFView)


class PDFDownloadView(PDFView):

    def __call__(self, *args, **kw):

        pdf_file = super(PDFDownloadView, self).__call__(*args, **kw)

        # return PDF over HTTP
        R = self.request.response
        R.setHeader('content-type', 'application/pdf')
        R.setHeader('content-disposition', 'attachment; filename="%s.pdf"' % self.context.getId())
        R.setHeader('content-length', os.stat(pdf_file)[6])
        R.setHeader('pragma', 'no-cache')
        R.setHeader('cache-control', 'no-cache')
        R.setHeader('Expires', 'Fri, 30 Oct 1998 14:19:41 GMT')
        R.setHeader('content-length', os.stat(pdf_file)[6])
        return file(pdf_file, 'rb').read()

InitializeClass(PDFDownloadView)

