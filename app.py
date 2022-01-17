import datetime
import socket
import sys
import pickle

from flask import Flask, render_template, request

socket_location = './uds_socket'
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
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

        return render_template('submit.html')


def send_data(data):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(socket_location)
        print(f'[INFO] Verbonden met socket op {socket_location}')
        s.sendall(data)
        print('Data verzonden')


if __name__ == '__main__':
    app.run()
