from flask import Flask, jsonify
from redis import Redis

app = Flask(__name__)
db = Redis(db='beans')

@app.route('/incr/<key>/<member>/')
def incr(key, member):
    return jsonify(count = db.zincrby(key, member))

@app.route('/count/<key>/<member>/')
def count(key, member):
    return jsonify(count = db.zscore(key, member))

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
