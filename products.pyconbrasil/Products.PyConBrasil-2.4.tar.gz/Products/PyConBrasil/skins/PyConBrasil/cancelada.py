## Script (Python) "cancelada"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
try:
    try:
        obs = context.getObservacoes()
    except:
        obs = ''
    linha = obs and obs.split('\n')[0] or ''
    value = linha.split(' ')[1] or False
    return value
except (IndexError, AttributeError):
    return False
