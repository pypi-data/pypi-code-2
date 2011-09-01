import os
import glob
from docutils import nodes
from docutils.parsers.rst import directives, Directive

from frontweb import utils
from frontweb import settings

DATA = settings.FRONTWEB_DATA

# TODO: poner como argumento de la directiva, algo como :width: y/o :height:
SIZE = '250x150'

class GalleryDirective(Directive):
    has_content = True

    def run(self):
        self.assert_has_content()

        images = self.create_list_of_files(self.content)
        list_of_images = [self.create_html_tag_for(i) for i in images]
        html_code = "\n".join(list_of_images)

        # Si no hay imagenes para mostrar lo indica dentro del bloque gallery.
        if not html_code:
            html_code = "<< No content >>"

        return [nodes.raw('', "<div class='gallery'>" + html_code + "</div>", format='html')]

    def create_thumbs_directory(self):
        dirname = os.path.join(DATA, "thumbs")

        if not os.path.exists(dirname):
            os.mkdir(dirname)

    def create_list_of_files(self, lines):
        """Genera una lista de archivos que se tienen que convertir a miniaturas.

        Generalmente la lista de archivos no requiere conversion, pero
        hay casos donde pueden existir comodines como '*' y en esos
        casos se tendrian que desplegar todos los archivos solicitados con
        este metodo.

        Retorna una lista de todos los archivos pero sin el
        prefijo 'data'.
        """

        # Bugfix: obtiene la ruta de donde se quieren obtener las imagenes
        #         a partir del archivo rst actual.
        prefix = os.path.dirname(self.src) + "/"
        new = []
        # filtra los archivos que no existen y despliega los patrones
        # de archivos tipo bash.
        for f in lines:
            if '*' in f:
                path = prefix + f
                archivos_recolectados = glob.glob(path)

                if not archivos_recolectados:
                    print "Cuidado, no se pudo expandir '%s', los archivos no existen?" %path

                new.extend(archivos_recolectados)

            elif os.path.exists(prefix + f):
                new.append(prefix + f)
            else:
                print "Cuidado, el archivo '%s' no se puede leer." %f

        return [x.replace(DATA, "") for x in new]


    def create_html_tag_for(self, file_name):
        """Genera un elemento HTML para representa a la imagen.

        Se admite como argumento la ruta a una imagen completa, y
        si es necesario este metodo construye una miniatura
        en FRONTWEB_DATA/thumb.

        El retorno de este metodo es una etiqueta de tipo <a href... <img src...>
        para generar la previsualizacion de la miniatura y a la
        vez el link a la imagen.
        """

        if file_name.startswith('/'):
            file_name = file_name[1:]

        # Rutas fisicas a los archivos en disco.
        full_path = os.path.join(DATA, file_name)
        full_thumb_path = os.path.join(DATA, 'thumb', file_name)

        if not os.path.exists(full_thumb_path):
            self.create_thumb_directory_for_file(full_thumb_path)
            self.create_thumb(full_path, full_thumb_path)

        # Rutas para la web
        href = os.path.join(settings.FRONTWEB_URL, file_name)
        src = os.path.join(settings.FRONTWEB_URL, 'thumb', file_name)

        # Genera la miniatura para el archivo solicitado si este
        # no existe.

        return "<a href='%s'><img src='%s'/></a>" %(href, src)

    def create_thumb_directory_for_file(self, file_name):
        basedir = os.path.dirname(file_name)

        if not os.path.exists(basedir):
            os.makedirs(basedir)

    def create_thumb(self, image, out):
        command = ['convert']
        command.append(image)
        command.append('-thumbnail')
        command.append(SIZE)
        command.append('-unsharp')
        command.append('0x.5')
        command.append(out)
        retorno = utils.ejecutar_comando(command, cwd='./')

        if retorno:
            print retorno


directives.register_directive("gallery", GalleryDirective)
