# Copyright 2011 Terena. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.

#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#        and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY TERENA ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL TERENA OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of Terena.

import re
from tempfile import NamedTemporaryFile
import urllib2

from django import db
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.files.base import File
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext
from django.db.utils import DatabaseError
from django.db import transaction
from django.utils.translation import ugettext as _

from domain.models import Domain
from entity.forms import EntityForm, MetadataTextEditForm
from entity.forms import MetadataFileEditForm, MetadataRemoteEditForm
from entity.models import Entity, PermissionDelegation
from entity.validation import validate

from vff.storage import create_fname

CONNECTION_TIMEOUT = 10


def _paginated_list_of_entities(request, entities):
    paginator = Paginator(entities, get_entities_per_page())

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        entities = paginator.page(page)
    except (EmptyPage, InvalidPage):
        entities = paginator.page(paginator.num_pages)
    return entities


def get_entities_per_page():
    if hasattr(settings, 'ENTITIES_PER_PAGE'):
        return settings.ENTITIES_PER_PAGE
    else:
        return 10


def entities_list(request):
    entities = Entity.objects.all()
    paginated_entities = _paginated_list_of_entities(request, entities)

    return render_to_response('entity/list.html', {
            'entities': paginated_entities,
            }, context_instance=RequestContext(request))


@login_required
def entity_add(request):
    return entity_add_with_domain(request, None, 'entities_list')


@login_required
def entity_add_with_domain(request, domain_name=None,
                           return_view_name='account_profile'):
    if domain_name is None:
        entity = None
    else:
        domain = get_object_or_404(Domain, name=domain_name)
        entity = Entity(domain=domain)

    if request.method == 'POST':
        form = EntityForm(request.user, request.POST, instance=entity)
        if form.is_valid():
            form.save()
            messages.success(request, _('Entity created succesfully'))
            return HttpResponseRedirect(reverse(return_view_name))
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))


    else:
        form = EntityForm(request.user, instance=entity)

    return render_to_response('entity/add.html', {
            'form': form,
            }, context_instance=RequestContext(request))


def entity_view(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    return render_to_response('entity/view.html', {
            'entity': entity,
            }, context_instance=RequestContext(request))


@login_required
def entity_remove(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if request.method == 'POST':
        entity.delete()
        messages.success(request, _('Entity removed succesfully'))
        return HttpResponseRedirect(reverse('entities_list'))

    return render_to_response('entity/remove.html', {
            'entity': entity,
            }, context_instance=RequestContext(request))

# METADATA EDIT


def _get_edit_metadata_form(request, entity, edit_mode, form=None):
    if form is None:
        if edit_mode == 'text':
            fname = create_fname(entity, 'metadata')
            text = entity.metadata.storage.get_revision(fname)
            form = MetadataTextEditForm(initial={'metadata_text': text})
        elif edit_mode == 'file':
            # XXX siempre vacia, imborrable, required
            form = MetadataFileEditForm()
        elif edit_mode == 'remote':
            form = MetadataRemoteEditForm()
    form_action = reverse('%s_edit_metadata' % edit_mode, args=(entity.id, ))

    context_instance = RequestContext(request)
    return render_to_string('entity/simple_edit_metadata.html', {
        'edit': edit_mode,
        'entity': entity,
        'form': form,
        'form_action': form_action,
        'form_id': edit_mode + '_edit_form',
    }, context_instance=context_instance)


def _get_username(request):
    return u'%s <%s>' % (
            request.user.get_full_name() or request.user.username,
            request.user.email or request.user.username)


@login_required
def text_edit_metadata(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if request.method == 'POST':
        form = MetadataTextEditForm(request.POST)
        text = form['metadata_text'].data
        if not text:
            form.errors['metadata_text'] = [_('Empty metadata not allowed')]
        else:
            errors = validate(text)
            if errors:
                form.errors['metadata_text'] = errors
        if form.is_valid():
            tmp = NamedTemporaryFile(delete=True)
            tmp.write(text.encode('utf8'))
            tmp.seek(0)
            content = File(tmp)
            name = entity.metadata.name
            username = _get_username(request)
            commit_msg = form['commit_msg_text'].data.encode('utf8')
            entity.metadata.save(name, content, username, commit_msg)
            entity.save()
            messages.success(request, _('Entity metadata has been modified'))
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))
    else:
        form = None
    return edit_metadata(request, entity.id, text_form=form,
                         accordion_activate='text')


@login_required
def file_edit_metadata(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if request.method == 'POST':
        form = MetadataFileEditForm(request.POST, request.FILES)
        content = form['metadata_file'].data
        if content is not None:
            text = content.read()
            content.seek(0)
            if not text:
                form.errors['metadata_file'] = [_('Empty metadata not allowed')]
            else:
                errors = validate(text)
                if errors:
                    form.errors['metadata_file'] = errors
        if form.is_valid():
            name = entity.metadata.name
            username = _get_username(request)
            commit_msg = form['commit_msg_file'].data.encode('utf8')
            entity.metadata.save(name, content, username, commit_msg)
            entity.save()
            messages.success(request, _('Entity metadata has been modified'))
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))
    else:
        form = None
    return edit_metadata(request, entity.id, accordion_activate='upload',
                         file_form=form)


@login_required
def remote_edit_metadata(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    if request.method == 'POST':
        form = MetadataRemoteEditForm(request.POST)
        if form.is_valid():
            content_url = form['metadata_url'].data
            try:
                resp = urllib2.urlopen(content_url, None, CONNECTION_TIMEOUT)
            except urllib2.URLError, e:
                form.errors['metadata_url'] = ['URL Error: ' + str(e)]
            except urllib2.HTTPError, e:
                form.errors['metadata_url'] = ['HTTP Error: ' + str(e)]
            except ValueError, e:
                try:
                    resp = urllib2.urlopen('http://' + content_url,
                                                 None, CONNECTION_TIMEOUT)
                except Exception:
                    form.errors['metadata_url'] = ['Value Error: ' + str(e)]
            except Exception, e:
                form.errors['metadata_url'] = ['Error: ' + str(e)]
            if form.is_valid():
                if resp.getcode() != 200:
                    form.errors['metadata_url'] = [_(
                                          'Error getting the data: %s'
                                                    ) % resp.msg]
                text = resp.read()
                if not text:
                    form.errors['metadata_url'] = [_('Empty metadata not allowed')]
                else:
                    errors = validate(text)
                    if errors:
                        form.errors['metadata_url'] = errors
                try:
                    encoding = resp.headers['content-type'].split('charset=')[1]
                except (KeyError, IndexError):
                    encoding = ''
                resp.close()
        if form.is_valid():
            tmp = NamedTemporaryFile(delete=True)
            if encoding:
                text = text.decode(encoding).encode('utf8')
            tmp.write(text)
            tmp.seek(0)
            content = File(tmp)
            name = entity.metadata.name
            username = _get_username(request)
            commit_msg = form['commit_msg_remote'].data.encode('utf8')
            entity.metadata.save(name, content, username, commit_msg)
            entity.save()
            messages.success(request, _('Entity metadata has been modified'))
        else:
            messages.error(request, _('Please correct the errors'
                                      ' indicated below'))
    else:
        form = None
    return edit_metadata(request, entity.id, accordion_activate='remote',
                         remote_form=form)


DEFAULT_SAML_META_JS_PLUGINS = ('attributes', 'certs', 'contact', 'info',
                                'location', 'saml2sp')


@login_required
def edit_metadata(request, entity_id, accordion_activate='text',
                  text_form=None, file_form=None, remote_form=None):
    entity = get_object_or_404(Entity, id=entity_id)

    samlmetajs_plugins = getattr(settings, 'SAML_META_JS_PLUGINS',
                                 DEFAULT_SAML_META_JS_PLUGINS)

    return render_to_response('entity/edit_metadata.html', {
            'entity': entity,
            'text_html': _get_edit_metadata_form(request, entity, 'text',
                                                 form=text_form),
            'file_html': _get_edit_metadata_form(request, entity, 'file',
                                                 form=file_form),
            'remote_html': _get_edit_metadata_form(request, entity, 'remote',
                                                   form=remote_form),
            'activate': accordion_activate,
            'samlmetajs_plugins': samlmetajs_plugins,
            'needs_google_maps': 'location' in samlmetajs_plugins,
            }, context_instance=RequestContext(request))


# ENTITY SEARCH

def _search_entities(search_terms):
    lang = getattr(settings, 'PG_FT_INDEX_LANGUAGE', u'english')
    sql = u"select * from entity_entity where to_tsvector(%s, name) @@ to_tsquery(%s, %s)"
    return Entity.objects.raw(sql, [lang, lang, search_terms])


def search_entities(request):
    search_terms_raw = request.GET.get('query', '').strip()
    op = getattr(settings, 'PG_FTS_OPERATOR', '&')
    sid = transaction.savepoint()
    if db.database['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
        search_terms = re.sub(ur'\s+', op, search_terms_raw)
        entities = _search_entities(search_terms)
    else:
        search_terms_list = search_terms_raw.split(' ')
        where = (u' %s ' % op).join([u"name ilike '%s'"] * len(search_terms_list))
        sql = u"select * from entity_entity where " + where
        entities = Entity.objects.raw(sql, search_terms_list)
        search_terms = op.join(search_terms)
    try:
        entities = list(entities)
    except DatabaseError:
        transaction.savepoint_rollback(sid)
        entities = []
        msg = _(u'There seem to be illegal characters in your search.\n'
                u'You should not use !, :, &, | or \\')
        messages.error(request, msg)
    else:
        n = len(entities)
        plural = n == 1 and 'entity' or 'entities'
        msg = _(u'Found %d %s matching "%s"') % (n, plural, search_terms_raw)
        messages.success(request, msg)

    paginated_entities = _paginated_list_of_entities(request, entities)
    return render_to_response('entity/search_results.html', {
            'entities': paginated_entities,
            'search_terms': search_terms_raw,
            }, context_instance=RequestContext(request))


# SHARING ENTITY EDITION

@login_required
def sharing(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    return render_to_response('entity/sharing.html', {
            'entity': entity,
            }, context_instance=RequestContext(request))


@login_required
def list_delegates(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    return render_to_response('entity/delegate_list.html', {
            'delegates': entity.delegates.all(),
            'entity_id': entity.pk,
            }, context_instance=RequestContext(request))


@login_required
def remove_delegate(request, entity_id, user_id):
    entity = get_object_or_404(Entity, id=entity_id)
    delegate = User.objects.get(pk=user_id)
    if entity and delegate:
        delegations = PermissionDelegation.objects.filter(entity=entity,
                                                  delegate=delegate)
        for delegation in delegations:
            delegation.delete()
    return list_delegates(request, entity_id)


@login_required
def add_delegate(request, entity_id, username):
    entity = get_object_or_404(Entity, id=entity_id)
    new_delegate = User.objects.get(username=username)
    if entity and new_delegate:
        pd = PermissionDelegation.objects.filter(entity=entity,
                                                delegate=new_delegate)
        if not pd and new_delegate != entity.owner:
            pd = PermissionDelegation(entity=entity, delegate=new_delegate)
            pd.save()
        elif pd:
            return HttpResponse('delegate')
        else:
            return HttpResponse('owner')
    return list_delegates(request, entity_id)


@login_required
def make_owner(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    old_owner = entity.owner
    new_owner_id = request.POST.get('new_owner_id')
    if new_owner_id:
        new_owner = User.objects.get(pk=int(new_owner_id))
        if new_owner:
            entity.owner = new_owner
            entity.save()
            msg = _('New owner successfully set')
            old_pd = PermissionDelegation.objects.get(entity=entity,
                                                  delegate=new_owner)
            if old_pd:
                old_pd.delete()
            if old_owner:
                new_pd = PermissionDelegation.objects.filter(entity=entity,
                                              delegate=old_owner)
                if not new_pd:
                    new_pd = PermissionDelegation(entity=entity,
                                                  delegate=old_owner)
                    new_pd.save()
        else:
            msg = _('User not found')
    else:
        msg = _('You must provide the user id of the new owner')
    messages.success(request, msg)
    return HttpResponseRedirect(reverse('entity_view', args=(entity_id,)))
