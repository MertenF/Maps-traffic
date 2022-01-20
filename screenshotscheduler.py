import pathlib
import sched
import time
import datetime
from pathlib import Path
from typing import Dict, List, Callable


class ScreenshotScheduler:
    def __init__(self, action_funtion: Callable[[Dict, pathlib.Path, int, int], None]):
        self.plan = sched.scheduler(time.time, time.sleep)
        self.action = action_funtion
        self.queue = []
        self._running = False

    def add_tasks(self, name: str, url: str, execute_times: List[datetime.datetime], screenshot_folder: Path):
        for execute_time in execute_times:
            if execute_time > datetime.datetime.now():
                self._add_task({name: url}, execute_time, screenshot_folder)

    def _add_task(self, locations: Dict, execute_time: datetime.datetime, save_path: Path):
        self.plan.enterabs(
            time=execute_time.timestamp(),
            priority=1,
            action=self.action,
            argument=(locations, save_path),
        )

    def running(self) -> bool:
        """Check whether the scheduler is running"""
        return self._running

    def run(self):
        if not self.plan.empty():
            if not self._running:
                print('[INFO]: Starting the scheduler!')
                self._running = True
                self.plan.run()
                self._running = False
                print('[INFO] Scheduler is done running')
            else:
                print('[WARNING] Scheduler already running!')
        else:
            print('[WARNING] No tasks planning, cannot run')

    def get_queue(self):
        self.queue = self.plan.queue  # buffer

    def _delete_task(self, timestamp, locations, save_path):
        for task in self.queue:
            if task.time == timestamp and task.argument == (locations, save_path):
                self.plan.cancel(task)

    def delete_tasks(self, name: str, url: str, execute_times: List[datetime.datetime], screenshot_folder: Path):
        """Looks in the queue and deletes all task that are matchin"""
        self.get_queue()  # buffer, reading from it is blocking

        for execute_time in execute_times:
            self._delete_task(execute_time.timestamp(), {name: url}, screenshot_folder)


