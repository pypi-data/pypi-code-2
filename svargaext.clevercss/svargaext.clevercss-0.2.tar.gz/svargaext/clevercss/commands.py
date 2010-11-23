from svarga.utils.opster import command

from svargaext import clevercss

@command()
def clevercss_compile():
    '''Compile CleverCSS stylesheet sources to CSS
    '''
    clevercss.process()
