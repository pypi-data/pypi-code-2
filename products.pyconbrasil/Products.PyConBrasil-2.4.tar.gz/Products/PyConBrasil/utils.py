# -*- coding: utf-8 -*-

import re
from datetime import datetime

def splitLines(lines):
    tmp = []
    for line in lines:
        tmp.append(line.split('|'))
    return tmp

def dictPrecos(precos,tipos):
    ''' Dada uma lista de precos 
        e uma lista de tipos de incricao
        retornamos os precos atuais
    '''
    data = datetime.now().strftime('%y%m%d')
    tipos = splitLines(tipos)
    precos = splitLines(precos)
    precos.sort()
    dictPrecos = {}
    for tipoId,dataLimite,valor in precos:
        # Consideramos que a primeira linha com datalimite maior que a 
        # atual sera a valida
        if (tipoId in dictPrecos) or (data>dataLimite):
            continue
        dictPrecos[tipoId] = valor
    return dictPrecos

def getGroupDiscount(descontos,tipo,participantes):
    ''' Dada uma lista de descontos
        selecionamos o maior desconto possivel
        dado o tipo de inscricao
        
        >>> descontos = ['1|4|0.1','2|2|0.05','2|3|0.1','1|2|0.05','1|6|0.15','2|6|0.15',]
        >>> getGroupDiscount(descontos,1,2)
        0.05
        >>> getGroupDiscount(descontos,2,1)
        0.0
        >>> getGroupDiscount(descontos,1,6)
        0.15
        >>> getGroupDiscount(descontos,2,6)
        0.15
    '''
    descontos = splitLines(descontos)
    descontos = [(t,int(l),float(d)) for t,l,d in descontos]
    descontos.sort()
    desconto = 0.0
    #4|2|0.2
    for tipoId,minimo,valor in descontos:
        # Consideramos que a primeira linha com datalimite maior que a 
        # atual sera a valida
        if (tipoId != tipo) or (participantes<minimo):
            continue
        desconto = valor
    return desconto

def listaPatrocinadores(grupos,cotas,patrocinadores):
    ''' Dada uma lista de cotas e patrocinadores, retornamos 
        um dicionario com as informacoes
    '''
    grupos = splitLines(grupos)
    cotas = splitLines(cotas)
    patrocinadores = splitLines(patrocinadores)
    groups = []
    dictGrupos = {}
    dictCotas = {}
    listaPatrocinadores = []
    for grupoId,desc,descId in grupos:
        dictGrupos[grupoId] = {'desc':desc,'list':[],'id':descId}
        groups.append(grupoId)
    groups.sort()
    for cotaId,desc,group in cotas:
        dictCotas[cotaId] = {'desc':desc,'group':group}
    for cotaId,title,url,logo in patrocinadores:
        group = dictCotas[cotaId]['group']
        tmpDict = {'title':title,'url':url,'logo':logo}
        dictGrupos[group]['list'].append(tmpDict)
    return [(dictGrupos[id]['desc'],dictGrupos[id]['list'])for id in groups if dictGrupos[id]['list']]


def formataValor(valor, moeda='R$'):
    ''' Considerando que recebemos o valor em centavos,
        retornamos uma string devidamente formatada
    '''
    if valor.isdigit():
        valor = int(valor) / 100
        return '%s %.2f' % (moeda,valor)

def fmtVocabInscr(sheet):
    ''' Formata o valor a ser exibido no tipo de 
        inscricao, informado o valor no momento
    '''
    lstTipos = []
    valores = sheet.getProperty('valor_inscricao',[])
    tipos = sheet.getProperty('tipo_inscricao',[])
    precos = dictPrecos(valores,tipos)
    tipos = splitLines(tipos)
    for k,v,corp in tipos:
        v = '%s (%s)' % (v,formataValor(precos[k]))
        lstTipos.append((k,v,corp))
    return lstTipos
    