""" Modulo creado a traves del fantastico libro Head First Python, de O'Reilly. Incluye
la funcion print_lol(), diseñada para imprimir en pantalla los elementos de una lista."""
def print_lol(la_lista, nivel):
    """ La funcion print_lol recibe como parametro una lista y la muestra en pantalla,
    detectando si hay listas anidadas dentro de esta, y mostrando sus elementos de igual
    modo, uno en cada linea. Ademas recibe un segundo parametro que indica el nivel de
    anidamiento para tabular al presentar la lista."""
    for cada_elemento in la_lista:
        if isinstance(cada_elemento, list):
            print_lol(cada_elemento, nivel+1)
        else:
            for tab_stop in range(nivel):
                print("\t",end='')
            print(cada_elemento)
