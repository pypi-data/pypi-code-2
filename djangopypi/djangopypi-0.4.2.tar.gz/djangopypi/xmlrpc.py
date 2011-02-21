import xmlrpclib

from django.conf import settings
from django.http import HttpResponseNotAllowed, HttpResponse
from django.contrib.sites.models import Site

from djangopypi.models import Package, Release



SITE_NAME = Site.objects.get_current().domain

def list_packages():
    pkg_list = list(Package.objects.all().values_list('name', flat=True))
    xml_out = xmlrpclib.dumps((pkg_list,), methodresponse=True)
    return HttpResponse(xml_out, content_type='text/xml')

def package_releases(package_name, show_hidden=False):
    releases = []
    try:
        pkg = Package.objects.get(name=package_name)
        releases = list(pkg.releases.filter(hidden=show_hidden).values_list('version', flat=True))
    except Package.DoesNotExist:
        pass
    except Exception, e:
        print e
    
    return HttpResponse(xmlrpclib.dumps((releases,), methodresponse=True))

def release_urls(package_name, version):
    output = []
    try:
        pkg = Package.objects.get(name=package_name)
        release = pkg.releases.get(version=version)
        
        for dist in release.distributions.all():
            output.append({
                'url': 'http://%s%s' % (SITE_NAME, dist.get_absolute_url()),
                'packagetype': dist.filetype,
                'filename': dist.filename,
                'size': dist.content.size,
                'md5_digest': dist.md5_digest,
                'downloads': 0,
                'has_sig': len(dist.signature)>0,
                'python_version': dist.pyversion,
                'comment_text': dist.comment
            })
    except (Package.DoesNotExist, Release.DoesNotExist):
        pass
    except Exception, e:
        print e
    
    return HttpResponse(xmlrpclib.dumps((output,), methodresponse=True))

def release_data(package_name, version):
    output = {
        'name': '',
        'version': '',
        'stable_version': '',
        'author': '',
        'author_email': '',
        'maintainer': '',
        'maintainer_email': '',
        'home_page': '',
        'license': '',
        'summary': '',
        'description': '',
        'keywords': '',
        'platform': '',
        'download_url': '',
        'classifiers': '',
        'requires': '',
        'requires_dist': '',
        'provides': '',
        'provides_dist': '',
        'requires_external': '',
        'requires_python': '',
        'obsoletes': '',
        'obsoletes_dist': '',
        'project_url': '',
    }
    try:
        pkg = Package.objects.get(name=package_name)
        release = pkg.releases.get(version=version)
        metadata = release.package_info
        output.update({'name': pkg.name, 'version': release.version,})
        output.update(metadata)
    except (Package.DoesNotExist, Release.DoesNotExist):
        pass
    except Exception, e:
        print e
    
    return HttpResponse(xmlrpclib.dumps((output,), methodresponse=True))

#
"""
search(spec[, operator])

Search the package database using the indicated search spec.
The spec may include any of the keywords described in the above list (except 'stable_version' and 'classifiers'), for example: {'description': 'spam'} will search description fields. Within the spec, a field's value can be a string or a list of strings (the values within the list are combined with an OR), for example: {'name': ['foo', 'bar']}. Valid keys for the spec dict are listed here. Invalid keys are ignored:
name
version
author
author_email
maintainer
maintainer_email
home_page
license
summary
description
keywords
platform
download_url
Arguments for different fields are combined using either "and" (the default) or "or". Example: search({'name': 'foo', 'description': 'bar'}, 'or'). The results are returned as a list of dicts {'name': package name, 'version': package release version, 'summary': package release summary}

changelog(since)

Retrieve a list of four-tuples (name, version, timestamp, action) since the given timestamp. All timestamps are UTC values. The argument is a UTC integer seconds since the epoch.

"""
def search(spec, operator='or'):
    output = {
        'name': '',
        'version': '',
        'summary': '',
    }
    return HttpResponse(xmlrpclib.dumps((output,), methodresponse=True))

def changelog(since):
    output = {
        'name': '',
        'version': '',
        'timestamp': '',
        'action': '',
    }
    return HttpResponse(xmlrpclib.dumps((output,), methodresponse=True))

def ratings(name, version, since):
    return HttpResponse(xmlrpclib.dumps(([],), methodresponse=True))


PYPI_COMMANDS = {
    'list_packages': list_packages,
    'package_releases': package_releases,
    'release_urls': release_urls,
    'release_data': release_data,
    'search': search,
    'changelog': changelog,
    'ratings': ratings,
}


def parse_xmlrpc_request(request):
    """
    Parse the request and dispatch to the appropriate view
    """
    args, command = xmlrpclib.loads(request.raw_post_data)
    if command in PYPI_COMMANDS:
        return PYPI_COMMANDS[command](*args)
    else:
        return HttpResponseNotAllowed(settings.DJANGOPYPI_ACTION_VIEW.keys())
