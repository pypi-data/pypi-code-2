from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.core.urlresolvers import reverse
from grate.mongo import PublicKey, Repo, User, Group
from grate.access import EntityAccess
from forms import PublicKeyForm, GroupForm, save_error_messages
from decorators import (restrict_http_method, user_has_repo_admin,
    repo_exists, group_exists, user_has_group_admin)
from pymongo.binary import Binary


@restrict_http_method('GET')
def index(request):
    return render_to_response('sewer/index.html',
        context_instance=RequestContext(request))


@restrict_http_method('POST')
@login_required
def key_add(request):
    form = PublicKeyForm(request.POST)
    if not form.is_valid():
        save_error_messages(request, form)
        return HttpResponseRedirect('../')
    key = form.cleaned_data['key']
    # We have a valid public key.
    data = Binary(key.blob())
    user = request.user
    try:
        pubkey, created = PublicKey.objects.get_or_create(data=data,
            defaults={'user': user})
        if not pubkey.user:
            pubkey.user = user
            pubkey.save()
        if not created and not pubkey.user == user:
            messages.error(request, 'The given public key is already '
                'claimed by %s' % pubkey.user.username)
        if user.add_key(pubkey):
            messages.info(request, 'Added key: %s' % pubkey)
            user.save()
        else:
            messages.warning(request, '%s has already been added' % pubkey)
    except Exception, e:
        messages.error(request, '%s %r' % (str(e), e))
        raise
    return HttpResponseRedirect('../')


@restrict_http_method('POST')
@login_required
def key_remove(request, id):
    key = PublicKey.objects(id=id).first()
    if not key:
        messages.error(request, 'Key with id %s not found.' % id)
    elif not key.user == request.user:
        messages.error(request, 'You do not own this key.')
    else:
        fingerprint = key.fingerprint()
        # XXX atomic protection.
        request.user.keys.remove(key)
        request.user.save(safe=True)
        key.delete(safe=True)
        messages.info(request, 'Key %s removed' % fingerprint)
    return HttpResponse('')


@restrict_http_method('GET')
@login_required
def key_index(request):
    return render_to_response('sewer/key_index.html',
        {'keys': request.user.keys, 'form': PublicKeyForm()},
        context_instance=RequestContext(request))


@restrict_http_method('POST')
@login_required
def repo_add(request):
    user = request.user
    name = request.POST['name']
    prefix_type = request.POST['prefix-type']
    prefix = request.POST['prefix']
    if not name:
        messages.error(request, 'Please enter a valid name.')
        return HttpResponseRedirect('../')
    name = '%s/%s' % (request.user.username, name)
    repo = Repo.create(name, request.user, False)
    if not repo.owner == user:
        messages.warning(request, 'Repository %s is already owned by %s'
            % (repo.name, repo.owner))
    return HttpResponseRedirect('../')


@restrict_http_method('GET')
@login_required
@user_has_repo_admin
def repo_admin(request, repo):
    if not repo:
        return HttpResponseRedirect(reverse('sewer:repo-index'))
    return render_to_response('sewer/repo_admin.html',
        {'repo': repo, 'levels': Repo.levels()},
        context_instance=RequestContext(request))


@restrict_http_method('POST')
@login_required
@user_has_repo_admin
def repo_add_access(request, repo):
    if not repo:
        return HttpResponseRedirect(reverse('sewer:repo-index'))
    access = request.POST['level']
    if not Repo.is_valid_access(access):
        messages.error(request, '"%s" is not understood.' % access)
        return HttpResponseRedirect('../../admin/')
    # Grab the entity.
    name = request.POST['name']
    entity = User.objects(username=name).first()
    if not entity and not settings.ALLOW_NONEXISTENT_USER:
        messages.error(request, '%s is not found.' % name)
        return HttpResponseRedirect('../../admin/')
    elif not entity and settings.ALLOW_NONEXISTENT_USER:
        messages.warning(request, 'User %s has been created.' % name)
        entity = User(username=name)
        entity.save()
    try:
        repo.add_access(entity, access)
        messages.info(request, '%s added as a %s.' % (entity, access))
    except Exception, e:
        messages.error(request, str(e))
    return HttpResponseRedirect('../../admin/')


@restrict_http_method('GET')
@login_required
@repo_exists
def repo_view(request, repo):
    if not repo:
        return HttpResponseRedirect(reverse('sewer:repo-index'))
    def show_get(access):
        return render_to_response('sewer/repo_view.html',
            {'repo': repo, 'access': access},
            context_instance=RequestContext(request))
    access = repo.get_access(request.user)
    if repo.is_public:
        return show_get(access)
    if access:
        return show_get(access)
    return HttpResponse('Forbidden.', status=403)


@restrict_http_method('GET')
@login_required
def repo_index(request):
    repos = request.user.owned_repos
    repos.extend(request.user.all_repos())
    # TODO group access.
    return render_to_response('sewer/repo_index.html',
        {'repos': repos},
        context_instance=RequestContext(request))


@restrict_http_method('GET')
@login_required
@user_has_repo_admin
def repo_set_public(request, repo):
    if repo:
        repo.is_public = True
        repo.save()
    return HttpResponse()


@restrict_http_method('GET')
@login_required
@user_has_repo_admin
def repo_set_private(request, repo):
    if repo:
        repo.is_public = False
        repo.save(safe=True)
    return HttpResponse()


@restrict_http_method('GET')
@login_required
def view_messages(request):
    return render_to_response('messages.html',
        context_instance=RequestContext(request))


@restrict_http_method('GET')
@login_required
def group_index(request):
    return render_to_response('sewer/group_index.html', {'form': GroupForm()},
        context_instance=RequestContext(request))


@restrict_http_method('POST')
@login_required
def group_add(request):
    form = GroupForm(request.POST)
    if not form.is_valid():
        save_error_messages(request, form)
        return HttpResponseRedirect('../')
    name = form.cleaned_data['name']
    g = Group(owner=request.user, name=name)
    try:
        g.save(safe=True)
        messages.info(request, 'Group %s created.' % name)
    except Exception, e:
        messages.error(request, str(e))
    return HttpResponseRedirect('../')


@restrict_http_method('POST')
@login_required
@user_has_group_admin
def group_add_access(request, group):
    # TODO refactor
    if not group:
        return HttpResponseRedirect(reverse('sewer:group-index'))
    access = request.POST['level']
    if not Group.is_valid_access(access):
        messages.error(request, '"%s" is not understood.' % access)
        return HttpResponseRedirect('../../admin/')
    # Grab the entity.
    name = request.POST['name']
    entity = User.objects(username=name).first()
    if not entity and not settings.ALLOW_NONEXISTENT_USER:
        messages.error(request, '%s is not found.' % name)
        return HttpResponseRedirect('../../admin/')
    elif not entity and settings.ALLOW_NONEXISTENT_USER:
        messages.warning(request, 'User %s has been created.' % name)
        entity = User(username=name)
        entity.save()
    try:
        group.add_access(entity, access)
        messages.info(request, '%s added as a %s.' % (entity, access))
    except Exception, e:
        messages.error(request, str(e))
    return HttpResponseRedirect('../../admin/')


@restrict_http_method('GET')
@login_required
@group_exists
def group_view(request, group):
    if not group:
        return HttpResponseRedirect(reverse('sewer:group-index'))
    return render_to_response('sewer/group_view.html', {'group': group},
        context_instance=RequestContext(request))


@restrict_http_method('GET')
@login_required
@user_has_group_admin
def group_admin(request, group):
    if not group:
        return HttpResponseRedirect(reverse('sewer:group-index'))
    return render_to_response('sewer/group_admin.html', {'group': group},
        context_instance=RequestContext(request))


@restrict_http_method('POST')
@login_required
def remove_access(request, id):
    user = request.user
    try:
        access = EntityAccess.objects(id=id).first()
        if access.provider.has_admin_access(user):
            level = access.provider.get_access_name(access.access)
            entity = access.entity
            access.delete(safe=True)
            messages.info(request, '%s %s removed.' % (level, entity))
        else:
            messages.error(request, 'Unauthorized.')
    except EntityAccess.DoesNotExist:
        messages.warning(request, 'Access ID: %s is not found.' % id)
    except Exception, e:
        messages.error(request, 'Error: %s' % e)
    return HttpResponse('')
