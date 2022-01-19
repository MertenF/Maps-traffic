#!/usr/bin/env python

import threading
import socket
import os
import pickle
from pathlib import Path
import sqlite3
from contextlib import closing
from typing import Dict
import datetime

import maps_traffic
import screenshotscheduler

SOCKET_LOCATION = '/tmp/uds_socket'
SCREENSHOT_PATH = Path.home() / 'screenshots_output'
DATABASE = './database.db'


def main():
    with closing(sqlite3.connect(DATABASE)) as conn:
        conn.row_factory = sqlite3.Row
        main_loop(conn)


def main_loop(db_conn):
    scheduler = screenshotscheduler.ScreenshotScheduler(maps_traffic.get_screenshots_now)

    # plan things in database
    for row in load(db_conn):
        plan(scheduler, row)

    # Make sure the socket does not already exist
    try:
        os.unlink(SOCKET_LOCATION)
    except OSError:
        if os.path.exists(SOCKET_LOCATION):
            raise

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        print(f'[Info] Starting server up on {SOCKET_LOCATION}')
        sock.bind(SOCKET_LOCATION)
        sock.listen(1)
        while True:
            # Wait for connection
            connection, client_address = sock.accept()
            with connection:
                while True:
                    data = connection.recv(1024)
                    if data:
                        data_dict = pickle.loads(data)
                        store(db_conn, **data_dict)
                        plan(scheduler, data_dict)

                    else:
                        break


def load(db_conn):
    """Load all the data from the database"""

    with closing(db_conn.cursor()) as cur:
        database_rows = [row for row in cur.execute('SELECT * from planned_tasks')]

    for row in database_rows:
        d_row = dict(row)
        d_row['start_datetime'] = [datetime.datetime.fromisoformat(d_row['start_datetime'])]
        d_row['end_datetime'] = [datetime.datetime.fromisoformat(d_row['end_datetime'])]
        yield d_row


def store(db_conn, **kwargs):
    """Store new data in the database"""

    with closing(db_conn.cursor()) as cur:
        for start_datetime, end_datetime in zip(kwargs['start_datetime'], kwargs['end_datetime']):
            cur.execute("""INSERT INTO planned_tasks VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (kwargs['name'],
                         kwargs['latitude'],
                         kwargs['longitude'],
                         kwargs['zoom'],
                         kwargs['interval'],
                         start_datetime,
                         end_datetime))
        db_conn.commit()


def plan(scheduler, data_dict: Dict):
    print(f'plan = {data_dict}')
    name, url, execute_times = maps_traffic.import_from_flask(**data_dict)
    scheduler.add_task_same_name(name, url, execute_times, SCREENSHOT_PATH)

    if not scheduler.running():
        print('[INFO] Scheduler was not running, starting thread')
        threading.Thread(target=scheduler.run).start()


if __name__ == '__main__':
    main()
