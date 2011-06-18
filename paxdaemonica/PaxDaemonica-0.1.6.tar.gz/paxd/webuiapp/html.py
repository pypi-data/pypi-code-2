import os
from StringIO import StringIO

def header():
    return u'''
<html>
<head>
<title>Pax Daemonica</title>
    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js"></script>
    %s
    %s
</head>
<body>
    ''' % (styles(), js())

def footer():
    return '''
    </body>
    </html>
    
    '''

def applications(apps):
    ret = u'''<table>'''
    ret += app_header()
    for app in apps:
        ret += application(app)
    return ret + u'</table>'

def app_header():
    return u'''<tr>
        <th>Q       </th>
        <th>Q:a     </th>
        <th>Q:f     </th>
        <th>Q:s     </th>
        <th>controls</th>
        <th>status  </th>
        <th>queue   </th>
        <th>name    </th>
        <th>entry   </th>
        <th>path    </th>
        <th>id      </th>
        </tr>
    '''

def application(app):
    id_query = u'?id=' + app['id']
    unstoppable = ''
    if app['unstoppable']:
        unstoppable = 'unstoppable'
    q = app.get('queued')
    qa = app.get('active')
    qf = app.get('failed')
    qs = app.get('success')
    return u'''
        <tr class="{unstoppable}">
            <td class="path">{q}</td>
            <td class="path">{qa}</td>
            <td class="path">
                <a class="failed" href="/failed{id_query}">{qf}</a>
            </td>
            <td class="path">{qs}</td>
            <td class="actions">
                <a class="action start" data-action="start" href="/unpause{id_query}">Start</a> |
                <a class="action stop" data-action="stop" href="/pause{id_query}">Stop</a> |
                <a class="action unload" data-action="unload" href="/unload{id_query}">Remove</a>
            </td>
            <td class="status">{app[status]}</td>
            <td class="queue">{app[queue]}</td>
            <td class="name">{app[name]}</td>
            <td class="entry">{app[entry]}</td>
            <td class="path">{app[path]}</td>
            <td class="id">{app[id]}</td>

        </tr>
    '''.format(**vars())

def failed(resp):
    app = resp['app']
    failed = resp['failed']
    s = StringIO()
    name = app['name']
    id = app['id']
    s.write(u'''
        <h2>{name} ({id})</h2>
        <table class="error">
    '''.format(**vars()))
    for f in failed:
        status = f['response']['status']
        time = f.get('time')
        type = f['response'].get('error_type')
        value = f['response'].get('error_value')
        traceback = f['response'].get('traceback')
        s.write(''' 
            <tr>
                <td>{status}</td>
                <td>{time}</td>
                <td>{type}</td>
                <td>{value}</td>
                <td><pre>{traceback}</pre></td>
            </tr>
        '''.format(**vars()))
    s.write('''
        </table>
    ''')
    return s.getvalue()

def load_file(name):
    file = os.path.join(os.path.dirname(__file__), name)
    with open(file) as f:
        return f.read()

def styles():
    return '''<style>%s</style>''' % load_file('webuiapp.css')

def js():
    return ''' <script>%s\n%s</script>''' % (load_file('json2.js'), load_file('webuiapp.js'))


