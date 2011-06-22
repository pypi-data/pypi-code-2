import urllib
import argparse
from lxml import etree
import zipfile
import StringIO
try:
    import json
except ImportError:
    import simplejson as json
import pkg_resources
import shutil
import os
import tempfile

jqueryui_download_url = 'http://jqueryui.com/download'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('version')
    args = parser.parse_args()
    print '''\
Make a git checkout of version %s of jqueryui:

    git@github.com:jquery/jquery-ui.git

Run the build script (ant) and rsync the resulting `ui` directory with the
directory in `resources`. This takes care of the 1) UI, 2) effects javascripts
and 3) the `base` theme.

In order to collect the themes listed on jqueryui.com/download, run this script.
Make sure to do a proper comparison before checking in the results.

The procedure for updating js.jqueryui may change with the next release.
    ''' % args.version

    download_page_html = etree.parse(jqueryui_download_url, etree.HTMLParser())

    dep_js = download_page_html.find('//div[@id="content-wrapper"]//script').text
    dep_json = dep_js[dep_js.find('{'):dep_js.find('}') + 1].replace("'", '"')
    dep_info = json.loads(dep_json)

    temp_download = tempfile.mkdtemp()

    for option in download_page_html.findall('//select[@id="theme"]/option'):
        theme = option.attrib['value']
        theme_name = option.text.lower().replace(' ', '-') or 'no-theme'
        postdata = urllib.urlencode({
            'download': 'true',
            'theme': theme,
            't-name': theme_name,
            'ui-version': args.version,
        }) + '&' + '&'.join(['files[]=%s' % key for key in dep_info])
        print 'downloading', theme_name
        theme_zip = urllib.urlopen(jqueryui_download_url, postdata).read()
        container = zipfile.ZipFile(StringIO.StringIO(theme_zip))
        for path in container.namelist():
            if not path.startswith('development-bundle/themes'):
                continue
            container.extract(path, temp_download)

    themes_dir = pkg_resources.resource_filename('js.jqueryui', 'resources/themes')
    for dir_ in os.listdir(themes_dir):
        if dir_ == 'base':
            continue
        try:
            shutil.rmtree(os.path.join(themes_dir, dir_))
        except OSError:
            pass

    bundle = os.path.join(temp_download, 'development-bundle', 'themes')
    for dir_ in os.listdir(bundle):
        if dir_ == 'base':
            continue
        shutil.move(os.path.join(bundle, dir_), os.path.join(themes_dir, dir_))

    # XXX rename custom/version from new paths
    custom = '-%s.custom' % args.version
    for root, _, files in os.walk(themes_dir):
        for file_ in files:
            if custom in file_:
                print 'renaming', os.path.join(root, file_)
                shutil.move(os.path.join(root, file_),
                    os.path.join(root, file_.replace(custom, '')))
