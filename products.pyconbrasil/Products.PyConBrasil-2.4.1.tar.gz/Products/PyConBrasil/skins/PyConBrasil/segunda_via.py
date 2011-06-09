## Script (Python) "segunda_via"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dados
##title=
##
template = context.template_segunda_via(context)

if not dados:
    dados = {
        'nome': context.getNome(),
        'email': context.getEmail(),
        'URL': context.absolute_url(),
    }

context.MailHost.send(template % dados)

return 'Enviado'
