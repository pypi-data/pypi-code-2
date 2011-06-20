from distutils.core import setup

setup(
    name         = 'print_anidadas',
    version      = '1.4.1',
    py_modules   = ['print_anidadas'],
    author       = 'Rotura',
    author_email = 'rknxtra@gmail.com',
    url          = 'http://lavidaeslagomas.blogspot.com',
    description  = '''Un sencillo listador de listas anidadas. Tiene la capacidad de tabular
    en cada nivel de anidamiento para mostrar mejor los elementos y distinguir en que nivel se
    encuentran. Ademas es capaz de recibir como parametro la salida donde se quiere imprimir
    el resultado, pudiendo utilizarse para volcar listas en archivos de datos en un formato
    legible y limpio.'''
    )
