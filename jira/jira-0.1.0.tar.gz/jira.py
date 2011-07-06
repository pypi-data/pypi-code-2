'''This is a thin wrapper around Jira XML/RPC.

See docs at http://bit.ly/m1zs3T (Note that some methods were combined together with defualt
values, see get_issue_types for example).

>>> import jira
>>> client = jira.connect('http://jira.server/rpc/xmlrpc', 'user', 'password')
>>> for issue in client.get_issues_from_filter('007'):
   ...:    client.add_comment(issue['id'], 'Mission accepted')
>>> client.logout()
'''

__version__ = '0.1.0'

from xmlrpclib import ServerProxy

#: Default maximal number of results (see get_issues_from_text_search)
DEFAULT_MAX_NUM_RESULTS = 100

class Jira:
    def __init__(self, url, user=None, password=None):
        self.url = url
        self._jira = self._token = None
        if user and password:
            self.login(user, password)

    def login(self, user, password):
        '''Logs the user into JIRA.'''
        self._jira = ServerProxy(self.url).jira1
        self._token = self._jira.login(user, password)

    def logout(self):
        '''Logs the user out of JIRA'''
        self._jira.logout(self._token)
        self._jira = self._token = None

    def add_comment(self, issue_key, comment):
        '''Adds a comment to an issue'''
        return self._jira.addComment(self._token, issue_key, comment)

    def create_issue(self, issue):
        '''Creates an issue in JIRA from a Hashtable object.'''
        return self._jira.createIssue(self._token, issue)

    def get_comments(self, issue_key):
        '''Returns all comments associated with the issue'''
        return self._jira.getComments(self._token, issue_key)

    def get_components(self, project_key):
        '''Returns all components available in the specified project'''
        return self._jira.getComponents(self._token, project_key)

    def get_favourite_filters(self):
        '''Gets all favourite filters available for the currently logged in user'''
        return self._jira.getFavouriteFilters(self._token)

    def get_issue(self, issue_key):
        '''Gets an issue from a given issue key.'''
        return self._jira.getIssue(self._token, issue_key)

    def get_issues_from_filter(self, filter_id):
        '''Executes a saved filter'''
        return self._jira.getIssuesFromFilter(self._token, filter_id)

    def get_issues_from_text_search(self, search_terms, project_keys=None,
                                    max_num_results=DEFAULT_MAX_NUM_RESULTS):
        '''Find issues using a free text search.
        With project_keys specified, search will be limited to these project.
        '''
        if project_keys:
            return self._jira.getIssuesFromTextSearchWithProject(
                self._token, project_keys, search_terms, max_num_results)
        else:
            return self._jira.getIssuesFromTextSearch(self._token, search_terms)

    def get_issue_types(self, project_id=None):
        '''Returns all visible issue types in the system.
        With project_id specified, will return issue types just for this
        project.
        '''
        if project_id:
            return self._jira.getIssueTypesForProject(self._token, project_id)
        else:
            return self._jira.getIssueTypes(self._token)

    def get_priorities(self):
        '''Returns all priorities in the system'''
        return self._jira.getPriorities(self._token)

    def get_projects_no_schemes(self):
        '''Returns a list of projects available to the user'''
        return self._jira.getProjectsNoSchemes(self._token)

    def get_resolutions(self):
        '''Returns all resolutions in the system'''
        return self._jira.getResolutions(self._token)

    def get_server_info(self):
        '''Returns the Server information such as baseUrl, version, edition, buildDate, buildNumber.'''
        return self._jira.getServerInfo(self._token)

    def get_statuses(self):
        '''Returns all statuses in the system'''
        return self._jira.getStatuses(self._token)

    def get_sub_task_issue_types(self, project_id):
        '''Returns all visible subtask issue types in the system.
        With project_id specified, will return issues types just for this
        project.
        '''
        if project_id:
            return self._jira.getSubTaskIssueTypesForProject(self._token, project_id)
        else:
            return self._jira.getSubTaskIssueTypes(self._token)

    def get_user(self, username):
        '''Returns a user's information given a username'''
        return self._jira.getUser(self._token, username)

    def get_versions(self, project_key):
        '''Returns all versions available in the specified project'''
        return self._jira.getVersions(self._token, project_key)

    def update_issue(self, issue_key, field_values):
        '''Updates an issue in JIRA from a Hashtable object.'''
        return self._jira.updateIssue(self._token, issue_key, field_values)

def connect(url, user, password):
    '''Connect to Jira server, return client object.'''
    return Jira(url, user, password)
