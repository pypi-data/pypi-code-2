## Script (Python) "aviso_segunda_via"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from DateTime import DateTime
raise
response = context.REQUEST.response
response.setHeader('Content-Type', 'text/plain; charset=utf-8')

path = '/pycon/2010/sobre-o-evento/inscricoes'

pendentes = context.portal_catalog(path=path, portal_type='Inscricao',
                                   getPaga=False, sort_on='sortable_title')

for inscricao in pendentes:
    if inscricao.getTipo > '3' or inscricao.created > DateTime() -5:
        continue
    dados = {
        'nome': inscricao.Title,
        'email': inscricao.getEmail,
        'URL': inscricao.getURL(),
    }
    try:
        context.segunda_via(dados=dados)
        response.write('OK: %s\n' % dados['nome'])
    except:
        response.write('ERRO: %s %s\n' % (dados['URL'], dados['nome']))
