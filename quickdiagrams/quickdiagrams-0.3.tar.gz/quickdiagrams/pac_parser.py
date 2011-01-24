# -*- coding: utf-8 -*-
import re
import StringIO

# Licencia: GPLv3
# Author: Pablo Codeiro
# Cambios de hugoruscitti: que simule crear un archivo .sc y la función
#                          'get_fakefile' que se llama desde quickdiagrams.
#
# por supuesto, aqui iria el autor, la fecha, la version
# que es GPL v3.0 y todas esas chorradas....

def esUnMensaje (unaLinea):
    elementos = re.match("!(\w+) categoriesFor: #(\w+)!  public! !",unaLinea)
    
    if elementos:
        return (elementos.group(1), elementos.group(2))

def esUnaClase (unaLinea):
    elementos = re.match("\s+add: #(\w+);", unaLinea)

    if elementos:
        return (elementos.group(1))


def esUnaRelacion (unaLinea):
    #elementos = re.match("\s+\w+\s*:=\s*(\w+)\s*new\s* \.",unaLinea)
    elementos = re.match(".+:=\s+(\w+)\s*new\s*\..*",unaLinea)

    if elementos:
        return (elementos.group(1))





def get_fakefile(input_filename):
    "Simula un archivo de disco, para realizar la conversion .pac -> .sc"

    new_file = StringIO.StringIO()
    last_file = open(input_filename, 'r')

    dict = {}
    claseActual = ""

    for linea in last_file.readlines():
        tmp_clase_actual = (re.match("!(\w+) methodsFor!", linea))

        if tmp_clase_actual:
            claseActual = tmp_clase_actual.group(1)

        clase = esUnaClase(linea)
        mens = esUnMensaje(linea)
        relacion = esUnaRelacion(linea)

        if clase:
            if len(dict) == 1:
                dict[clase] = clase
            elif not dict.has_key(clase):
                dict[clase] = clase

            claseActual = clase

        if mens:
            (clase2,mensaje) = mens
            dict[clase2] = dict[clase2] + "\n\t" + mensaje + "()"
            claseActual = clase

        if relacion:
            new_file.write("%s <>- %s\n" %(claseActual, relacion))

    for elemento in dict.values():
        new_file.write(elemento + "\n");

    last_file.close()

    new_file.flush()
    new_file.seek(0)

    import pprint
    pprint.pprint(new_file.readlines())

    return new_file
