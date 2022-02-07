import sqlite3
import datetime
from typing import List, Dict


class Database:
    def __init__(self, db_location: str):
        self.connection = sqlite3.connect(db_location)
        self.connection.row_factory = sqlite3.Row  # return row as dict
        self._create()

    def _create(self):
        with self.connection as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS planned_tasks (
                            name VARCHAR,
                            latitude FLOAT,
                            longitude FLOAT,
                            zoom FLOAT,
                            interval INT,
                            start_datetime DATETIME,
                            end_datetime DATETIME)""")

    def delete_row(self, row: Dict):
        """Delete a row"""
        if type(row['start_datetime']) == List:
            row['start_datetime'] = row['start_datetime'][0]
            row['end_datetime'] = row['end_datetime'][0]

        print(f'{row = }')
        with self.connection as conn:
            conn.execute("""DELETE FROM planned_tasks WHERE (
                            name = :name AND
                            latitude = :latitude AND
                            longitude = :longitude AND
                            zoom = :zoom AND
                            interval = :interval AND
                            start_datetime = :start_datetime AND
                            end_datetime = :end_datetime)""",
                         row
                         )

    def get_rows(self):
        """Returns raw list with rows as dicts"""
        with self.connection as conn:
            rows = [dict(row) for row in conn.execute('SELECT * from planned_tasks')]

        return rows

    def get_rows_generator(self):
        """Load all the data from the database"""

        # Change datetime string to datetime object in a list
        for row in self.get_rows():
            row['start_datetime'] = [datetime.datetime.fromisoformat(row['start_datetime'])]
            row['end_datetime'] = [datetime.datetime.fromisoformat(row['end_datetime'])]
            yield row

    def store(self, **kwargs):
        """Store new data in the database"""
        with self.connection as conn:
            for start_datetime, end_datetime in zip(kwargs['start_datetime'], kwargs['end_datetime']):
                conn.execute("""INSERT INTO planned_tasks VALUES (?, ?, ?, ?, ?, ?, ?)""",
                            (kwargs['name'],
                             kwargs['latitude'],
                             kwargs['longitude'],
                             kwargs['zoom'],
                             kwargs['interval'],
                             start_datetime,
                             end_datetime)
                             )

    def remove_old_rows(self):
        """Remove all rows where end time is in the past"""
        with self.connection as conn:
            conn.execute("""DELETE FROM planned_tasks WHERE end_datetime < DATETIME('NOW', 'LOCALTIME')""")

