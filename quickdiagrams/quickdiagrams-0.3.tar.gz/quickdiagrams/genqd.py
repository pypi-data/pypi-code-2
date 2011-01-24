"""
Arma una descripcion de las clases contenidas en un modulo,
su herencia, y sus metodos, en el formato que usa
QuickDiagrams http://code.google.com/p/quickdiagrams/

Uso:
    genqd [modulo] ... > output_file

Copyright (C) 2010 Gabriel A. Genellina
Licencia: GNU General Public License v3
"""

import os, sys
import pyclbr
import StringIO

INCLUIR_METODOS = True

def emitir(file_handler, cls, indent):
    file_handler.write('%s%s\n' % ('    ' * indent, cls.name))
    methods = [m for m in cls.methods if not m[0] == '_']
    if INCLUIR_METODOS and methods:
        for method in methods:
            file_handler.write('%s%s()\n' % ('    ' * (indent+1), method))
    else:
        file_handler.write('%s%s\n' % ('    ' * (indent+1), '_'))

    file_handler.write("\n")

def procesar_cls(file_handler, cls, clsdict, hm, indent=0):
    emitir(file_handler, cls, indent)
    base_name = cls.name
    # enumero las subclases *directas* de esta, que son las que
    # se muestran indentadas.
    # si hubiera herencia multiple se declara con -> mas adelante
    for name in clsdict.keys():
        subcls = clsdict.get(name)
        if not subcls:
            continue # se van borrando!
        if base_name in subcls.super:
            # guardar las "otras" bases, si hay
            for otra in subcls.super:
                if otra != base_name:
                    hm.append((subcls.name, otra))
            del clsdict[name]
            procesar_cls(file_handler, subcls, clsdict, hm, indent+1)

def procesar_modulo(file_handler, modulenames, path):
    # para guardar las declaraciones de herencia multiple pendientes: (derivada, base)
    hm = []
    #path, name = os.path.split(modname)

    clsdict = {}

    for modname in modulenames:
        if path:
            new_classes = pyclbr.readmodule(modname, [path])
        else:
            new_classes = pyclbr.readmodule(modname)

        clsdict.update(new_classes)

    clslist = clsdict.values()
    for cls in clslist:
        cls.super = sorted(s.name if hasattr(s, 'name') else s for s in cls.super)
    # las bases primero, queda mejor :)
    clslist.sort(key=lambda c:(len(c.super), c.super))
    for cls in clslist:
        if cls.name not in clsdict:
            continue
        procesar_cls(file_handler, cls, clsdict, hm)
        # herencia multiple pendiente
        # (trato de mostrarla tan pronto como sea posible)
        while hm:
            subcls, base = hm.pop(0)
            file_handler.write("%s -> %s\n" % (subcls, base))


def is_python_module_name(filename):
    path, name = os.path.split(filename)
    try:
        clsdict = pyclbr.readmodule(name, path)
    except ImportError:
        return False

    return True


def main():
    for name in sys.argv[1:]:
        procesar_modulo(name)
    return 0

if __name__ == '__main__':
    sys.exit(main())


def create_file_handler(name, path=None):
    "Simula un nuevo archivo para que lo lea quickdiagrams."

    if name.endswith('.py'):    # it's like a python filename
        name = name[:-3]

    items = name.rsplit('/', 1)

    if len(items) == 2:
        path, name = items
    else:
        name = items
        path = None

    new_file = StringIO.StringIO()
    procesar_modulo(new_file, name, path)

    new_file.flush()
    new_file.seek(0)
    return new_file
