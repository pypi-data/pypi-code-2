from turbojson.jsonify import jsonify
from sqlalchemy.orm.query import Query

jsonify.when((Query,))(lambda obj: obj.all())
