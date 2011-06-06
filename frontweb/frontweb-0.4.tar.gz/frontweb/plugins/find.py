from yapsy.IPlugin import IPlugin

from frontweb import settings, utils

DATA = settings.FRONTWEB_DATA


class Find(IPlugin):
    name = "find"

    def run(self, request, url):
        files = utils.obtener_todos_los_archivos_de_texto(DATA)

        parametro_get = request.GET.get('query', None)

        # Busca los parametros para filtrar en los parametros
        # get (si existen), o los toma directamente de la URL.
        if parametro_get:
            expresion = parametro_get
        else:
            # Si no llega la busqueda por el parametro
            # get, busca los argumentos en la misma url.
            expresion = url

        resultado = utils.filtrar_lista_por_expresion_regular(expresion, files)

        if resultado:
            resultado = self._convertir_a_lista_html(resultado)
            return utils.mostrar_pagina("<h1>Resultado de busqueda para: %s</h1> %s" %(expresion, resultado), 'find')
        else:
            return utils.mostrar_pagina("No hay paginas que contengan <strong>%s</strong> en su titulo." %(expresion), "find")

    def _convertir_a_lista_html(self, lista):
        "Toma una lista de python y retorna un string con el codigo de una lista HTML."

        nombres_sin_prefijo = [x.replace(DATA+'/', '').replace('.rst', '').replace('.txt', '') for x in lista]
        lista_de_enlaces = ["<li><a href='/%s'>%s</a></li>" %(x, x) for x in nombres_sin_prefijo]
        return '<ul>' + '\n'.join(lista_de_enlaces) + '</ul>'
