import os
import urllib2
import cgi
from posixpath import join

from mercurial.cmdutil import show_changeset
from mercurial.templater import templater, stringify

def notify(ui, repo, node, source, url, hooktype, **kwargs):
    if hooktype not in ['changegroup', 'incoming']:
        ui.warn('Campfire Notify extension is intended only for use as changegroup or incoming hook')
    
    api_key = ui.config('campfire', 'api_key')
    campfire_url = ui.config('campfire', 'url')
    campfire_room = ui.config('campfire', 'room')
    cset_template = ui.config('campfire', 'cset_template', default=' * "{desc}" by {author}\n')
    template = ui.config('campfire', 'template', default='{user} pushed:\n{changesets}')
    strip_root_prefix = ui.config('campfire', 'strip_root_prefix', default='')
    
    if api_key is None or campfire_url is None or campfire_room is None:
        ui.warn('Campfire Notify extension requires api_key, url, and room to be set in [campfire] section of hgrc')
        return True

    user = os.environ.get('USER', 'unknown-user')
    root = repo.root
    if root.startswith(strip_root_prefix):
        root = root[len(strip_root_prefix):]

    displayer = show_changeset(ui, repo, {'template': cset_template})
    
    node_rev = repo[node].rev()
    tip_rev = repo['tip'].rev()

    ui.pushbuffer()
    for rev in range(tip_rev, node_rev-1, -1):
        displayer.show(repo[rev])
    revs = ui.popbuffer()

    t = templater(None)
    t.cache['default'] = template
    message = stringify(t('default', root=root, user=user, changesets=revs))
    
    password_manager = urllib2.HTTPPasswordMgr()
    password_manager.add_password('Application', campfire_url, api_key, 'X')

    handler = urllib2.HTTPBasicAuthHandler(password_manager)

    opener = urllib2.build_opener(handler)

    target_url = join(campfire_url, 'room', campfire_room, 'speak.xml')

    req = urllib2.Request(target_url,
                          "<message><body>%s</body></message>" % cgi.escape(message))
    req.add_header('Content-Type', 'application/xml')

    # Python < 2.6 raises HTTPError on a 201 status code
    try:
        response = opener.open(req)
    except urllib2.HTTPError, e:
        if not (200 <= e.code < 300):
            raise

