## Script (Python) "participantes.csv"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain;; charset=utf-8')
path = '/'.join(context.getPhysicalPath())
brains = context.portal_catalog(path=path,
#                                portal_type='Inscricao',
                                review_state=['registrado','aprovado'],
                                sort_on='sortable_title')

for brain in brains:
  o = brain.getObject()
  id = o.getId()
  nome = o.getNome()
  try:
    sexo = o.getSexo()
  except:
    sexo = ''
  email = o.getEmail()
  try:
    cidade = o.getCidade()
  except:
    cidade = ''
  try:
    estado = o.getEstado()
  except:
    estado = ''
  instituicao = o.getInstituicao()
  try:
    paga = (o.getPaga() and "Paga") or "Pendente"
  except:
    paga = 'Paga'
  tipo = o.portal_type
  print '''"%s","%s","%s","%s","%s","%s","%s","%s"''' % (nome, tipo, sexo, email, cidade, estado, instituicao, paga)

return printed
