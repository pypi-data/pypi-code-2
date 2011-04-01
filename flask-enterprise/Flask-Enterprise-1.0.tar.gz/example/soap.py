from time import ctime
from flask import Flask
from flaskext.enterprise import Enterprise


app = Flask(__name__)
enterprise = Enterprise(app)


class DemoService(enterprise.SOAPService):

    @enterprise.rpc(_returns=enterprise._sp.String)
    def get_time(self):
        return ctime()


if __name__ == '__main__':
    app.run()
