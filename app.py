import datetime
import socket
import pickle
import shutil
import database
import json
import subprocess

from flask import Flask, render_template, request

SOCKET_LOCATION = '/tmp/uds_socket'
DATABASE = './database.db'

app = Flask(__name__)
app.jinja_env.globals.update(zip=zip)


@app.route("/", methods=['POST', 'GET'])
def index():
    db = database.Database(DATABASE)

    if request.method == 'POST':
        if 'delete_row' in request.form:
            d = json.loads(request.form['delete_row'])
            print(d)
            db.delete_row(d)
            d['start_datetime'] = [datetime.datetime.fromisoformat(d['start_datetime'])]
            d['end_datetime'] = [datetime.datetime.fromisoformat(d['end_datetime'])]
            delete_data(d)
        elif 'debug' in request.form:
            ask_debug()

    db.remove_old_rows()

    total, used, free = shutil.disk_usage('/')
    disk_used = '{:.2f}'.format(used / (10 ** 9))
    disk_total = '{:.2f}'.format(total / (10 ** 9))

    planned_tasks = db.get_rows()

    return render_template('index.html',
                           pct=int(used/total*100), disk_used=disk_used, disk_total=disk_total,
                           planned_tasks=planned_tasks)


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'GET':
        return index()

    fields = ('name', 'latitude', 'longitude', 'zoom', 'start_datetime[]', 'end_datetime[]', 'interval')
    errors = []
    for field in fields:
        app.logger.info(f'{request.form[field] =} {type(request.form.get(field))}')
        if not request.form[field]:
            errors.append(f'{field} is niet doorgegeven!')

    name = request.form['name']
    zoom = float(request.form['zoom'])
    start_datetime = [datetime.datetime.fromisoformat(item) for item in request.form.getlist('start_datetime[]')]
    end_datetime = [datetime.datetime.fromisoformat(item) for item in request.form.getlist('end_datetime[]')]
    try:
        lat = float(request.form['latitude'])
        long = float(request.form['longitude'])
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
    print(f'{data_dict=}')
    try:
        add_data(data_dict)
    except Exception as e:
        return render_template(
            'error.html',
            info_text='Probleem bij het verbinden met de taak-server',
            error=repr(e))

    datetimes = [(start, end) for start, end in zip(data_dict['start_datetime'], data_dict['end_datetime'])]
    return render_template('submit.html', data_dict=data_dict, datetimes=datetimes)

@app.route('/shutdown', methods=['GET'])
def shutdown():
    p = subprocess.run(['sudo', 'shutdown', '-h', 'now'], capture_output=True)
    print(p.stdout, p.stderr)
    return p.stdout


def _send_data(data):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(SOCKET_LOCATION)
        print(f'[INFO] Verbonden met socket op {SOCKET_LOCATION}')
        s.sendall(data)
        print('Data verzonden')

def add_data(data):
    _send_data(pickle.dumps({'CREATE': data}))

def delete_data(data):
    _send_data(pickle.dumps({'DELETE': data}))

def ask_debug():
    _send_data(pickle.dumps({'DEBUG': True}))
