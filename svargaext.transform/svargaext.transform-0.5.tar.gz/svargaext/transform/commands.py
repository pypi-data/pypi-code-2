from opster import command

from svargaext import transform

@command()
def transform_compile():
    '''Transform declared sources to according destinations
    '''
    transform.process()
