## Script (Python) "enviar_email_feedback"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
response = context.REQUEST.response
response.setHeader('Content-Type', 'text/plain; charset=utf-8')

# remove
raise 'foo', 'bar'

results = {}
path = '/pycon/2009/sobre-o-evento/inscricoes'
                 
treinamentos = context.portal_catalog(path=path, portal_type='Treinamento')
palestras = context.portal_catalog(path=path, portal_type='Palestra')
inscricoes = context.portal_catalog(path=path, portal_type='Inscricao')

for tipo in treinamentos, palestras, inscricoes:
    for item in tipo:
        results[item.getEmail] = item.Title

for email, nome in results.items():
    dados = {
        'nome': nome,
        'primeiro': nome.split()[0],
        'email': email,
    }
    try:
        template = context.template_feedback(context)
        context.MailHost.send(template % dados)
        response.write('OK: %s\n' % email)
    except:
        response.write('ERRO: %s\n' % email)
