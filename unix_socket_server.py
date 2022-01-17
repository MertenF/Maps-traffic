#!/usr/bin/env python

import threading
import socket
import os
import pickle
from pathlib import Path

import maps_traffic
import screenshotscheduler

socket_location = './uds_socket'

scheduler = screenshotscheduler.ScreenshotScheduler(maps_traffic.get_screenshots_now)

# Make sure the socket does not already exist
try:
    os.unlink(socket_location)
except OSError:
    if os.path.exists(socket_location):
        raise

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
    print(f'[Info] Starting server up on {socket_location}')
    sock.bind(socket_location)
    sock.listen(1)
    while True:
        # Wait for connection
        connection, client_address = sock.accept()
        with connection:
            while True:
                data = connection.recv(1024)
                if data:
                    data_dict = pickle.loads(data)
                    name, url, execute_times = maps_traffic.import_from_flask(**data_dict)
                    scheduler.add_task_same_name(name, url, execute_times, Path('/home/pi/screenshots_output'))

                    if not scheduler.running():
                        print('[INFO] Scheduler was not running, starting thread')
                        threading.Thread(target=scheduler.run).start()
                else:
                    break
