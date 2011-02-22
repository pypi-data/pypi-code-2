import yaml
from flask import Flask
from flaskext.genshi import Genshi

from nowsync import config

app = Flask(__name__, '/static')
app.nowsync_cfg = config.load_config()
app.config['DEBUG'] = app.nowsync_cfg.get('debug', False)
app.jinja_env.globals['nowsync_cfg'] = app.nowsync_cfg

genshi = Genshi(app)

def load_deps():
    """Load dependencies
    
    """
    from nowsync.views.frontend import frontend
    from nowsync.views.api import api
    app.register_module(frontend)
    app.register_module(api, url_prefix='/api')
    
if __name__ == '__main__':
    load_deps()
    app.run(debug=True, use_reloader=False)