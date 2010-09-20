# -*- encoding: utf-8 -*-
# Pilas engine - A video game framework.
#
# Copyright 2010 - Hugo Ruscitti
# License: LGPLv3 (see http://www.gnu.org/licenses/lgpl.html)
#
# Website - http://www.pilas-engine.com.ar

import pilas
from PySFML import sf

import os

class Sonido:

    def __init__(self, buffer):
        self.buffer = buffer
        self.sonido = sf.Sound(buffer)
        pass

    def reproducir(self):
        self.sonido.Play()
    
    def Play(self):
        self.reproducir()

def cargar(ruta):
    """Carga un sonido para reproducir, donde el argumento ``ruta`` indica cual es el archivo.

    Por ejemplo::

        import pilas

        risa = pilas.sonidos.cargar("risa.ogg")

    En caso de éxito retorna el objeto Sound, que se puede
    reproducir usando el método ``Play()``, por ejemplo::

        risa.Play()

    El directorio de búsqueda del sonido sigue el siguiente orden:

        * primero busca en el directorio actual.
        * luego en 'data'.
        * por último en el directorio estándar de la biblioteca.

    En caso de error genera una excepción de tipo IOError.
    """
    path = pilas.utils.obtener_ruta_al_recurso(ruta)

    buff = sf.SoundBuffer()
    buff.LoadFromFile(path)
    return Sonido(buff)
