"""Common configuration constants
"""
from betahaus.memberprofile.permissions import AddMemberProfile


PROJECTNAME = 'betahaus.memberprofile'

#For the archetypes init stuff :)
ADD_PERMISSIONS = {
    'MemberProfile': AddMemberProfile,
}

DEFAULT_SETTINGS = {}
DEFAULT_SETTINGS['title_as'] = 'username'