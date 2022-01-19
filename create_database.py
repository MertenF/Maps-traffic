#!/usr/bin/env python3

import sqlite3
from contextlib import closing

DATABASE = './database.db'

print('Creating database')

with closing(sqlite3.connect(DATABASE)) as conn:
    with closing(conn.cursor()) as cur:
        cur.execute("""CREATE TABLE planned_tasks (
                        name VARCHAR,
                        latitude FLOAT,
                        longitude FLOAT,
                        zoom FLOAT,
                        interval INT,
                        start_datetime DATETIME,
                        end_datetime DATETIME)""")
    conn.commtit()

