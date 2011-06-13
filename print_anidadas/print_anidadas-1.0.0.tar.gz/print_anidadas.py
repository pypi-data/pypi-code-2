""" Modulo creado a traves del fantastico libro Head First Python, de O'Reilly. Incluye
la funcion print_lol(), diseñada para imprimir en pantalla los elementos de una lista."""
def print_lol(the_list):
    """ La funcion print_lol recibe como parametro una lista y la muestra en pantalla,
    detectando si hay listas anidadas dentro de esta, y mostrando sus elementos de igual
    modo, uno en cada linea. """
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
