import logging

from pylons import url, request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect

from openbiblio.lib.base import BaseController, render
import openbiblio.model as model
AccountNamespace = model.Account.instance_namespace() 

log = logging.getLogger(__name__)

class AccountController(BaseController):
    def index(self):
        c.accounts = [ model.Account.get_by_uri(id_.identifier) for id_ in model.Account.find() ]
        return render('account/index.html')

    def view(self, username):
        ###
        ### should really use a lens (upgrade the bibo lens to
        ### understand about accounts and just display the
        ### account graph in here.
        ###
        ### *PARTICULARLY* because if we are asked for a
        ### content-type other than text/html we will want
        ### to give out an equivalent RDF description of the
        ### user. That is how users' activities on this site will
        ### get joined up to their activities on other sites.
        ###
        ### There should be no difference here from the
        ### graph controller. This is *NOT* a LAMP silo.
        ###
        c.is_myself = False
        if c.account is not None:
            account_id = c.account.identifier.rsplit("/", 1)[-1]
            c.is_myself = (username == account_id)

        if c.is_myself:
            c.view_account = c.account
        else:
            try:
                c.view_account = model.Account.get_by_uri(c.request_uri)
            except KeyError:
                abort(404)
                
        if c.view_account.avatar == []:
            c.view_account.avatar = c.account.get_avatar
            c.view_account.save(c.author, message='added gravatar to account %s' % c.account)
        return render('account/view.html')

    def login(self):
        if c.account is not None:
            redirect(c.account.identifier)
        else:
            c.error = request.params.get('error', '')
            form = render('account/openid_form.html')
            # /login_openid page need not exist -- request gets intercepted by openid plugin
            form = form.replace('FORM_ACTION', '/login_openid')
            return form

    def logout(self):
        if c.account is not None:
            redirect('/logout_openid')
        c.account = None
        return render('account/logout.html')

