""" Modulo creado a traves del fantastico libro Head First Python, de O'Reilly. Incluye
la funcion print_lol(), diseñada para imprimir en pantalla los elementos de una lista."""
def print_lol(la_lista, tabulacion=False, nivel=0):
    """ La funcion print_lol recibe como parametro una lista y la muestra en pantalla,
    detectando si hay listas anidadas dentro de esta, y mostrando sus elementos de igual
    modo, uno en cada linea.
    
    Hay un segundo parametro que indica si se quiere tabulacion. En caso de quererse la
    funcion va tabulando conforme encuentra listas anidadas en la lista principal. De no
    quererse no se muestra tabulacion y salen todos los elementos en la misma columna.
    
    Ademas puede recibir un tercer parametro que indica el nivel de
    anidamiento para tabular al presentar la lista. Se puede usar un entero positivo para
    empezar a tabular a cierto nivel, o un valor negativo para anular el tabulamiento y +
    mostrar todos los elementos en una columna sin importar el anidamiento."""
    for cada_elemento in la_lista:
        if isinstance(cada_elemento, list):
            print_lol(cada_elemento, tabulacion, nivel+1)
        else:
            if tabulacion:
                for tab_stop in range(nivel):
                    print("\t",end='')
            print(cada_elemento)
