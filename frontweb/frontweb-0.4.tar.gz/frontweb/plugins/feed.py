# -*- encoding: utf-8- -*-
from datetime import datetime
from yapsy.IPlugin import IPlugin

from django.utils import feedgenerator
from django.http import HttpResponse

from frontweb import settings, utils, html, conversor

DATA = settings.FRONTWEB_DATA


class Feed(IPlugin):
    name = "feed"

    def run(self, request, url):

        nombre = settings.FRONTWEB_SITE_NAME
        url_base = settings.FRONTWEB_URL
        descripcion = settings.FRONTWEB_DESCRIPCION
        autor =  settings.FRONTWEB_AUTHOR
        idioma = 'en'

        feed = feedgenerator.Atom1Feed(
                title=nombre,
                link=url_base,
                description=descripcion,
                language=idioma,
                author_name=autor,
                feed_url=url,
        )

        # Obtiene los filtros para retornar solo los articulos solicitados.
        parametros = url.split('/', 1)

        if len(parametros) > 1:
            filtro = parametros[1]
        else:
            filtro = ''

        self._recolectar_y_publicar_articulos(feed, filtro)
        response = HttpResponse(mimetype='application/xml')
        feed.write(response, 'utf-8')
        return response

    def _recolectar_y_publicar_articulos(self, feed, filtro):
        archivos = utils.obtener_todos_los_archivos_de_texto_con_fecha(DATA)
        archivos = utils.filtrar_lista_por_expresion_regular(filtro, archivos)
        url = settings.FRONTWEB_URL

        for archivo in archivos:
            contenido = conversor.convertir_archivo_en_html(archivo)
            titulo = html.obtener_titulo_principal_del_cuerpo(contenido, "Sin titulo")
            fecha = utils.obtener_fecha_del_archivo(archivo)
            url_al_archivo = url + '/' + archivo
            url_al_archivo = url_al_archivo.replace(DATA, "")

            feed.add_item(title=titulo,
                    link=url_al_archivo,
                    pubdate=fecha,
                    description=contenido)
