'''
Use this command to relase
'''

#live or staging?

import os
import sys
import subprocess
import urllib2

if __name__ == '__main__':
    
    if len(sys.argv) < 3:
            print 'usage: %s <ReleaseVersion> <staging|live|pypi>' % sys.argv[0]
            sys.exit(1)
            
    version = sys.argv[1]
    server = sys.argv[2]
    
    if server == 'pypi':
        #handle pypi releasing
        try:
            os.unlink('src')
        except:
            pass
        try:
            os.unlink(os.path.expanduser('~/.pypirc'))
        except:
            pass
        
        
        os.symlink('../client', 'src')
        
        os.symlink(os.path.expanduser('~/.pypirc26'),os.path.expanduser('~/.pypirc'))
        p = subprocess.Popen('python2.6 setup.py sdist bdist_egg upload', shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        stdout, stderr = p.communicate(input=False)
        if stderr:
            print 'python2.6 package stderr \n' + stderr
        if stdout:
            print'uploaded python2.6 package! \n' + stdout
        
        os.unlink(os.path.expanduser('~/.pypirc'))
        os.symlink(os.path.expanduser('~/.pypirc25'),os.path.expanduser('~/.pypirc'))
        p = subprocess.Popen('python2.5 setup.py bdist_egg upload', shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        stdout, stderr = p.communicate(input=False)
        if stderr:
            print 'python2.5 package stderr \n' + stderr
        if stdout:
            print'uploaded python2.5 package! \n' + stdout
        
        os.unlink('src')
        sys.exit(0)
    
    
    if server not in ['staging', 'live']:
        print 'server must be staging or live'
        sys.exit(1)
    
    import autotagger.local_settings as local_settings
    local_settings.isTestApp = (lambda: True) if server == 'staging' else (lambda: False)
    
    #print 'hmm', local_settings.isTestApp()
    print local_settings.getTakeYourOrderDBInfo()
    
    from autotagger.cloud.server.models import ClientDistribution
    from autotagger.cloud.server.db import tyodb
    
    import autotagger.utils.remote as remote
    
    
    distdir = 'dist'
    files = os.listdir(distdir)
    
    platforms = ['win', 'unix']
    py_versions = ['2.5', '2.6', '2.7']
    
    prefix = 'cloud-' + version
    
    upload_files = []
    
    #source first:    
    srcfile = prefix + '.tar.gz'
    if srcfile not in files:
        print 'missing source distribution %s' % srcfile
        sys.exit(1)
    upload_files.append(srcfile)
        
    distributions = []
    for py_version in py_versions:
        for platform in platforms:        
            distributions.append(ClientDistribution(version=version,py_version=py_version,
                                                    py_platform=platform, dist_type='src',filename=version+'/'+srcfile))
    
    #Now Egg:
    for py_version in py_versions:
        eggfile = prefix + '-py' + py_version + '.egg'
        if eggfile not in files:
            print 'missing egg distribution %s' % eggfile       
            sys.exit(1)  
        upload_files.append(eggfile)            
        for platform in platforms:        
            distributions.append(ClientDistribution(version=version,py_version=py_version,
                                                    py_platform=platform, dist_type='egg',filename=version+'/'+eggfile))
    

    tyodb.client_distributions.add(distributions, replace_duplicates=True)
    
    if server == 'staging':
        webservers = ['staging.picloud.net']
        #upload_dir = '/var/media/cloudweb/downloads/cloud/' + version
    else:
        from autotagger.cloud.server.admin import servermgr
        
        all_servers = servermgr.describe_instances()
        webservers = [server.public_dns_name for server in all_servers \
                      if ('webserver' in server.groups and server.public_dns_name)] 
        #webservers = ['phi.picloud.net']
        
    #we symlink to this:
    upload_dir = '/root/cloud_download/' + version
    
    #old webserver via cloudinfo. This fails as we can't use 
    #webserver = urllib2.httplib.urlsplit(local_settings.getCloudInfo()['server_url']).netloc
    ec2team = '%sadmin/aws/keys/ec2_team.pem' % local_settings.getResourceDirectory()
    
        
    #print 'start', webserver
    for webserver in webservers:
        print 'uploading cloud to %s' % webserver
    
        remote.broadcast('mkdir -p %s'%(upload_dir) , 'root', webserver, ec2team)
        #print 'done'    
        remote.broadcast('chown www-data:www-data %s'%(upload_dir) , 'root', webserver, ec2team)
      
      
        for file in upload_files:
            src_file = distdir + '/' + file
            dst_file = upload_dir + '/' + file
          
            remote.scp(src_file, dst_file, 'root', webserver, ec2team)
            remote.broadcast('chown www-data:www-data %s' % dst_file, 'root', webserver, ec2team)
           
