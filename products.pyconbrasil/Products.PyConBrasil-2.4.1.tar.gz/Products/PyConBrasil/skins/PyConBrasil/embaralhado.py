## Script (Python) "embaralhado"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=lista
##title=
##
from random import shuffle

results = list(lista)
shuffle(results)

return results
