# -*- encoding: utf-8-
# Copyright: Hugo Ruscitti <hugoruscitti@gmail.com>
# License: GPLv3

import time
from threading import Thread
import gtk


class DrawingThread(Thread):
    """Representa el componente del programa que dibuja los diagramas.

    Este componente actua de manera desacoplada por medio de un hilo, para
    no interferir en la interfaz de usuario gtk."""

    def __init__(self, main, queue):
        Thread.__init__(self)
        self.queue = queue
        self.main = main

    def run(self):

        while True:
            task = self.queue.get()        # agota la cola para quedarse 

            if task:
                task()
                self.queue.task_done()
            else:
                # se desbloquea el programa
                return
