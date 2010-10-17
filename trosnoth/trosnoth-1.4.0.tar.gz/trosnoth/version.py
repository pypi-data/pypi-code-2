version = '1.4.0'
release = True
revision = 'dev'

if release:
    fullVersion = '%s' % (version,)
else:
    fullVersion = '%s-%s' % (version, revision)
    
titleVersion = 'Version %s' % (fullVersion,)
