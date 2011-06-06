import os
from docutils import nodes
from docutils.parsers.rst import directives, Directive
import glob
import re


class TocTreeDirective(Directive):
    has_content = True

    def run(self):
        self.assert_has_content()

        if ':nosubtitles:' in self.content:
            self.nosubtitles = True
        else:
            self.nosubtitles = False

        list_of_lines = self.create_links_to_titles(self.content)
        html_code = "\n".join(list_of_lines)

        text = '<div class="toctree">%s</div>' % html_code
        return [nodes.raw('', text, format='html')]

    def create_links_to_titles(self, items):
        "Genera una lista de links indicando los titulos de cada articulo"
        result = []
        result.append("<ul>")

        for i in items:

            if ':no' in i or not i:
                continue

            title, subtitles = self.get_title_and_subtitles(i)
            result.append(self.create_link_to(i, title))

            if subtitles and not self.nosubtitles:
                result.append("<ul>")

                for s in subtitles:
                    # Forma el nombre del sublink que rst2html genera
                    # con el mismo nombre del subtitulo pero quitando los
                    # espacios y reemplazando por guiones.
                    anchor = "%s#%s" %(i, s.replace(" ", "-"))
                    result.append(self.create_link_to(anchor, s))

                result.append("</ul>")

        result.append("</ul>")
        return result

    def create_link_to(self, i, title):
        return "<li><a href='%s'>%s</a></li>" %(i, title)

    def get_title_and_subtitles(self, filename):
        "Obtiene el texto del titulo y de todos los subtitulos que le siguen"
        basename = os.path.dirname(self.src)
        path_to_file = os.path.join(basename, filename)

        try:
            f = open(path_to_file, 'rt')
            content = f.read().decode('utf-8')
            f.close()
        except IOError:
            print "Error, no se encuentra el archivo '%s'" %(path_to_file)
            return ("<b>ERROR:</b> no file '%s'..." %(filename), "")

        # intenta buscar un nombre de capitulo.
        result = re.search(r"===*\n(.*)\n===*", content)

        if result:
            title = result.group(1)
            return (title, self.get_subtitles(content, title))

        # intenta buscar un nombre de titulo simple.
        result = re.search(r"(.*)\n===*", content)

        if result:
            title = result.group(1)
            return (title, self.get_subtitles(content, title))

        return ("<b>WARNING:</b> No title...", "")

    def get_subtitles(self, content , title):
        """Intenta obtener todos los subtitulos del contenido rst indicado.

        El argumento title corresponde al nombre del capitulo o titulo
        principal del texto."""

        # primero busca subtitulos marcados con signos ===
        items = re.findall(r"(.*)\n===*", content)

        # Si el titulo principal se encuenta en la busqueda lo elimina
        if title in items:
            items.remove(title)

        # Si no se encontraron subtitulos puede que esten marcados con ---
        if not items:
            items = re.findall(r"(.*)\n---*", content)

        # caso raro, que el titulo este marcado como subtitulo en cuyo caso
        # lo quita de la lista.
        if title in items:
            items.remove(title)

        return items

    def create_list_of_files(self, lines):
        """Genera una lista de archivos que se tienen que convertir a miniaturas.

        Generalmente la lista de archivos no requiere conversion, pero
        hay casos donde pueden existir comodines como '*' y en esos
        casos se tendrian que desplegar todos los archivos solicitados con
        este metodo."""

        new = []

        # filtra los archivos que no existen y despliega los patrones
        # de archivos tipo bash.
        for f in lines:

            if '*' in f:
                new.extend(glob.glob(DATA + f))
            elif os.path.exists(DATA + f):
                new.append(f)
            else:
                print "Cuidado, el archivo '%s' no se puede leer." %f

        return new


directives.register_directive("toctree", TocTreeDirective)
