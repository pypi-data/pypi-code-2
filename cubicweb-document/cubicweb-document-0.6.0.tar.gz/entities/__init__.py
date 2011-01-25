def req_branch_scope(req):
    branch = req.form.get('branch')
    if branch is not None:
        return branch
    try:
        return req.__branch
    except AttributeError:
        pass
    cookies = req.get_cookie()
    branchcookie = cookies.get('branch_scope')
    if branchcookie is None:
        cookies['branch_scope'] = branch = u'default' # XXX hg specific, should use repo.default_branch()
        req.set_cookie(cookies, 'branch_scope')
    else:
        branch = unicode(branchcookie.value)
    req.__branch = branch
    return branch


def main_repository(config, req):
    try:
        return req.__mainrepo
    except AttributeError:
        pass
    mainrepo = config.get('main-repository')
    if mainrepo:
        reporset = req.execute('Repository R WHERE R path %(rpath)s',
                               {'rpath' : mainrepo})
    else:
        reporset = req.execute('Repository R')
    if not reporset:
        req.error('no repository can be found')
        req.__mainrepo = None
        return
    if len(reporset) > 1:
        req.error('%s repositories found but main-repository is not set, using '
                  'an arbitrary one')
    repo = reporset.get_entity(0,0)
    req.__mainrepo = repo
    return repo
