import datetime
import socket
import pickle
import shutil

from flask import Flask, render_template, request

SOCKET_LOCATION = '/tmp/uds_socket'


app = Flask(__name__)


@app.route("/")
def index():
    total, used, free = shutil.disk_usage('/')
    disk_used = '{:.2f}'.format(used / (10 ** 9))
    disk_total = '{:.2f}'.format(total / (10 ** 9))
    return render_template('index.html', pct=int(used/total*100), disk_used=disk_used, disk_total=disk_total)


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'GET':
        return index()

    app.logger.info(request.form)
    fields = ('name', 'latitude', 'longitude', 'zoom', 'start_datetime', 'end_datetime', 'interval')
    errors = []
    for field in fields:
        app.logger.info(f'{request.form[field] =} {type(request.form.get(field))}')
        if not request.form[field]:
            errors.append(f'{field} is niet doorgegeven!')

    name = request.form['name']
    try:
        lat = float(request.form['latitude'])
        long = float(request.form['longitude'])
        zoom = float(request.form['zoom'])
        start_datetime = datetime.datetime.fromisoformat(request.form['start_datetime'])
        end_datetime = datetime.datetime.fromisoformat(request.form['end_datetime'])
        interval = int(request.form['interval'])
    except ValueError as e:
        return render_template(
            'error.html',
            info_text='Gegevens zijn niet juist ingevoerd, er was een fout bij de omzetting. Heb je een comma gebruikt in plaats van een punt?',
            error=str(e))

    data_dict = {
        'name': name,
        'latitude': lat,
        'longitude': long,
        'zoom': zoom,
        'start_datetime': start_datetime,
        'end_datetime': end_datetime,
        'interval': interval
    }
    try:
        send_data(pickle.dumps(data_dict))
    except Exception as e:
        return render_template(
            'error.html',
            info_text='Probleem bij het verbinden met de taak-server',
            error=repr(e))

    return render_template('submit.html', data_dict=data_dict)


def send_data(data):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(SOCKET_LOCATION)
        print(f'[INFO] Verbonden met socket op {SOCKET_LOCATION}')
        s.sendall(data)
        print('Data verzonden')
