## Script (Python) "exportar_participantes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
path = '/pycon/2010/sobre-o-evento/inscricoes'

results = []
                 
def compute(lista):
    for item in lista:
        if not item.getPaga:
            continue
        results.append('"%s","%s","%s","%s/%s","%s","%s"' % (item.Title.strip(), item.getEmail, item.getInstituicao.strip(), item.getCidade, item.getEstado,item.getPaga,item.getTipo))

compute(context.portal_catalog(path=path, portal_type='Inscricao', getPaga=True,sort_on='sortable_title'))

print '"Nome","Email","Instituicao","Local","Paga","Tipo"'
for line in results:
    print line


return printed
