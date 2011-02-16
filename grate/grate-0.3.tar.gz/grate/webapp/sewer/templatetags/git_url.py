from django import template

register = template.Library()


def git_url(repo, user):
    try:
        return repo.git_url(str(user))
    except:
        return ''
register.filter('git_url', git_url)
