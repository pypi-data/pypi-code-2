import bottle
import controller
import sys

app = bottle.default_app()

if __name__ == '__main__':
    from bottle import run
    port = 8000
    if len(sys.argv) > 1:
        port = sys.argv[1]
    run(host='localhost', port=port)

