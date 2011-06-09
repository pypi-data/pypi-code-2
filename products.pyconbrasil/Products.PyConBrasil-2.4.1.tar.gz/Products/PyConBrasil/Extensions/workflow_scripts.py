from Products.CMFPlone.utils import log, getToolByName

def marcaComoPaga(self, state_change, **kw):
    obj = state_change.object
    obj.setPaga(True)
    obj.reindexObject()
    template = obj.template_pagamento_realizado
    params = {
        'nome': obj.getNome(),
        'email': obj.getEmail(),
        'URL': obj.absolute_url(),
    }
    _enviaEmail(obj, template(obj), template.title, params)

def enviaEmailConfirmacao(self, state_change, **kw):
    obj = state_change.object
    template = obj.template_inscricao
    params = {
        'nome': obj.getNome(),
        'email': obj.getEmail(),
        'URL': obj.absolute_url(),
    }
    _enviaEmail(obj, template(obj), template.title, params)

def depoisSalvar(self, state_change, **kw):
    obj = state_change.object
    template = obj.template_recebimento_trabalho
    params = {
        'nome': obj.getNome(),
        'email': obj.getEmail(),
        'titulo': obj.Title(),
    }
    _enviaEmail(obj, template(obj), template.title, params)

def depoisAprovar(self, state_change, **kw):
    obj = state_change.object
    template = obj.template_aprovacao_trabalho
    params = {
        'nome': obj.getNome(),
        'email': obj.getEmail(),
        'titulo': obj.Title(),
    }
    _enviaEmail(obj, template(obj), template.title, params)

def depoisRejeitar(self, state_change, **kw):
    obj = state_change.object
    template = obj.template_rejeicao_trabalho
    params = {
        'nome': obj.getNome(),
        'email': obj.getEmail(),
        'titulo': obj.Title(),
    }
    _enviaEmail(obj, template(obj), template.title, params)

def enviaEmailPreInscritos(self, state_change, **kw):
    obj = state_change.object
    template = obj.template_confirmacao
    inscricoes = obj.portal_catalog(portal_type='Inscricao',
                                    review_state='pre-inscrito')
    for inscricao in inscricoes:
        params = {
            'nome': inscricao.getNome,
            'email': inscricao.getEmail,
            'UID': inscricao.UID,
        }
        _enviaEmail(obj, template(obj), template.title, params)

def _enviaEmail(obj, template, subject, params, charset='utf-8'):
    mto = "%s <%s>" % (params['nome'], params['email'])
    mfrom = "%s <%s>" % (obj.email_from_name, obj.email_from_address)
    obj.MailHost.secureSend(template % params, mto, mfrom,
                            subject, charset=charset)
