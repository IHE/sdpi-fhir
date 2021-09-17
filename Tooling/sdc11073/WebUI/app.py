import os

from logging import StreamHandler
from threading import Thread
from engineio.async_drivers import gevent
from flask import Flask, render_template, abort, request, send_from_directory
from flask_socketio import SocketIO

from Tests.TestLogger import setUpLogger, logger, formatter
from WebUI.tasks import discoveryTask, consumerTestTask

async_mode = None
if async_mode is None:
    try:
        from gevent import monkey
        async_mode = 'gevent'
    except ImportError:
        pass

if async_mode is None:
    async_mode = 'threading'


if async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


class WSHandler(StreamHandler):

    def emit(self, record):
        msg = self.format(record)
        with app.test_request_context('/'):
            socketio.emit('log', {'msg': msg}, broadcast=True)


@app.route('/reports/<path:path>')
def showReport(path):
    return send_from_directory('reports', path)


@app.route('/')
def main():
    return render_template('index.html')


@socketio.on('discover')
def handleMessage(_):
    app.logger.info("Received discover event")
    discoveryTask()


@app.route('/test', methods = ['POST'])
def executeTest():
    if request.method == 'POST':
        data = request.form
        if 'uuid' not in data or 'config' not in data or 'ca' not in data:
            abort(400)

        args = (data['uuid'], data['config'], data['ca'], socketio, os.path.join(app.root_path, "reports"))
        thread = Thread(target=consumerTestTask, args=args)
        thread.daemon = True
        thread.start()
        return "OK"
    else:
        abort(500)


if __name__ == '__main__':
    setUpLogger()
    wsHandler = WSHandler()
    wsHandler.setFormatter(formatter)
    logger.addHandler(wsHandler)
    socketio.run(app)
