version = '1.4.1'
release = True
revision = 'dev'

if release:
    fullVersion = '%s' % (version,)
else:
    fullVersion = '%s-%s' % (version, revision)
    
titleVersion = 'Version %s' % (fullVersion,)
