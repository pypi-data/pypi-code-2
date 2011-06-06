## Script (Python) "juiz.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
import random
context.REQUEST.response.setHeader('Content-Type', 'text/plain; charset=utf-8')

path = '/pycon/2010/sobre-o-evento/inscricoes'
palestras = context.portal_catalog(path=path, portal_type='Palestra',
                                   sort_on='sortable_title')
treinamentos = context.portal_catalog(path=path, portal_type='Treinamento',
                                      sort_on='sortable_title')

def tabela(lista):
    out = []
    lista = list((n, elem) for n, elem in enumerate(lista))
    random.shuffle(lista)
    for n, trabalho in lista:
        out.append("%02d %s (%s)" % (n+1, trabalho.Title.strip(), trabalho.getNome))
    return "\n".join(out)

print """\
# -*- coding: utf-8 -*-

\"\"\"
Prezado Juiz,

copie este arquivo para juiz_seunome.py e ordene os itens dos contextos
'Treinamentos' e 'Palestras' de acordo com a sua preferência.

Quanto mais ao topo de cada contexto ficar o item, melhor a classificação
dele naquele contexto. Evite editar as linhas; apenas mude as linhas de
posição.

Além dos trabalhos listados neste arquivo também teremos, pré-aprovados,
os keynotes do evento: Leah Culver e Ian Bicking; e a palestra sobre uma
outra linguagem de programação: Ruby, apresentada por Fábio Akita.

Para maiores detalhes sobre cada um dos trabalhos presentes neste arquivo,
consulte o endereço:

  http://www.pythonbrasil.org.br/processo_avaliacao

Depois de computados os votos de todos os juízes, os trabalhos serão
encaixados na grade, de acordo com os horários que estiverem disponíveis.

Eventualmente assuntos repetidos serão agrupados e pequenos ajustes serão
feitos, sempre buscando o que for melhor para o evento.
\"\"\"

Treinamentos = \"\"\"\
"""

print tabela(treinamentos)
print """\
\"\"\"

Palestras = \"\"\"\
"""

print tabela(palestras)
print '"""'

return printed
