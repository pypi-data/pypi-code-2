from functools import wraps
from django.http import HttpResponseNotAllowed
from django.contrib import messages
from grate.mongo import Repo, Group


def cls_exists(cls, cls_name, key):
    def outer(f):
        @wraps(f)
        def wrapper(request, name, *args, **kwargs):
            x = cls.objects(**{key: name}).first()
            if not x:
                messages.error(request, '%s %s does not exist.'
                    % (cls_name, name))
                x = None
            return f(request, x, *args, **kwargs)
        return wrapper
    return outer


def group_exists(f):
    return cls_exists(Group, 'Group', 'name')(f)


def repo_exists(f):
    return cls_exists(Repo, 'Repository', 'name')(f)


def user_has_group_admin(f):
    @wraps(f)
    def wrapper(request, group_name, *args, **kwargs):
        group = Group.objects(name=group_name).first()
        if not group:
            messages.error(request, 'Group %s does not exist.' % group_name)
            group = None
        elif not group.has_admin_access(request.user):
            messages.error(request, 'You do not have access for this group.')
            group = None
        return f(request, group, *args, **kwargs)
    return wrapper


def user_has_repo_admin(f):
    """
    A decorator for automatically resolving the repository object from a
    name. The wrapped function should take the repository as the second
    argument. e.g.

        def my_view(request, repo, ...):
            ...
    """
    @wraps(f)
    def wrapper(request, repo_name, *args, **kwargs):
        repo = Repo.objects(name=repo_name).first()
        if not repo:
            messages.error(request, 'Repository %s does not exist.'
                % repo_name)
            repo = None
        elif not repo.has_admin_access(request.user):
            messages.error(request, 'You do not have access for this '
                'repository.')
            repo = None
        return f(request, repo, *args, **kwargs)
    return wrapper


def restrict_http_method(*methods):
    def outer(f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                return HttpResponseNotAllowed(methods)
            return f(request, *args, **kwargs)
        return wrapper
    return outer
