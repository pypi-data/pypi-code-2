# -*- coding: utf-8 -*-
import re
from docutils import nodes
from docutils.parsers.rst import directives, Directive

import frontweb
from frontweb import utils
from frontweb import settings

DATA = settings.FRONTWEB_DATA

# Lista de palabras que no se deben detectar como tags.
NO_TAGS = ['.hg', '.git', 'los', 'all', 'sin', 'and', 'the', 'you', 'your', 'use', 'las', 'desde', 'con']
# Lista de palabras de menos de 3 caracteres que se deben tratar como tags.
SHORT_TAGS = ['vi', '3g']

class TagsDirective(Directive):
    "Permite a los usuarios colocar una nube de tags en cualquier pagina."
    has_content = True
    option_spec = {'min': directives.nonnegative_int}
    has_content = False


    def run(self):

        if 'min' in self.options:
            self.min_counter = self.options['min']
        else:
            self.min_counter = 2

        tags = self.get_tags()

        text = '<div class="tags">%s</div>' % tags
        return [nodes.raw('', text, format='html')]

    def get_tags(self):
        "Genera un string con todos los tags en distintos tamaños"
        tags = self._get_tags_as_dict()
        items = []

        fontmax = max(tags.values())

        for (word, counter) in tags.items():
            if counter > self.min_counter:
                fontsize = counter/float(fontmax)
                items.append("<a href='/find/%s'><span style='font-size: %fem'>%s</span></a>" %(word, 0.5 + fontsize, word))

        # retorna todos los items en formato string separados por espacios.
        items.sort()
        return " ".join(items)

    def _get_tags_as_dict(self):
        "Retorna un diccionario con tags y la cantidad de veces que aparece cada una."

        # Obtiene todos los archivos de texto del repositorio.
        files = utils.obtener_todos_los_archivos_de_texto(DATA)

        # Genera una lista de todas las palabras que aparecen en los nombres de archivos.
        words = []

        # por cada archivo intenta generar palablas para agregar en la lista `words`.
        for f in files:
            f = re.sub(DATA+"|\.rst|.txt", '', f)
            f = re.sub("/|-|\ ", '_', f)

            for w in f.split("_"):
                if len(w) > 2 and w not in SHORT_TAGS:
                    words.append(w)


        # Reduce la lista de palabras para dejar solamente las que puede llegar
        # a ser `tags` y elimina duplicados.
        bag_words = set(words) - set(NO_TAGS)
        tags = {}

        # Genera un diccionario donde la clave indica la palabra que representa
        # el tag y el valor es el indicador numerico de cuantas veces aparece.
        for b in bag_words:
            tags[b] = words.count(b)

        return tags


directives.register_directive("tags", TagsDirective)
