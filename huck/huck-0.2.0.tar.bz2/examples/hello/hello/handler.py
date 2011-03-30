from hello import web

class Home(web.Handler):

    def get(self, path=''):
        if not path:
            content = 'We are home'
        else:
            content = 'We are at /%s' % path
        self.render('base.html', title='Hello World', content=content)

route = [
    (r'/(.*)', Home),
]
