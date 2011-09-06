#!/usr/bin/env python
import os, sys, tempfile, mercurial, traceback
from amqpdeliver import send
from mercurial import commands, hg
from optparse import OptionParser

CONFIG_SECTION = "amqp-deliver"
GPG_SECTION = "amqp-gpg"

DEFAULT_SERVER = send.DEFAULT_SERVER
DEFAULT_USERID = send.DEFAULT_USERID
DEFAULT_PASSWORD = send.DEFAULT_PASSWORD
DEFAULT_VIRTUAL_HOST = send.DEFAULT_VIRTUAL_HOST

def tmp_bundle(exchange):
    return tempfile.mkstemp(suffix='.hg', prefix='%s-'%(exchange))

# Use this in your .hgrc to send bundles as the repository is changed
def send_bundle(ui, repo, node, **kwargs):
    try:
        send_bundle1(ui, repo, node)
    except Exception, err:
        traceback.print_exc()
        ui.status('ERROR: %s\n' % str(err))
        raise err

def send_bundle1(ui, repo, node):
    server = ui.config(
        CONFIG_SECTION, 
        'server', 
        default=DEFAULT_SERVER)
    exchange = ui.config(CONFIG_SECTION, 'exchange')
    userid = ui.config(
        CONFIG_SECTION, 
        'userid', 
        default=DEFAULT_USERID)
    password = ui.config(
        CONFIG_SECTION, 
        'userid', 
        default=DEFAULT_PASSWORD)
    virtual_host = ui.config(
        CONFIG_SECTION, 
        'virtual-host', 
        default=DEFAULT_VIRTUAL_HOST)

    sign = ui.configbool(GPG_SECTION, 'sign')
    encrypt = ui.configbool(GPG_SECTION, 'encrypt')

    ui.status("Sending bundle to %s\n" % exchange);

    bundle_file_fd, bundle_file = tmp_bundle(exchange)
    os.close(bundle_file_fd)

    # We specify the destination, and mercurial keeps track of what it has, and
    # hasn't sent to that destination for us, which is handy
    base_files_dir = "%s/amqp-deliver" % repo.path
    base_file = "%s/%s.base" % (base_files_dir, exchange)

    if os.path.exists(base_file):
        base_node = open(base_file).read()
        ui.status("base = %s\n" % base_node)
        commands.bundle(ui, repo, bundle_file, base = [base_node])
    else:
        commands.bundle(ui, repo, bundle_file, all = True)

    if sign or encrypt:
        options = [ 'gpg' ]
        if sign:
            localuser = ui.config(GPG_SECTION, 'local-user', ui.username())
            options += ['--sign', '--local-user', '"%s"' % localuser]
        if encrypt:
            recipient = ui.config(GPG_SECTION, 'recipient', exchange)
            options += ['--encrypt', '--recipient', '"%s"' % recipient]
        ui.status('%s\n' % ' '.join(options))
        (stdin, stdout) = os.popen2(' '.join(options), 'b')
        stdin.write(open(bundle_file, 'rb').read())
        stdin.close()
        body = stdout.read()
        stdout.close()
    else:
        body = open(bundle_file, 'rb').read()

    send.send(
        server = server,
        exchange = exchange,
        body = body,
        userid = ui.config(
            CONFIG_SECTION, 
            'userid', 
            default=DEFAULT_USERID),
        password = ui.config(
            CONFIG_SECTION, 
            'userid', 
            default=DEFAULT_PASSWORD),
        virtual_host = ui.config(
            CONFIG_SECTION, 
            'virtual-host', 
            default=DEFAULT_VIRTUAL_HOST),
        message_id = node)

    if not(os.path.isdir(base_files_dir)):
        os.mkdir(base_files_dir)
    base_out = open(base_file, 'w')
    base_out.write(str(node))
    base_out.close()
    ui.status("Sent bundle %s to %s\n" % (bundle_file, exchange))


# The main is intended to be launched by receive_d, to apply
# changes to the local repository
def main(args=None):

    parser = OptionParser(
        usage="usage: %prog [options] repository")
    
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("Two few arguments")
        return 1

    repository = args[0]

    repo = hg.repository(mercurial.ui.ui(), repository)
    body = sys.stdin.read()
    exchange = os.environ['AMQP_EXCHANGE']
    unbundle(repo.ui, repo, body, exchange)
    return 0

def unbundle(ui, repo, body, exchange):

    bundle_file_fd, bundle_file = tmp_bundle(exchange)

    decrypt = ui.configbool(GPG_SECTION, 'decrypt')
    verify = ui.configbool(GPG_SECTION, 'verify')

    if decrypt or verify:
        os.close(bundle_file_fd)
        options = [ 'gpg' ]
        if decrypt:
            localuser = ui.config(GPG_SECTION, 'local-user', ui.username())
            options += ['--decrypt', '--local-user', '"%s"' % localuser]
        options += [ '--output', bundle_file]
        
        bundle_out = os.popen(' '.join(options), 'wb')
    else:
        bundle_out = os.fdopen(bundle_file_fd, 'wb')
    bundle_out.write(body)
    bundle_out.close()
    
    commands.unbundle(ui, repo, bundle_file)
    

if __name__ == "__main__":
    sys.exit(main())

