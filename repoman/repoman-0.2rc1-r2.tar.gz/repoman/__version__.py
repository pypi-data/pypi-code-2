major = '0.2'
minor = ''
tag = 'rc1'
revision = '2'
version = major

if minor:
    version += '.' + minor
if tag:
    version += tag
if revision:
    version += '-r' + revision

