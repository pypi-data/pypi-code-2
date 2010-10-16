import httplib
import urllib

from mercurial import util

def build(ui, repo, **kwargs):
    """The hook entry point to send a build message to Hudson"""

    hudson_url = __get_from_hudson_config(ui, 'url', 'Url for Hudson server not specified in configuration')
    job_name = __get_from_hudson_config(ui, 'job', 'Job name for hudson not specified in configuration')
    authentication_token = ui.config('hudson', 'authentication_token')

    __send_to_server(hudson_url, job_name, authentication_token)

    return 0

def __get_from_hudson_config(ui, key, error_message):
    value = ui.config('hudson', key)
    if value is None or len(value) == 0:
        raise util.Abort(error_message)

    return value

def __send_to_server(hudson_url, job_name, authentication_token):
    connection = httplib.HTTPConnection(hudson_url)

    build_url = '/job/{0}/build'.format(job_name)
    if authentication_token is not None and len(authentication_token) != 0:
        build_url  += '?' + urllib.urlencode({'token':authentication_token})

    connection.request('GET', build_url)

    status = connection.getresponse().status

    if status == httplib.NOT_FOUND:
        raise util.Abort('Job not found in specified Hudson server')

    if status == httplib.FORBIDDEN:
        raise util.Abort('You should specify a valid authentication token in order to perform the build')
