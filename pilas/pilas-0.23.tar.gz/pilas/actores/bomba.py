# -*- encoding: utf-8 -*-
# Pilas engine - A video game framework.
#
# Copyright 2010 - Hugo Ruscitti
# License: LGPLv3 (see http://www.gnu.org/licenses/lgpl.html)
#
# Website - http://www.pilas-engine.com.ar

import pilas
from pilas.actores import Animacion
from pilas.actores import Explosion

class Bomba(Animacion):
    "Representa una explosion para una bomba, dinamita etc..."

    def __init__(self):
        Animacion.__init__(self, pilas.imagenes.Grilla("bomba.png", 2), ciclica=True)

    def explotar(self):
        explosion = Explosion()
        explosion.x = self.x
        explosion.y = self.y
        explosion.escala = self.escala * 2

        self.eliminar()
