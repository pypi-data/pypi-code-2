## Script (Python) "exportar_palestrantes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
path = '/pycon/2010/sobre-o-evento/inscricoes'

results = {}
                 
def compute(lista):
    for item in lista:
        if item.cancelada:
            continue
        results[item.getNome.strip()] = (item.getInstituicao.strip(), item.getCidade, item.getEstado)

compute(context.portal_catalog(path=path, portal_type='Treinamento', sort_on='ordenacao'))
compute(context.portal_catalog(path=path, portal_type='Palestra', sort_on='ordenacao'))

print '"Nome","Instituicao","Local"'
for nome, value in results.items():
    print '"%s","%s","%s/%s"' % (nome, value[0], value[1], value[2])

return printed
