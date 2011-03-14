#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
import os
from shutil import rmtree
from tempfile import mkdtemp
from subprocess import Popen
import cherrypy
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail import schema
from cocktail.controllers import serve_file
from cocktail.controllers.location import Location
from woost.models import Extension
from woost.controllers import BaseCMSController


translations.define("PDFExtension",
    ca = u"Exportació de documents PDF",
    es = u"Exportación de documentos PDF",
    en = u"PDF rendering"
)

translations.define("PDFExtension-plural",
    ca = u"Exportació de documents PDF",
    es = u"Exportación de documentos PDF",
    en = u"PDF rendering"
)

translations.define("PDFExtension.command",
    ca = u"Comanda",
    es = u"Comando",
    en = u"Command"
)


class PDFExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"Permet publicar pàgines HTML en format PDF.",
            "ca"
        )
        self.set("description",            
            u"Permite publicar páginas HTML en formato PDF.",
            "es"
        )
        self.set("description",
            u"Publishes HTML pages as PDF documents.",
            "en"
        )

    command = schema.String(
        required = True,
        default = u"python -m woost.extensions.pdf.renderpdf "
                  u"%(url)s %(output_file)s",
        text_search = False
    )

    @event_handler
    def handle_loading(cls, event):

        extension = event.source

        def render_pdf(self):

            # Create a temporary folder to hold the PDF
            temp_path = mkdtemp()
            pdf_file_path = os.path.join(temp_path, "file.pdf")

            try:
                location = Location.get_current(relative = False)
                location.query_string["format"] = "html"

                # Create the file
                command = extension.command % {
                    "url": unicode(location),
                    "output_file": pdf_file_path
                }
                proc = Popen(command.encode("utf-8"), shell = True)
                stdout, stderr = proc.communicate()

                if proc.returncode:
                    raise OSError("Error generating PDF"
                        + (": " + stderr) if stderr else ""
                    )
 
                # Serve the file
                cherrypy.response.headers["Content-Type"] = "application/x-pdf"

                return serve_file(
                    pdf_file_path,
                    content_type = "application/x-pdf",
                    disposition = "attachment",
                    name = translations(self.context["publishable"]) + ".pdf"
                )

            finally:
                rmtree(temp_path)
        
        BaseCMSController.render_pdf = render_pdf    
        BaseCMSController.allowed_rendering_formats = frozenset(
            list(BaseCMSController.allowed_rendering_formats)
          + ["pdf"]
        )

