import os
import time
import base64
from zope.testbrowser.browser import Browser
from urllib2 import HTTPError
import subprocess

RETRIES = 1
METH_ID = 'meth_collective_migrator'

Browsers = {}


def get_zmi(instance):
    zmi = instance.get('zmi', None)
    if zmi:
        return 'http://%s' % zmi
    else:
        return 'http://%(host)s:%(port)s/%(root)s' % instance

def import_one(instance, obj, br):
    zmi = get_zmi(instance)
    pos = obj.rfind('/')
    if pos == -1:
        url = '%s/manage_importObject?file=%s.zexp&set_owner:int=0'% (zmi, obj)
    else:
        top_obj = obj[:pos]
        obj = obj[pos+1:]
        url = '%s/%s/manage_importObject?file=%s.zexp&set_owner:int=0'% (zmi, top_obj, obj)

    try:
        br.open(url)
    except HTTPError:
        return 0
    s1 = br.contents
    success = s1.find('successfully imported') != -1
    if success:
        import_file = '%s/%s.zexp' % (instance['import'], obj)
        if instance['host'] == 'localhost':
            os.remove(import_file)
        else:
            cmd = 'ssh %s@%s rm -f %s' % (instance['user'], instance['host'], import_file)
            os.system(cmd)
    return success

def export_one(instance, obj, br):
    zmi = get_zmi(instance)
    export_folder = instance['export']
    pos = obj.rfind('/')
    if pos == -1:
        url = '%s/manage_exportObject?id=%s&download:int=0&submit=Export'% (zmi, obj)
    else:
        top_obj = obj[:pos]
        obj = obj[pos+1:]
        url = '%s/%s/manage_exportObject?id=%s&download:int=0&submit=Export'% (zmi, top_obj, obj)

    export_file = '%s/%s.zexp' % (export_folder, obj)

    cmd = 'rm -f %s' % export_file
    if host_name != 'localhost':
        cmd = 'ssh %s@%s %s' % (instance['user'], host_name, cmd)
    os.system(cmd)

    try:
        f1 = br.open(url)
    except HTTPError:
        return -1
    else:
        s1 = br.contents
        str1 = "successfully exported"
        return s1.find(str1) >= 0

def create_dir(source, source_dir):
    cmd = ['mkdir', source_dir]
    if source['host'] != 'localhost':
        cmd = ['ssh', '%s@%s' % (source['user'], source['host'])] + cmd 
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]
    cmd = ['ls', '-d', source_dir]
    if source['host'] != 'localhost':
        cmd = ['ssh', '%s@%s' % (source['user'], source['host'])] + cmd 
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0].strip()
    return output == source_dir

def copy_file(source, source_dir, file_name, target, target_dir, keep=False):
    if source['host'] == 'localhost' or source['host'] == target['host']:
        source_file = '%s/%s' % (source_dir, file_name)
    else:
        source_file = '%s@%s:%s/%s' % (source['user'], source['host'], source_dir, file_name)
    if target['host'] == 'localhost' or source['host'] == target['host']:
        target_file = target_dir
    else:
        target_file = '%s@%s:%s' % (target['user'], target['host'], target_dir)
    pos1 = source_file.find(':')
    pos2 = target_file.find(':')
    if pos1 == -1 and pos2 == -1:
        cmd = "cp %s %s" % (source_file, target_file)
    else:
        cmd = "scp %s %s" % (source_file, target_file)
    os.system(cmd)
    target_file = '%s/%s' % (target_dir, file_name)
    cmd = ['ls', target_file]
    if target['host'] != 'localhost':
        cmd = ['ssh', '%s@%s' % (target['user'], target['host'])] + cmd 
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0].strip()
    if output != target_file:
        return -1
    if not keep:
        cmd = 'rm -f %s/%s' % (source_dir, file_name)
        if source['host'] != 'localhost':
            cmd = 'ssh %s@%s %s' % (source['user'], source['host'], cmd)
        os.system(cmd)
    return 0

def get_browser(instance):
    host_name, host_port = (instance['host'], instance['port'])
    key = '%s:%s' % (host_name, host_port)
    if key not in Browsers:
        br = Browser()
        if instance.get('zmi_user', None):
            zmi_user, zmi_pwd = (instance['zmi_user'], instance['zmi_pwd'])
            br.addHeader('Authorization', 'Basic %s' % base64.encodestring('%s:%s' % (zmi_user, zmi_pwd)))
        Browsers[key] = br
    return Browsers[key]
    

def create_ext_method(instance, module, function, br):
    zmi = get_zmi(instance)
    del_object(instance, METH_ID, br)
    url = '%s/manage_addProduct/ExternalMethod/manage_addExternalMethod' % zmi
    try:
        br.post(url, 'id=%s&module=%s&function=%s&title=collective_migrator' % (METH_ID, module, function))
    except HTTPError:
        return dump_error_log(instance)
    return ''

def run_ext_method(instance, args, out_file, br):
    zmi = get_zmi(instance)
    url = '%s/%s' % (zmi, METH_ID)
    if args:
        url_add = []
        for k,v in args.items():
            url_add.append('%s=%s' % (k, v))
        url_add = '&'.join(url_add)
        url = url + '?' + url_add
    try:
        br.open(url)
    except HTTPError:
        return dump_error_log(instance)
    fp = open(out_file, "a")
    fp.write('--- %s\n' % time.asctime())
    fp.write(br.contents)
    fp.close()
    return ''

def dump_error_log(instance):
    cmd = 'sed -n -e "/^---*/{h;d;}" -e H -e "\${g;p;}" %s' % instance['log']
    if instance['host'] != 'localhost':
        cmd = "ssh %s@%s '%s'" % (instance['user'], instance['host'], cmd)
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0]
    return output

def del_object(instance, obj, br):
    zmi = get_zmi(instance)
    pos = obj.rfind('/')
    if pos == -1:
        url = '%s/manage_delObjects?ids=%s' % (zmi, obj)
    else:
        top_obj = obj[:pos]
        obj = obj[pos+1:]
        url = '%s/%s/manage_delObjects?ids=%s' % (zmi, top_obj, obj)
    try:
        br.open(url)
    except HTTPError:
        pass

def submit_url(instance, url, args, out_file, br):
    zmi = get_zmi(instance)
    url = '%s/%s' % (zmi, url)
    br.open(url)
    if 'form_index' in args:
        br = br.getForm(index=int(args['form_index']))
    for k in args:
        if k in ('submit', 'form_index') :
            continue
        br.getControl(name=k).value = args[k]
    if 'submit' in args:
        br.getControl(name=args['submit']).click()
    elif 'form_index' in args:
        br.submit()
    else:
        br.getForm().submit()
    fp = open(out_file, "a")
    fp.write(br.contents)
    fp.close()
